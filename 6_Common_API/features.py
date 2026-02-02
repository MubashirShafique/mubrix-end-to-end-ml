
# Extracting date to fetching data from yfinanace
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd 

# Aaj ki date
today = datetime.now()

# 60 din peechay (Minus)
sixty_days_ago = today - timedelta(days=90)
one_days_after = today + timedelta(days=1)
# Format convert karna (YYYY-MM-DD)
start_date = sixty_days_ago.strftime("%Y-%m-%d")
one_day = one_days_after.strftime("%Y-%m-%d")




assets_list = [
    "BTC-USD",
    "ETH-USD",
    "LTC-USD",
    "XRP-USD",
    "GC=F",
    "SI=F"
]




# ***************************  Lines of code for fetching data and adding Features *******************************************


# ----------------------------------------------------------
# FUNCTION: Fetch Price Data from yfinance
# ----------------------------------------------------------
def fetch_price_data(asset_symbol, start_date, end_date):
    data = yf.download(asset_symbol, start=start_date, end=end_date)
    data = data.reset_index()
    data = data[["Date", "Close"]]
    data.columns = ["date", "final_price"]
    data["asset"] = asset_symbol
    return data



# ----------------------------------------------------------
# FUNCTION: Feature Engineering
# ----------------------------------------------------------
def add_features(df):

    # Always group by asset
    df = df.sort_values(["asset", "date"]).reset_index(drop=True)

    g = df.groupby("asset")

    df["7d_avg"] = g["final_price"].transform(lambda x: x.rolling(7).mean())
    df["30d_avg"] = g["final_price"].transform(lambda x: x.rolling(30).mean())

    df["daily_pct_change"] = g["final_price"].transform(lambda x: x.pct_change())

    df["volatility_7d"] = g["final_price"].transform(lambda x: x.rolling(7).std())

    df["momentum_14d"] = g["final_price"].transform(lambda x: x - x.shift(14))

    df["price_zscore"] = g["final_price"].transform(
        lambda x: (x - x.rolling(30).mean()) / x.rolling(30).std()
    )

    return df



main_df = []
for_graph=[]

for i in assets_list:
    df = fetch_price_data(i, start_date, one_day)
    if df.empty:
        continue
    df = add_features(df)
    for_graph.append(df[['asset','final_price','date']])
    main_df.append(df.tail(1))

main_df = pd.concat(main_df, ignore_index=True)
for_graph=pd.concat(for_graph,ignore_index=True)





symbol_to_name = {
    "BTC-USD": "bitcoin",
    "ETH-USD": "ethereum",
    "LTC-USD": "litecoin",
    "XRP-USD": "ripple",
    "GC=F": "gold",
    "SI=F": "silver"
}
main_df["asset"] = main_df["asset"].replace(symbol_to_name)
for_graph["asset"] = for_graph["asset"].replace(symbol_to_name)
main_df=main_df.dropna()
for_graph=for_graph.dropna()

main_df.to_csv(r"today_features_for_all_assets.csv",index=False)
for_graph.to_csv(r"for_graph.csv",index=False)