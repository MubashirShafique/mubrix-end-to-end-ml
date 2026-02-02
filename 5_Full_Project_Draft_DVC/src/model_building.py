# IMPORTING LIBRARIES
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
import os
from sklearn.model_selection import train_test_split
import logging
import pickle
import yaml


# LOGGING CONFIGURATION

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger("model_building")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

log_file_path = os.path.join(log_dir, "model_building.log")
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


# FUNCTION: Load Data

def data_load():
    """
    Loads the feature engineered dataset from the Data folder.
    Returns:
        df (DataFrame): Loaded dataset.
    """
    try:
        df = pd.read_csv(r"Data\feature_engineering_data\feature_engineering_data.csv")
        logger.info("Data loaded successfully.")
        return df

    except FileNotFoundError:
        logger.error("Feature engineering CSV file not found.")
        raise

    except Exception as e:
        logger.error(f"Unexpected error while loading data: {e}")
        raise



# FUNCTION: Feature Selection + Encoding

def feature_selection(df):
    """
    Drops unnecessary columns and applies one-hot encoding to asset column.
    Args:
        df (DataFrame): Original dataset.
    Returns:
        df (DataFrame): Processed dataset with encoded features.
    """
    try:
        df = df.drop(columns=["date", "final_price"])
        df = pd.get_dummies(df, columns=["asset"], dtype=int)
        logger.info("Feature selection and encoding completed.")
        return df

    except Exception as e:
        logger.error(f"Error during feature selection: {e}")
        raise


# Save Train/Test Data

def save_train_test_data(X_train, X_test, Y_train, Y_test):
    """
    Combines and saves training and testing data as CSV files.
    """
    try:
        base_dir = "Data"
        cleaned_dir = os.path.join(base_dir, "cleaned_train_test_data")
        os.makedirs(cleaned_dir, exist_ok=True)

        train_df = X_train.copy()
        train_df["trend_signal"] = Y_train
        train_df.to_csv(os.path.join(cleaned_dir, "train_data.csv"), index=False)

        test_df = X_test.copy()
        test_df["trend_signal"] = Y_test
        test_df.to_csv(os.path.join(cleaned_dir, "test_data.csv"), index=False)

        logger.info("Train and test datasets saved successfully.")

    except Exception as e:
        logger.error(f"Error saving train/test data: {e}")
        raise



# FUNCTION: Train/Test Split

def train__test__split(df,test_size):
    """
    Splits the dataset into 80/20 training and testing sets.
    Saves the split datasets to disk.
    Returns:
        X_train (DataFrame)
        Y_train (Series)
    """
    try:
        X = df.drop("trend_signal", axis=1)
        Y = df["trend_signal"]

        X_train, X_test, Y_train, Y_test = train_test_split(
            X, Y, test_size=test_size, random_state=40
        )

        save_train_test_data(X_train, X_test, Y_train, Y_test)
        logger.info("Train-test split completed.")

        return X_train, Y_train

    except Exception as e:
        logger.error(f"Error during train-test split: {e}")
        raise



# FUNCTION: Train Model and Save

def train_model_and_save(X_train, Y_train,n_estimators,learning_rate,max_depth):
    """
    Trains an XGBoost classification model and saves model + training columns.
    """
    try:
         # For Handle Imbalance Data 
        pos = Y_train.sum()
        neg = len(Y_train) - pos
        scale_pos_weight = neg / pos

        xgb_model = XGBClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth= max_depth,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=1,
        reg_lambda=1.5,
        reg_alpha=0.5,
        min_child_weight=5,
        scale_pos_weight=scale_pos_weight, 
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss'
    )


        training_columns = list(X_train.columns)

        logger.info("Training started...")
        model = xgb_model.fit(X_train, Y_train)
        logger.info("Model training completed.")

        os.makedirs("models", exist_ok=True)

        with open("models/model.pkl", "wb") as f:
            pickle.dump(model, f)

        with open("models/Training_columns.pkl", "wb") as f:
            pickle.dump(training_columns, f)

        logger.info("Model and columns saved successfully.")

    except Exception as e:
        logger.error(f"Error during model training/saving: {e}")
        raise



# MAIN PIPELINE
def main():
    """
    Full model building pipeline:
    1. Load data
    2. Feature selection
    3. Train-test split
    4. Train & save model
    """
    try:
        logger.info("Pipeline started.")
        params=load_params(params_path="params.yaml")
        df = data_load()
        df = feature_selection(df)
        test_size=params["model_building"]["test_size"]
        X_train, Y_train = train__test__split(df,test_size=test_size)
        n_estimators=params["model_building"]["n_estimators"]
        learning_rate=params["model_building"]["learning_rate"]
        max_depth=params["model_building"]["max_depth"]
        train_model_and_save(X_train, Y_train,n_estimators,learning_rate,max_depth)

        logger.info("Pipeline completed successfully.")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
