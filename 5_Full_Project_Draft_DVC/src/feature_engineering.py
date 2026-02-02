# Importing Libraries 
import pandas as pd 
import numpy as np
import logging
import os 


# Ensure the "logs" directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Logging Configuration 
logger = logging.getLogger("feature_engineering")
logger.setLevel("DEBUG")

console_handler = logging.StreamHandler()
console_handler.setLevel("DEBUG")

log_file_path = os.path.join(log_dir, "feature_engineering.log")
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel("DEBUG")

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


def load_data() -> pd.DataFrame:
    """
    Load the preprocessed dataset from the Data folder.
    """
    logger.info("Loading preprocessed data...")
    df = pd.read_csv("Data/preprocessed_data/preprocessed_data.csv")
    logger.info(f"Data loaded successfully with shape {df.shape}")
    return df



def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add rolling, momentum, z-score and trend features for each asset.
    """
    logger.info("Starting feature engineering...")
    df["date"] = pd.to_datetime(df["date"])


    # Sort by asset and date
    df = df.sort_values(["asset", "date"]).reset_index(drop=True)
    logger.debug("Data sorted by asset and date.")

    g = df.groupby("asset")
    logger.debug("Data grouped by asset for rolling calculations.")

    # Rolling features
    df["7d_avg"] = g["final_price"].transform(lambda x: x.rolling(7).mean())
    df["30d_avg"] = g["final_price"].transform(lambda x: x.rolling(30).mean())
    df["daily_pct_change"] = g["final_price"].transform(lambda x: x.pct_change())
    df["volatility_7d"] = g["final_price"].transform(lambda x: x.rolling(7).std())
    df["momentum_14d"] = g["final_price"].transform(lambda x: x - x.shift(14))
    df["price_zscore"] = g["final_price"].transform(
    lambda x: (x - x.rolling(30).mean()) / (x.rolling(30).std() + 1e-9)
)


    logger.debug("Rolling features calculated.")

    # Trend Signal (your requested code inserted correctly)
    df["trend_signal"] = g.apply(
        lambda x: ((x["7d_avg"] > x["30d_avg"]).astype(int)).shift(-1)
    ).reset_index(level=0, drop=True)

    logger.debug("Trend signal generated.")

    # Drop NA rows
    df = df.dropna()
    logger.info(f"Feature engineering completed. Final shape: {df.shape}")

    return df



def save_data(df: pd.DataFrame) -> None:
    """
    Save feature engineered data into a dedicated folder.
    """
    logger.info("Saving feature engineered data...")

    base_dir = "Data"
    os.makedirs(base_dir, exist_ok=True)

    feature_eng_dir = os.path.join(base_dir, "feature_engineering_data")
    os.makedirs(feature_eng_dir, exist_ok=True)

    file_path = os.path.join(feature_eng_dir, "feature_engineering_data.csv")
    df.to_csv(file_path, index=False)

    logger.info(f"Data saved successfully at {file_path}")



def main() -> None:
    """
    Run the complete feature engineering pipeline.
    """
    logger.info("Feature engineering pipeline started.")

    df = load_data()
    df = add_features(df)
    save_data(df)

    logger.info("Feature engineering pipeline completed.")


if __name__ == '__main__':
    main()


