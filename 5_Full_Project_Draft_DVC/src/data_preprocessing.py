# importing Libraries 

import os 
import logging
import pandas as pd
import numpy as np


# Ensure "logs" directory exists
log_dir='logs'
os.makedirs(log_dir,exist_ok=True)

# Setting up logger
logger=logging.getLogger("data_preprocessing")
logger.setLevel("DEBUG")

console_handler=logging.StreamHandler()
console_handler.setLevel("DEBUG")

log_file_path=os.path.join(log_dir,'data_preprocessing.log')
file_handler=logging.FileHandler(log_file_path)
file_handler.setLevel("DEBUG")

formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    '''
    This Function Remove Dollar Sign from the final_price colum for further
    and convert it to float for furthur mathamtical operations 

    Parameters
    df : pd.DataFrame 

    Returns
    pd.DataFrame
    '''
    df["final_price"] = (
    df["final_price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .astype(float)
    )
    return df


def remove_old_rows(df: pd.DataFrame) -> pd.DataFrame:
    '''
    This Function Remove the same quantity of old rows as the quantity is fetched 
    from yfinance library

    -----------
    Parameters 
    df : pd.DataFrame

    -----------
    Process

    >> First of sorting the dataset according to date column
    >> then counting how many rows are fetched 
    >> then drop the same quantity of rows from the Head of the data 

    ----------
    Return
    pd.DataFrame

    '''
    try:
        df = df.sort_values("date").reset_index(drop=True)

        # Count how many new rows are added 
        new_rows_count = df.shape[0] - 50000

        # Remove only if new rows exist
        if new_rows_count > 0:
            df = df.iloc[new_rows_count:]
        else:
            pass

        logger.debug(f"Removed {new_rows_count} old rows successfully")
        return df

    except Exception as e:
        logger.error("Failed To remove rows") 
        raise



def save(df:pd.DataFrame) ->None:
    '''
    This Function make the Folder name preprocessed_data in the Data Folder 
    And save the dataset into it 

    ------------
    Parameters
    df : pd.DataFrame

    -----------
    Return 
    None
    '''
    base_dir="Data"
    # Create Data Folder if it is not exist 
    os.makedirs(base_dir,exist_ok=True)
    # create preprocessed_data folder if it is not exist
    prepro_dir=os.path.join(base_dir,"preprocessed_data")
    os.makedirs(prepro_dir,exist_ok=True)
    # Saving the file as name preprocessed_data.csv
    file_path=os.path.join(prepro_dir,"preprocessed_data.csv")
    df.to_csv(file_path,index=False)


def main():
    '''
    This Function is Main Function From where all the Functions will Run

    ----------
    Process 
    This Function call the preprocess ,remove_old_rpws and save function
    '''
    try:
        data=pd.read_csv(r"Data\raw_data\raw_data.csv")
        logger.debug("data Loaded Successfuly ")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
    try:
        df=preprocess(df=data)
        logger.debug("data preprocessed Successfuly ")
    except Exception as e :
        logger.error(f"Failed to preprocessing : {e} ")
    try:
        df=remove_old_rows(df)
    except Exception as e:
        logger.error(f"Failed to remove old rows: {e}")
    try:

        save(df=df)
        logger.debug("Data Saved Successfuly in the Data\preprocessed_data")
    except Exception as e:
        logger.error(f"Failed to save data: {e}")


if __name__ == '__main__':
    main()


