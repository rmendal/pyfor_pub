"""
The data should be pulled and passed to a tulipy indicator in strategy.py as a numpy array.
"""

from __init__ import UserVals
import logging
from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments
import numpy as np

logging.basicConfig(format='\n%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', filename="log/candles.log", filemode='a', level=logging.DEBUG)
u = UserVals

class UserData:
    client = API(access_token=u.key)

    #TODO: Passing this in from the init fails. Fix it!
    # o = instruments.InstrumentsCandles(instrument=u.pair, params=u.params)
    o = instruments.InstrumentsCandles(instrument="EUR_USD", params=u.params) # for testing

class Candles:
    def ohlc(self, data):
        # Call imported UserData class
        UserData.client.request(UserData.o)
        candles = UserData.o.response.get("candles")
        candle_data = candles[data].get("mid")

        # OHLC variables to return in array
        open = candle_data.get("o")
        high = candle_data.get("h")
        low = candle_data.get("l")
        close = candle_data.get("c")
        return float(open), float(high), float(low), float(close)

    # Define clean function routes for returning proper data
    def open(self, data):
        return self.ohlc(data)[0]

    def high(self, data):
        return self.ohlc(data)[1]

    def low(self, data):
        return self.ohlc(data)[2]

    def close(self, data):
        return self.ohlc(data)[3]

    def get_candles(self):
        close_list = []
        for x in range(0, u.count):
            close_list.append(self.close(x))
        return np.asarray(close_list)

# TODO: For testing only, remove from final release
#p = Candles()
#print(p.get_candles())