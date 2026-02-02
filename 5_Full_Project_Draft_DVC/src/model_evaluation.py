# IMPORTING LIBRARIES
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score ,precision_score ,recall_score,f1_score
from sklearn.model_selection import cross_val_score,cross_val_predict
import logging
import pickle
import os
import json
from sklearn.model_selection import StratifiedKFold
import yaml
from dvclive import Live



# LOGGING CONFIGURATION
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger("model_evaluation")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

log_file_path = os.path.join(log_dir, "model_evaluation.log")
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)




# Function to load Parameters 
def load_params(params_path:str) ->dict:
    '''Load Parameters from a YAML file'''
    try:
        with open(params_path,'r') as file:
            params=yaml.safe_load(file)
        logger.debug("Parameters retrived from %s",params_path)
        return params
    except FileNotFoundError:
        logger.error("File not found %s ",params_path)
        raise
    except yaml.YAMLError as e :
        logger.error("YAML Error %s",e)
        raise
    except Exception as e:
        logger.error("Unexpected Error %s ",e)
        raise



# Function to Load Model
def load_model():
    """
    Sirf 'models/model.pkl' file se trained ML model load karega.
    """
    try:
        model_path = os.path.join("models", "model.pkl")

        with open(model_path, 'rb') as file:
            model = pickle.load(file)

        logger.debug("Model Loaded Successfully from %s", model_path)
        return model

    except Exception as e:
        logger.error("Error Loading Model: %s", str(e))
        return None


# Function to Load data
def load_data() -> pd.DataFrame:
    df=pd.read_csv(r"Data\cleaned_train_test_data\test_data.csv")
    return df


# Function to Evaluate the  Model
def evaluate_model(model, X, y,n_split):
    """
    Evaluate the model using train-test evaluation + cross-validation metrics.
    """
    try:
        # Standard Predictions
        
        y_pred = model.predict(X)

        accuracy = accuracy_score(y, y_pred)
        precision = precision_score(y, y_pred, zero_division=0)
        recall = recall_score(y, y_pred, zero_division=0)
        f1 = f1_score(y, y_pred, zero_division=0)

        
        # Cross Validation (5-Fold)
       
        cv = StratifiedKFold(n_splits=n_split, shuffle=True, random_state=42)

        cv_accuracy = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
        cv_precision = cross_val_score(model, X, y, cv=cv, scoring='precision')
        cv_recall = cross_val_score(model, X, y, cv=cv, scoring='recall')
        cv_f1 = cross_val_score(model, X, y, cv=cv, scoring='f1')

        
        # Metrics Dictionary
        
        metrics_dict = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,

            "cv_accuracy_mean": cv_accuracy.mean(),
            "cv_precision_mean": cv_precision.mean(),
            "cv_recall_mean": cv_recall.mean(),
            "cv_f1_mean": cv_f1.mean()
        }

        logger.debug("Evaluation Completed. Metrics: %s", metrics_dict)
        return metrics_dict

    except Exception as e:
        logger.error("Error during model evaluation: %s", str(e))
        return None
    
# Function to save the matrics 
def save_matrics(metrics,file_path):
    ''' Save the Evalution metrics to a JSON FILE'''
    try:
        # Ensure Directory Exists
        os.makedirs(os.path.dirname(file_path),exist_ok=True)

        with open(file_path,'w') as file:
            json.dump(metrics,file,indent=4)
        logger.debug("Metrics saved to %s ",file_path)
    except Exception as e:
        logger.error("Error occurred while saving the metrics %s ",e)
        raise


# The Main Function From all The code Will Run 
def main():
    try:
        model=load_model()
        test_data=load_data()
        X_test=test_data.iloc[:,:-1]
        y_test=test_data.iloc[:,-1]
        params=load_params(params_path="params.yaml")
        metrics = evaluate_model(model, X_test, y_test,params["model_evaluation"]["n_splits"])
         
        #  Experiment Tracking Using DVC Live
        with Live(save_dvc_exp=True) as live:
            live.log_metric("accuracy", metrics["accuracy"])
            live.log_metric("precision", metrics["precision"])
            live.log_metric("recall", metrics["recall"])
            live.log_metric("f1", metrics["f1_score"])

            live.log_params(params)



        save_matrics(metrics, "evaluation_results/metrics.json")
    except Exception as e:
        logger.error("Failed to complete the Model Evaluation Process %s ",e)
        print(f"Error : {e}")


if __name__ == "__main__":
    main()
