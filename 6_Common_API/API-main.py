from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pickle
import pandas as pd
import os

# Paths for data and models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

MODEL_PATH = os.path.join(PROJECT_ROOT, "5_Full_Project_Draft_DVC", "models", "model.pkl")
TRAIN_COLUMNS_PATH = os.path.join(PROJECT_ROOT, "5_Full_Project_Draft_DVC", "models", "Training_columns.pkl")

TODAY_FEATURES_PATH = os.path.join(BASE_DIR, "today_features_for_all_assets.csv")
GRAPH_DATA_PATH = os.path.join(BASE_DIR, "for_graph.csv")

# -----------------------------------------
#          LOAD MODEL & ARTIFACTS
# -----------------------------------------

# Load the trained XGBoost model
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# Load the training columns to ensure data alignment
with open(TRAIN_COLUMNS_PATH, "rb") as f:
    Training_Columns = pickle.load(f)

app = FastAPI()

class InputData(BaseModel):
    asset: str

# -----------------------------------------
#          PREDICTION ENDPOINT
# -----------------------------------------

@app.post("/predict")
def predict_premium(request: InputData):

    # 1. Load the latest features for prediction
    df = pd.read_csv(TODAY_FEATURES_PATH)
    
    # Filter data for the specific asset requested
    row = df[df["asset"] == request.asset]

    if row.empty:
        return JSONResponse(status_code=404, content={"message": "Asset not found"})

    # 2. Preprocess the data
    # Create dummy variables for categorical asset column
    df_proc = pd.get_dummies(row, columns=["asset"], dtype=int)
    
    # Drop non-feature columns
    df_proc.drop(columns=["date", "final_price"], errors="ignore", inplace=True)

    # Reindex columns to match the training set format
    new_last_row = df_proc.reindex(columns=Training_Columns, fill_value=0.0)

    # 3. Make Prediction & Calculate Confidence Score
    # Use predict() to get the class (0 for Down, 1 for Up)
    prediction = int(model.predict(new_last_row)[0])
    
    # Use predict_proba() to get probability of each class
    # Format: [prob_of_0, prob_of_1]
    probabilities = model.predict_proba(new_last_row)[0]
    
    # Extract confidence score for the predicted class and convert to percentage
    confidence_score = float(probabilities[prediction]) * 100

    # 4. Prepare Graph Data for Frontend
    df_for_graph = pd.read_csv(GRAPH_DATA_PATH)
    df_asset = df_for_graph[df_for_graph["asset"] == request.asset]
    
    # Format: [{"date": "2026-01-01", "final_price": 100}, ...]
    graph_data = df_asset[["date", "final_price"]].to_dict(orient="records")

    # 5. Return JSON Response including Confidence Score
    return JSONResponse(
        status_code=200,
        content={
            "prediction": prediction,
            "confidence": round(confidence_score, 2), # Send rounded percentage e.g. 85.5
            "graph_data": graph_data
        }
    )