# Multi-Asset Trend Prediction Pipeline (End-to-End ML + DVC) (Draft)

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Machine Learning](https://img.shields.io/badge/ML-Pipeline-green)
![XGBoost](https://img.shields.io/badge/Model-XGBoost-orange)
![DVC](https://img.shields.io/badge/DVC-Pipeline%20Orchestration-purple)
![DVC Live](https://img.shields.io/badge/DVC%20Live-Experiment%20Tracking-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## Overview

This project is a fully automated end-to-end Machine Learning pipeline built for **multi-asset financial trend prediction**.  
It integrates:

- Yahoo Finance (YFinance) for live market data  
- DVC for pipeline orchestration  
- DVC Live for experiment tracking  
- XGBoost classifier  
- A structured Data Engineering + ML workflow  

The system automatically:

- Downloads & updates multi-asset historical data  
- Cleans & preprocesses the dataset  
- Generates technical indicators & engineered features  
- Trains an ML model using XGBoost  
- Evaluates performance and logs experiments via DVC Live  
- Saves all datasets, models, metrics, and logs in structured folders  

---
## Folder Structure

```
  .
  ├── .dvc/                         # DVC internal metadata
  ├── Experiments/                  # Original seed dataset
  ├── dvclive/                      # DVC-Live experiment logs
  ├── src/
  │   ├── data_ingestion.py
  │   ├── data_preprocessing.py
  │   ├── feature_engineering.py
  │   ├── model_building.py
  │   ├── model_evaluation.py
  │
  ├── dvc.lock
  ├── dvc.yaml                      # DVC pipeline definition
  ├── params.yaml                   # Hyperparameters
  ├── requirements.txt
  └── README.md

```

## Folder Structure After Running The Project 
```
.
├── .dvc/                       # DVC internal metadata
├── Data/
│   ├── raw_data/               # Ingested dataset
│   ├── preprocessed_data/      # Cleaned dataset
│   ├── feature_engineering_data/ # Engineered features
│   ├── cleaned_train_test_data/  # Train/Test split
│
├── dvclive/                    # DVC-Live experiment logs
├── evaluation_results/         # Evaluation metrics (JSON)
├── Experiments/                # Original seed dataset
├── logs/                       # Logs for each pipeline stage
├── models/
│   ├── model.pkl               # Trained ML model
│   ├── Training_columns.pkl
│
├── src/
│   ├── data_ingestion.py
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   ├── model_building.py
│   ├── model_evaluation.py
│
├── params.yaml                 # Hyperparameters
├── dvc.yaml                    # DVC pipeline definition
├── dvc.lock
├── requirements.txt
└── README.md


```
## Pipeline Overview (Stage-by-Stage)
### The entire ML workflow is declared in dvc.yaml.

- yaml
```
stages:
  data_ingestion:
    cmd: python src/data_ingestion.py
    deps:
    - src/data_ingestion.py
    outs:
    - Data/raw_data

  data_preprocessing:
    cmd: python src/data_preprocessing.py
    deps:
    - Data/raw_data
    - src/data_preprocessing.py
    outs:
    - Data/preprocessed_data

  feature_engineering:
    cmd: python src/feature_engineering.py
    deps:
    - Data/preprocessed_data
    - src/feature_engineering.py
    outs:
    - Data/feature_engineering_data

  model_building:
    cmd: python src/model_building.py
    deps:
    - Data/feature_engineering_data
    - src/model_building.py
    params:
    - model_building.test_size
    - model_building.n_estimators
    - model_building.learning_rate
    - model_building.max_depth
    outs:
    - Data/cleaned_train_test_data
    - models/model.pkl

  model_evaluation:
    cmd: python src/model_evaluation.py
    deps:
    - Data/cleaned_train_test_data
    - models/model.pkl
    - src/model_evaluation.py
    params:
    - model_evaluation.n_splits
    metrics:
    - evaluation_results/metrics.json
  ```
## Parameters (params.yaml)
- yaml
```
model_building:
  test_size: 0.30
  n_estimators: 600
  learning_rate: 0.06
  max_depth: 9

model_evaluation:
  n_splits: 6
```
## Pipeline Stages Explained
### Each stage below explains the purpose, operations, outputs, and functions involved.

1. Data Ingestion — src/data_ingestion.py
```
This stage:

Reads the existing dataset from Experiments/multi_asset_market_data.csv

Maps asset names to tickers

Downloads latest market data using YFinance

Appends new rows

Ensures correct schema
```
```
Saves the updated dataset to:

Data/raw_data/raw_data.csv
```
```
Functions:
fetch_price_data()

build_dataset()

save_data()

main()
```

2. Data Preprocessing — src/data_preprocessing.py
```
This stage:

Removes "$" from final_price

Converts prices to float

Removes excess historical rows
```
```
Saves cleaned dataset to:
Data/preprocessed_data/preprocessed_data.csv
```
```
Functions:
preprocess()

remove_old_rows()

save()

main()
```
3. Feature Engineering — src/feature_engineering.py
```
Adds financial indicators:

7-day moving average

30-day moving average

Daily % change

7-day volatility

14-day momentum

Z-score

Trend signal (Label)
```
```
Output:
Data/feature_engineering_data/feature_engineering_data.csv
```
```
Functions:
load_data()

add_features()

save_data()

main()
```
4. Model Building — src/model_building.py
```
This stage:

Loads params from params.yaml

Selects features

Encodes categorical columns

Splits into train/test

Trains XGBoost model

Handles imbalance with scale_pos_weight
```
```
Saves outputs:
models/model.pkl
models/Training_columns.pkl
Data/cleaned_train_test_data/train_data.csv
Data/cleaned_train_test_data/test_data.csv
```
```
Functions:
load_params()

data_load()

feature_selection()

train__test__split()

train_model_and_save()

main()
```
5. Model Evaluation — src/model_evaluation.py
```
This stage:

Loads trained model

Loads test dataset

Predicts trend

Computes:

Accuracy

Precision

Recall

F1-score

Stratified K-Fold cross-validation

Logs metrics via DVC Live
```
```
Saves metrics:
evaluation_results/metrics.json
```
```
Functions:
load_params()

load_model()

load_data()

evaluate_model()

save_matrics()

main()
```

## How to Run the Entire Pipeline
1. Install dependencies
```
pip install -r requirements.txt
```
2. Run the full pipeline
```
pip install dvc
dvc repro
```
3. View experiment metrics
```
dvc metrics show
```
4. Check DVC Live dashboard
### Located inside the dvclive/ folder.

## Outputs Generated
```
Stage	Output Files
Data Ingestion	-----> raw_data.csv
Preprocessing	------>  preprocessed_data.csv
Feature Engineering	---> feature_engineering_data.csv
Model Building	-------> model.pkl, Training_columns.pkl, train/test CSVs
Evaluation	-----> metrics.json, dvclive logs
```
## Technologies Used
- Python

- Pandas, NumPy

- YFinance

- XGBoost

- Scikit-Learn

- DVC

- DVC Live

- YAML

- Logging

## What This Project Solves

### This system provides:

- Automated dataset updates

- Clean, structured inputs for ML

- Advanced engineered financial indicators

- Fully reproducible ML workflow

- Experiment tracking

- Controlled, monitored ML lifecycle

## Author

### Muhammad Mubashir Shafique
