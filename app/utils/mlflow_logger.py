# utils/mlflow_logger.py
import mlflow
import json
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def start_chat_run(user_input):
    try:
        # Set tracking URI here instead of at module level
        try:
            # Set active model:
            mlflow.set_active_model(name="AzureOpenAI")
            mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))

        except:
            pass  # Continue if tracking URI setup fails
            
        # Check if experiment exists and handle it properly
        experiment_name = os.environ.get("MLFLOW_EXPERIMENT_NAME")
        experiment = mlflow.get_experiment_by_name(experiment_name)
        
        if experiment is None:
            # Create experiment if it doesn't exist
            mlflow.create_experiment(experiment_name)
        elif experiment.lifecycle_stage == "deleted":
            # Restore if deleted using MLflow client
            client = mlflow.client.MlflowClient()
            client.restore_experiment(experiment.experiment_id)
            
        mlflow.set_experiment(experiment_name)
        mlflow.start_run(nested=True)
        mlflow.log_param("user_input", user_input)
    except Exception as e:
        print(f"Failed to start MLflow run: {e}")
        # Continue without MLflow if it fails

def log_router_response(message):
    try:
        mlflow.log_text(message, "router_response.json")
    except:
        pass

def log_table_retriever_response(message):
    try:
        mlflow.log_text(str(message), "table_retriever_response.txt")
    except:
        pass

def log_sql_code(sql_code):
    try:
        mlflow.log_text(sql_code, "generated_sql_code.txt")
    except:
        pass

def log_sql_results(results):
    try:
        mlflow.log_text(json.dumps(results, indent=2), "sql_results.json")
    except:
        pass

def log_generated_chart_results(results):
    try:
        mlflow.log_text(json.dumps(results, indent=2), "generated_chart_results.txt")
    except:
        pass

def log_sql_analysis_error(info):
    try:
        mlflow.log_text(json.dumps(info, indent=2), "sql_analysis_error.txt")
    except:
        pass

def log_required_tables(tables):
    try:
        mlflow.log_text(tables, "required_tables.txt")
    except:
        pass

def log_polish_prompt(info):
    try:
        mlflow.log_text(json.dumps(info, indent=2), "polish_prompt.txt")
    except:
        pass

def log_final_response(response):
    try:
        mlflow.log_text(response, "final_response.txt")
    except:
        pass

def end_chat_run():
    try:
        mlflow.end_run()
    except:
        pass