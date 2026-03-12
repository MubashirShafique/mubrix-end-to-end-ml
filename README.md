# Mubrix: Your AI-Powered Market Compass (End-to-End Project) 

**Mubrix** is an end-to-end decision-making engine designed to bridge the gap between complex market data and actionable trading insights. By leveraging machine learning, Mubrix provides trend predictions for 6 major assets (including Gold, Silver, and Bitcoin), helping traders navigate volatility with confidence and also Andriod App.

---

## Key Features
- Trend Prediction: Instant UP/DOWN signals for 6 major assets using optimized ML models.
- Confidence Scoring: Provides a probability-based confidence score for every prediction.
- Deep Visualization: Integrated 90-day historical trend analysis.
- Real-time :  latest market news.
- Multi-Platform Access: Available via a Streamlit Web App and Android Application(Flutter).

---

## Repository Structure
- **1_Data:** Dataset used for training.  
- **02_Python_EDA:** Notebook with model training and evaluation steps.  
- **03_Saved_Model:** Trained `.pkl` files (Model and Vectorizer).  
- **04_API_Backend:** FastAPI scripts for serving the model.  
- **05_Streamlit_App:** Python web UI code using Streamlit.  
- **06_Android_App:** Flutter mobile app source code.  

---

## Installation & Setup Guide

### 1. Backend Setup (FastAPI)
First, run the API:

```bash
# Go to API folder
cd 04_API_Backend

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn API:app --reload
```

### 2. Web App Setup (Streamlit)
```bash
# Go to Streamlit folder
cd 05_Streamlit_App

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run Streamlit_App.py
```


### 3. Mobile App Setup (Flutter)
```bash
# Go to Android app folder
cd 06_Android_App

# Get Flutter packages
flutter pub get

# Run the app
flutter run

```
## How It Works

- User enters an SMS or Email text.

- FastAPI sends it to the NLP model.

- Model predicts Spam or Ham.

- Result is shown instantly in Web or Mobile app.


## Notes

- Make sure Python and Flutter are installed on your system.

- API must be running before using Web or Mobile apps.

- Dataset and trained model files are already included in the repository.
