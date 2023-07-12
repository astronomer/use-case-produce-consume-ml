Overview
========

This Astro project is an example of creating a simple ML pipeline with two DAGs in a producer/consumer relationship. One DAG extracts and loads housing data into a local S3FileSystem. A dataset is defined on the load task, and the updating of that dataset triggers a second consumer DAG. The second DAG then takes that data and uses it to train and run a predictive model. This set up has two main advantages. One is that two teams can work independently on their specific sections of the pipeline without needing to coordinate with each other outside of the initial set up. The second is that because the consumer DAG will only trigger once the data arrives, you can avoid the situation where the producer DAG takes longer than expected to complete and leads to the consumer DAG running on incomplete data.
  

  
Project Contents
================

  
- dags:  
    - astro_ml_producer: This DAG shows a simple producer pipeline that creates a clean feature engineer dataset for the astro_ml_consumer DAG to use for its model training and predictions.  
    - astro_ml_consumer: This DAG uses the dataset produced by the astro_ml_producer DAG to train a Scikit RidgeCV regression model, and then make predictions using that model. 
  
- Dockerfile: Environment variables for local development mode are stored in .env since they will be referenced by other docker containers (ie. minio).   When deploying to Astro cloud the environment variables in the Dockerfile should be updated to reference cloud storage.  
  
- Additional services:  
    - minio: To accomodate local development without relying on cloud storage this project includes a Minio instance for object storage in dev mode.  


Deploy Your Project Locally
===========================

1. 'astro dev init'  
2. 'astro dev start'  

This command will spin up 5 Docker containers on your machine, 3 for a the Airflow components:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI http://localhost:8080/
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- MLflow: http://localhost:5000
- Minio: http://localhost:9001
