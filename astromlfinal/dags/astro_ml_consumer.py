from airflow.decorators import dag, task
from datetime import datetime 
from astro import sql as aql 
from astro.files import File 
from astro.dataframes.pandas import DataFrame
import os
from airflow import Dataset
from airflow.models.taskinstance import TaskInstance
from airflow.models.xcom import XCom
import pandas as pd


dataset_uri = "built_features"
ingestion_dataset = Dataset(dataset_uri)


@dag(dag_id='astro_ml_consumer', schedule=[Dataset(dataset_uri)], start_date=datetime(2023, 1, 1), catchup=False)
def astro_ml_consumer():
    data_bucket = 's3://data'
    models_bucket = 's3://models'

    model_id = datetime.utcnow().strftime("%y_%d_%m_%H_%M_%S_%f")
    model_dir = os.path.join(models_bucket, model_id)

    #Train a model
    @aql.dataframe(task_id='train')
    def train_model(feature_df:ingestion_dataset, model_dir:str) -> str:
        from sklearn.linear_model import RidgeCV
        import numpy as np
        from joblib import dump
        from s3fs import S3FileSystem

        fs = S3FileSystem(key='minioadmin', secret='minioadmin', client_kwargs={'endpoint_url': "http://host.docker.internal:9000/"})
        
        target = 'MedHouseVal'
        pandasfeature = fs.open("s3://local-xcom/wgizkzybxwtzqffq9oo56ubb5nk1pjjwmp06ehcv2cyij7vte315r9apha22xvfd7.parquet")
        cleanpanda = pd.read_parquet(pandasfeature)

        model = RidgeCV(alphas=np.logspace(-3, 1, num=30))

        reg = model.fit(cleanpanda.drop(target, axis=1), cleanpanda[target ])
        model_file_uri = model_dir+'/ridgecv.joblib'

        with fs.open(model_file_uri, 'wb') as f:
            dump(model, f) 

        return model_file_uri

    #Score data
    @aql.dataframe(task_id='predict')
    def predict_housing(feature_df:DataFrame, model_file_uri:str) -> DataFrame:
        from joblib import load
        from s3fs import S3FileSystem

        fs = S3FileSystem(key='minioadmin', secret='minioadmin', client_kwargs={'endpoint_url': "http://host.docker.internal:9000/"})
        with fs.open(model_file_uri, 'rb') as f:
            loaded_model = load(f) 
        featdf = fs.open("s3://local-xcom/wgizkzybxwtzqffq9oo56ubb5nk1pjjwmp06ehcv2cyij7vte315r9apha22xvfd7.parquet")
        cleandf = pd.read_parquet(featdf)

        target = 'MedHouseVal'

        cleandf['preds'] = loaded_model.predict(cleandf.drop(target, axis=1))
        print(cleandf)

        return cleandf
    
    model_file_uri = train_model(ingestion_dataset, model_dir)
    pred_df = predict_housing(ingestion_dataset, model_file_uri)

    pred_file = aql.export_file(task_id='save_predictions', 
                                     input_data=pred_df, 
                                     output_file=File(os.path.join(data_bucket, 'housing_pred.csv')),
                                     if_exists="replace")

astro_ml_consumer()