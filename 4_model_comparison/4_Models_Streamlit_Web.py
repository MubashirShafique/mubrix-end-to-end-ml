# Importing All Libraries 
import streamlit as st
import seaborn as sns
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score
from sklearn.model_selection import cross_val_predict,StratifiedKFold


# ---------- SESSION STATE FIX (IMPORTANT) ----------
if "training_done" not in st.session_state:
    st.session_state.training_done = False
if "results_df" not in st.session_state:
    st.session_state.results_df = None
if "best_model" not in st.session_state:
    st.session_state.best_model = None



results = []

st.set_page_config(page_title="Model Training Progress", page_icon="🤖", layout="centered")
st.title("Model Training Dashboard")

# Importing DATASETS
df = pd.read_csv("Balanced_cleaned_multi_asset_market_data.csv")

# Feature Selection
df.drop(columns=['date','final_price'], inplace=True)

# Applying One Hot Encoding On Assets Column
df = pd.get_dummies(df, columns=['asset'], dtype=int)

# Dividing Features as Target Feature (Y) and Input Feature (X)
X = df.drop('trend_signal', axis=1)
Y = df['trend_signal']

# Test And Training Data Splitting 
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=43)


# ***** Defining all Four Algorithms With Parameters ******

# Logistic Regression 
log_model = LogisticRegression(
    penalty='l2',
    solver='lbfgs',
    max_iter=2000,
    C=1.0,
    n_jobs=-1
)

# Decision Tree
tree_model = DecisionTreeClassifier(
    criterion='gini',
    max_depth=15,
    min_samples_split=50,
    min_samples_leaf=20,
    max_features='sqrt',
    random_state=42
)

# Random Forest
rf_model = RandomForestClassifier(
    n_estimators=200,
    criterion='gini',
    max_depth=20,
    min_samples_split=50,
    min_samples_leaf=20,
    max_features='sqrt',
    bootstrap=True,
    n_jobs=-1,
    random_state=42
)

# XGBoost
xgb_model = XGBClassifier(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8,
    gamma=1,
    reg_lambda=1.5,
    reg_alpha=0.5,
    min_child_weight=5,
    random_state=42,
    n_jobs=-1,
    eval_metric='logloss'
)

# All Models List 
models = [log_model, tree_model, rf_model, xgb_model]


# ---------------------------------------------------------
#               START TRAINING BUTTON LOGIC (FIXED)
# ---------------------------------------------------------
if st.button("Start Training"):

    st.session_state.training_done = True
    results = []

    for item in models:
        st.progress(0, text=f"Training {item.__class__.__name__}...")
        item.fit(X_train, Y_train)
        st.progress(100, text=f"Training {item.__class__.__name__} done ✅")

        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        y_pred = cross_val_predict(item, X, Y, cv=cv)

        acc = accuracy_score(Y, y_pred)
        prec = precision_score(Y, y_pred, average='weighted')
        rec = recall_score(Y, y_pred, average='weighted')
        f1 = f1_score(Y, y_pred, average='weighted')

        results.append({
            "Model": item.__class__.__name__,
            "Accuracy": round(acc, 3),
            "Precision": round(prec, 3),
            "Recall": round(rec, 3),
            "F1-Score": round(f1, 3)
        })

        time.sleep(0.5)

    # Save results in session_state to prevent reset
    df_results = pd.DataFrame(results)
    st.session_state.results_df = df_results
    st.session_state.best_model = df_results.loc[df_results['F1-Score'].idxmax(), 'Model']



# ---------------------------------------------------------
#               SHOW RESULTS (EVEN AFTER DOWNLOAD)
# ---------------------------------------------------------
if st.session_state.training_done and st.session_state.results_df is not None:

    df = st.session_state.results_df

    st.write(df)

    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False),
        file_name="data.csv",
        mime="text/csv",
    )

    # Create Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    melted_df = df.melt(
        id_vars="Model",
        value_vars=["Accuracy", "Precision", "Recall", "F1-Score"],
        var_name="Metric",
        value_name="Score"
    )

    sns.barplot(data=melted_df, x="Model", y="Score", hue="Metric", ax=ax)

    ax.set_title("📊 Model Performance Comparison (Accuracy, Precision, Recall, F1-Score)")
    ax.set_ylabel("Score")
    ax.set_xlabel("Models")
    ax.set_ylim(0.8, 1.0)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig)

    best_model = st.session_state.best_model
    st.write(f"🏆 Best Model Overall: {best_model}")

    # Show parameters
    def get_param(i):
        params = i.get_params()
        pdf = pd.DataFrame(list(params.items()), columns=["Parameter", "Value"])
        st.write(pdf)
        st.download_button(
            label="Download Parameters CSV",
            data=pdf.to_csv(index=False),
            file_name=f"parameters_of_{i.__class__.__name__}.csv",
            mime="text/csv",
        )

    if best_model == "RandomForestClassifier":
        get_param(rf_model)
    elif best_model == "LogisticRegression":
        get_param(log_model)
    elif best_model == "DecisionTreeClassifier":
        get_param(tree_model)
    elif best_model == "XGBClassifier":
        get_param(xgb_model)
