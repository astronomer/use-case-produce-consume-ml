from airflow.decorators import dag
from datetime import datetime 
from astro import sql as aql 
from astro.files import File 
from astro.dataframes.pandas import DataFrame
import os
from airflow import Dataset

dataset_uri = "built_features"


@dag(dag_id='astro_ml_producer', schedule_interval=None, start_date=datetime(2023, 1, 1), catchup=False)
def astro_ml_producer():
    data_bucket = 's3://data'
    models_bucket = 's3://models'

    model_id = datetime.utcnow().strftime("%y_%d_%m_%H_%M_%S_%f")
    model_dir = os.path.join(models_bucket, model_id)
    
    #Extract data from source system
    @aql.dataframe(task_id='extract')
    def extract_housing_data() -> DataFrame:
        from sklearn.datasets import fetch_california_housing
        return fetch_california_housing(download_if_missing=True, as_frame=True).frame
    
    #Build Features
    @aql.dataframe(task_id='featurize', outlets=Dataset(dataset_uri))
    def build_features(raw_df:DataFrame, model_dir:str) -> DataFrame:
        from sklearn.preprocessing import StandardScaler
        import pandas as pd
        from joblib import dump
        from s3fs import S3FileSystem

        fs = S3FileSystem(key='minioadmin', secret='minioadmin', client_kwargs={'endpoint_url': "http://host.docker.internal:9000/"})

        target = 'MedHouseVal'
        X = raw_df.drop(target, axis=1)
        y = raw_df[target]

        scaler = StandardScaler()
        X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
        metrics_df = pd.DataFrame(scaler.mean_, index=X.columns)[0].to_dict()

        #Save scalar for later monitoring and eval
        with fs.open(model_dir+'/scalar.joblib', 'wb') as f:
            dump([metrics_df, scaler], f)

        X[target]=y

        return X
    
    extract_df = extract_housing_data()
    loaded_data = aql.export_file(task_id='save_data_to_s3', 
                                     input_data=extract_df, 
                                     output_file=File(os.path.join(data_bucket, 'housing.csv')), 
                                     if_exists="replace")

    feature_df = build_features(extract_df, model_dir)
    
    
astro_ml_producer()