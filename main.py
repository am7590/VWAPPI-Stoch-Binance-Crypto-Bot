import pandas_ta

from strategy import *
# Good info: https://www.tradingsetupsreview.com/volume-weighted-moving-average-vwma/

def run_technicals(ticker_pair, timeframe):
    # Create a dataframe with price data + technical indicators
    dataframe = get_minute_data(ticker_pair, timeframe, "100")

    print("Before indicators:\n", dataframe)

    apply_technical_indicators(dataframe)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print("After indicators:\n", dataframe)


    print("After indicators:\n", dataframe)


def run_bot(ticker_pair, timeframe, quantity):
    # Create a dataframe with price data + technical indicators
    dataframe = get_minute_data(ticker_pair, timeframe, "100")
    apply_technical_indicators(dataframe)

    # Find buy signals
    inst = Signals(dataframe, 25)
    inst.decide()
    # print(dataframe[dataframe.Buy == 1])

    # Run Strategy to find close price for current trade
    # Does not actually trade anything
    while True:
        strategy(ticker_pair, quantity)
        time.sleep(1)


if __name__ == '__main__':
    # help(pandas_ta.vwma)
    run_bot("BTCUSDT", "1m", 50)
    # run_technicals("BTCUSDT", "1m")
