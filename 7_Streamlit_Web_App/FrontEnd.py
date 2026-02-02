import streamlit as st
import requests
import pandas as pd

# API URL (Make sure API is running)
API_URL = "http://localhost:8000/predict"

st.set_page_config(page_title="Market Predictor", layout="centered")

st.title("Multi Assets Trend Predictor")
st.markdown("Select an asset to predict its trend for tomorrow.")

# Asset Selection
option = st.selectbox(
    "Choose Asset:",
    ["bitcoin", "ethereum", "litecoin", "ripple", "gold", "silver"]
)

if st.button(f"Predict & Analyze {option.capitalize()}"):
    
    # Progress bar for better UI experience
    with st.spinner('Fetching data from API...'):
        input_payload = {"asset": option}

        try:
            # Request to API
            response = requests.post(API_URL, json=input_payload)

            if response.status_code == 200:
                result = response.json()
                
                # 1. Get Prediction and Confidence Score
                prediction = result["prediction"]
                confidence = result.get("confidence", 0) # Get confidence from API
                
                # 2. Get Graph Data
                graph_data = result["graph_data"]
                
                # --- Create Graph ---
                df = pd.DataFrame(graph_data)
                
                if not df.empty:
                    df["date"] = pd.to_datetime(df["date"])
                    df.set_index("date", inplace=True)
                    
                    st.subheader(f"{option.capitalize()} Price Trend (Last 90 Days)")
                    st.line_chart(df["final_price"], color="#FF4B4B")
                else:
                    st.warning("No graph data available.")

                # --- Display Prediction & Confidence Result ---
                st.divider()
                st.subheader("Prediction Result:")
                
                trend_text = "UPWARD" if prediction == 1 else "DOWNWARD"
                trend_color = "green" if prediction == 1 else "red"
                
                # Display Prediction with dynamic text
                if prediction == 1:
                    st.success(f"### Tomorrow the **{option.upper()}** trend will be **{trend_text}**")
                else:
                    st.error(f"### Tomorrow the **{option.upper()}** trend will be **{trend_text}**")

                # --- Confidence Score Section ---
                st.write(f"**Confidence Level:** {confidence}%")
                
                # Visual Progress Bar (Color changes based on confidence)
                bar_color = "green" if confidence > 70 else "orange" if confidence > 50 else "red"
                st.progress(int(confidence))
                
                st.info(f"There is a **{confidence}%** chance that the market will move **{trend_text}**.")

            else:
                st.error(f"API Error: {response.status_code} - {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("Connection Failed! Make sure API is running on port 8000.")