# importing libraries
from requests.exceptions import RequestException
import pandas as pd
import numpy as np
import yfinance as yf
import logging
import os
from datetime import datetime, timedelta


# Ensure the "logs" directory exists
log_dir='logs'
os.makedirs(log_dir,exist_ok=True)


# logging Configuration
logger=logging.getLogger("data_ingestion")
logger.setLevel('DEBUG')


console_handler=logging.StreamHandler()
console_handler.setLevel('DEBUG')

log_file_path=os.path.join(log_dir,'data.ingestion.log')
file_handler=logging.FileHandler(log_file_path)
file_handler.setLevel('DEBUG')


formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)


reverse_map = {
    "bitcoin": "BTC-USD",
    "ethereum": "ETH-USD",
    "litecoin": "LTC-USD",
    "ripple": "XRP-USD",
    "gold": "GC=F",
    "silver": "SI=F"
}
    

symbol_map = {
    "BTC-USD": "bitcoin",
    "ETH-USD": "ethereum",
    "LTC-USD": "litecoin",
    "XRP-USD": "ripple",
    "GC=F": "gold",
    "SI=F": "silver"
}
    
assets_list = [
    "BTC-USD",
    "ETH-USD",
    "LTC-USD",
    "XRP-USD",
    "GC=F",
    "SI=F"
]



def fetch_price_data(asset_symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches historical daily closing prices from Yahoo Finance.

    Parameters
    ----------
    asset_symbol : str
        e.g., 'BTC-USD'
    start_date : str
        Start date (YYYY-MM-DD)
    end_date : str
        End date (YYYY-MM-DD), exclusive

    Returns
    -------
    pd.DataFrame
        Columns: ['date', 'final_price', 'asset']
    """

    try:
        logger.debug(f"Fetching data for {asset_symbol} from {start_date} to {end_date}")

        data = yf.download(asset_symbol, start=start_date, end=end_date,progress=False)

        # Validate data
        if data is None or data.empty:
            logger.error(f"No data returned from yfinance for {asset_symbol}")
            raise ValueError(f"No price data available for {asset_symbol} between given dates.")

        data = data.reset_index()

        # Ensure required columns exist
        if "Date" not in data.columns or "Close" not in data.columns:
            logger.error(f"Expected columns not found for {asset_symbol}: {data.columns}")
            raise ValueError("Downloaded data missing expected columns (Date, Close).")

        data = data[["Date", "Close"]]
        data.columns = ["date", "final_price"]
        data["asset"] = asset_symbol

        logger.debug(f"Successfully loaded {len(data)} rows for {asset_symbol}")

        return data

    except RequestException as e:
        logger.error("Network/connection issue while fetching %s: %s", asset_symbol, e)
        raise

    except ValueError as e:
        logger.error("Value error for %s: %s", asset_symbol, e)
        raise

    except Exception as e:
        logger.error("Unexpected error fetching data for %s: %s", asset_symbol, e)
        raise




def build_dataset(old_df:pd.DataFrame, asset_symbol:str) ->pd.DataFrame:
    """
    Updates an existing dataset by fetching and appending new price data.

    Parameters
    ----------
    old_df : pd.DataFrame
        Existing dataset containing historical price data.
        Must include columns: ['date', 'final_price', 'asset'].
    asset_symbol : str
        Asset ticker symbol to update (e.g., 'BTC-USD').

    Process
    -------
    1. Identify the last available date for the given asset.
    2. Determine the next date range to fetch new data.
    3. Call `fetch_price_data()` to download fresh records.
    4. Concatenate old and new data, removing duplicates.
    5. Return the updated full dataset.

    Returns
    -------
    pd.DataFrame
        Updated dataset containing old + newly fetched rows for the asset.
    """
    try:
        old_df = old_df.copy()

        old_df["date"] = pd.to_datetime(old_df["date"])

        # Find last date of the asset
        last_date = old_df[old_df["asset"] == asset_symbol]["date"].max()

        # FIX for NaT
        if pd.isna(last_date):
            start_date = "2010-01-01"
        else:
            start_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")

        END_DATE = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")

        try:
            new_df = fetch_price_data(asset_symbol, start_date, END_DATE)
            if new_df.empty:
               logger.warning(f"No new data for {asset_symbol}, skipping")
               return old_df

        except Exception as e:
            raise RuntimeError(f"fetch_price_data failed: {e}")
        

        # Merge both
        full_df = pd.concat([old_df, new_df], ignore_index=True)
        full_df = full_df.reset_index(drop=True)
        return full_df
    
    except Exception as e:
        logger.error("Error in build_dataset: %s ",e)
        raise



def save_data(data: pd.DataFrame) -> None:
    """
    Saves the final raw dataset into the Data directory.

    Parameters
    ----------
    data : pd.DataFrame
        The processed dataset to be stored.
        Must contain standardized columns: ['date', 'final_price', 'asset'].

    Process
    -------
    1. Creates the 'Data' directory if it does not exist.
    2. Writes the dataset to 'raw_data.csv'.
    3. Logs the save location for debugging and verification.

    Returns
    -------
    None
        Writes the output file but returns no object.
    """
    try:
        base_dir="Data"
        # Create Data folder if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
        # Create raw folders
        raw_dir = os.path.join(base_dir, "raw_data")
        os.makedirs(raw_dir, exist_ok=True)
        
        # Saving csv File with name 'raw_data.csv'
        file_path = os.path.join(raw_dir, "raw_data.csv")
        data.to_csv(file_path, index=False)
        logger.debug("Data Saved to %s",file_path)
        
    except Exception as e:
        logger.error("Unexpected error occurred while saving the data: %s ",e)
        raise




def main():
    """
    Orchestrates the complete data ingestion workflow.

    Process
    -------
    1. Loads the existing multi-asset dataset from CSV.
    2. Converts human-readable asset names to their ticker symbols.
    3. Iterates through each asset in `assets_list` and updates its dataset.
    4. Converts ticker symbols back to human-readable names.
    5. Saves the fully updated dataset using `save_data()`.

    Input/Output
    ------------
    Input  : Experiments/multi_asset_market_data.csv
    Output : Data/raw_data.csv (updated dataset)

    Returns
    -------
    None
        Executes the full ingestion pipeline without returning a value.
    """
    try:
        old_data_path=r"Experiments\multi_asset_market_data.csv"

        old_df = pd.read_csv(old_data_path)

        
        # FIX: convert once globally before updates
        old_df["asset"] = old_df["asset"].replace(reverse_map)

        final_dataset = old_df.copy()

        for asset in assets_list:
            final_dataset = build_dataset(final_dataset, asset)
            
            
        final_dataset["asset"] = final_dataset["asset"].replace(symbol_map)
        save_data(final_dataset)
    except Exception as e:
        logger.error("Failed to complete the data ingestion process: %s",e)
        print(f"Error:{e}")




if __name__ == '__main__':
    main()
