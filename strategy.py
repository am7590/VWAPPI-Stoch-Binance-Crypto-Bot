import pandas as pd
import ta as ta
import numpy as np
import pandas_ta as pta
import sheets
from datetime import datetime, timezone
import time
from data import *


def get_true_count(df, iter):
    true_count = 0
    iter_count = 0
    last_column = df.iloc[:, -1]
    for row in last_column:
        iter_count += 1
        if iter_count > iter:
            break

        # print(row)
        if row:
            true_count += 1

    return true_count


def get_false_count(df, iter):
    false_count = 0
    iter_count = 0
    last_column = df.iloc[:, -1]
    for row in last_column:
        iter_count += 1
        if iter_count > iter:
            break

        # print(row)
        if not row:
            false_count += 1

    return false_count


def get_time():
    now_utc = datetime.now(timezone.utc)
    return now_utc.strftime('%m/%d/%Y %H:%M:%S')


def get_title_time():
    now_utc = datetime.now(timezone.utc)
    return now_utc.strftime('%m/%d/%Y %H:%M'+":00")


# Add K-line, D-line, RSI, and MACD columns to any dataframe
def apply_technical_indicators(df):
    # df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window=14, smooth_window=3)
    df['vwma'] = pta.vwma(df['Close'], df['Volume'], length=14)
    df.dropna(inplace=True)


class Signals:
    # lags is steps back
    def __init__(self, df, lags):
        self.dfx = None
        self.df = df
        self.lags = lags

    def get_trigger(self):
        self.dfx = pd.DataFrame()
        count = 0

        for i in range(self.lags + 1):
            # Check if vwma is greater than close
            mask = (self.df['vwma'].shift(i) > self.df['Close'].shift(i))  # & (self.df['%D'].shift(i) < 20)

            # Append to dataframe
            # dfx = dfx.append(mask, ignore_index=True)  # Depreciated
            dfxn = pd.DataFrame([mask])
            self.dfx = pd.concat([self.dfx, dfxn])

        # Print signals DF
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print("dfx:\n", self.dfx)

        return self.dfx

    # Are all buying conditions and the trigger fulfilled?
    def decide(self):

        # Error check if df was not created yet
        dataframe = self.get_trigger()
        if get_title_time() not in dataframe:
            return

        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(self.get_trigger()[get_title_time()]) #.iloc[-1]


        # Check for if vwma is above close and if the last 5 bars are below close




        print("Last df value: ", dataframe[get_title_time()].iloc[0])
        print("Last 5 false: ", get_false_count(dataframe, 5))

        self.df['Buy'] = np.where(
            (dataframe[get_title_time()].iloc[0]) & get_false_count(dataframe, 5) == 4, 1, 0)


def strategy(pair, qty, open_position=False):
    df = get_minute_data(pair, '1m', '100')
    apply_technical_indicators(df)
    inst = Signals(df, 25)
    inst.decide()

    print(f"" + str(get_time()) + "\tBOT RUNNING: current close price for " + pair + " is " + str(
        df.Close.iloc[-1]))

    # If there is a buying signal in the last row, place an order
    client = connect_to_client()
    if df.Buy.iloc[-1]:
        print(f"\nNew market BUY order for " + str(qty) + " " + pair + "\n")
        aoa = [[str(get_time()), "BUY", pair, str(float(df.Close.iloc[-1])), str(qty)]]
        sheets.update_sheet(aoa)
        # order = client.create_order(symbol=pair, side='BUY', type='MARKET', quantity=qty)
        # print(order)

        # Filter out price of the order to find official buying price
        buyprice = float(df.Close.iloc[-1])  # buyprice = float(order['fills'][0]['price'])
        open_position = True

    # Set parameters and close position
    while open_position:
        time.sleep(0.5)  # Avoid excessive requests to API
        df = get_minute_data(pair, '1m', '2')  # grab last 2 minutes of data
        print(f"Current Close: " + str(df.Close.iloc[-1]))
        print(f"Current Target: " + str(buyprice * 1.005))  # 0.5% take profit
        print(f"Current Stop loss is: " + str(buyprice * 0.995) + "\n")  # 0.5% stop loss

        # Check for stop loss
        if df.Close[-1] <= buyprice * 0.995 or df.Close[-1] >= 1.005 * buyprice:
            # Place sell order
            # order = client.create_order(symbol=pair, side='SELL', type='MARKET', quantity=qty)
            # print(order)
            print(f"\n New market SELL order for " + str(qty) + " " + pair + "\n")
            aoa = [[str(get_time()), "SELL", pair, str(df.Close[-1]), str(qty)]]
            sheets.update_sheet(aoa)
            break
