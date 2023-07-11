Overview
========

This Astro project is a "Hello World" example of a very simple machine learning workflow using Astro SDK.  It is intended to show the basic functionality and to demonstrate how a Data Scientist with basic python skills would be able to more simply build a DAG wihtout all the boilerplate code involved in many MLops pipelines.  
  
This project can also be used to highlight some areas where Astronomer might start looking at further reducing boilerplate code for integrations with open-source ML tools (ie. MLFlow, Feast, etc.).  
  
Project Contents
================

- include: This folder contains Jupyter Notebooks which would conceivably be the starting point for development.  In this workflow the user (Data Scientist) would start with exploratory analysis and experimentation in a notebook and then to build an enterprise-grade pipeline.  While some MLOps pipelines will treat the notebook itself as scheduled object for automation this approach has many limitations and introduces new challenges for maintainability, auditability and reproducibility.  
  
- dags:  
    - astro_ml: This DAG shows a very simple pipeline with Astro SDK where ML models are saved to object storage.  
    - astro_mlflow: This DAG shows the same workflow but using MLflow to track experiments and register models.  
  
- Dockerfile: Environment variables for local development mode are stored in .env since they will be referenced by other docker containers (ie. minio and mlflow).   When deploying to Astro cloud the environment variables in the Dockerfile should be updated to reference cloud storage and mlflow services running externally.  
  
- Additional services:  
    - mlflow: Many MLops platforms include a model catelog/registry for tracking models and experiments. This project includes an additional container for MLflow in local dev mode.  When deployed to Astro cloud this service would need to be provided by an external MLflow instance.  
    - minio: To accomodate local development without relying on cloud storage this project includes a Minio instance for object storage in dev mode.  


Deploy Your Project Locally
===========================

1. (optional) If planning to run the notebooks to simulate experimentation it is recommended to create a virtual environment and install packages locally (example: `conda env create -n astro_ml -f requirements.txt`)
2. 'astro dev init'  
3. 'astro dev start'  

This command will spin up 5 Docker containers on your machine, 3 for a the Airflow components:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI http://localhost:8080/
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- MLflow: http://localhost:5000
- Minio: http://localhost:9001