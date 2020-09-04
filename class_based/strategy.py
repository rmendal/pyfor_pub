from tulipy import rsi, ema, sma, bbands, macd
import numpy as np
from candles import Candles
import logging

logging.basicConfig(format='\n%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', filename="log/strategy.log", filemode='a', level=logging.DEBUG)

### TESTING ONLY ###
# raw_data is for testing. Delete later.
# raw_data = np.asarray([1.12446, 1.1252, 1.12581, 1.12604, 1.1279, 1.12929, 1.12353, 1.1221, 1.1227, 1.12328, 1.12394, 1.12862, 1.12935, 1.12754, 1.12748, 1.12671, 1.12652, 1.1317, 1.13398, 1.13333], dtype=np.float64)
c = Candles()
#array_data = np.asarray(c.get_candles)
### TESTING ONLY ###

class Strategies:
    def __init__(self, data, period, stddev=2):
        self.data = data
        self.period = period
        self.stddev = stddev
    
    def rsi(self):
        """
        0-30: Oversold Area
        30-70: Neutral Area
        70-100: Overbought Area
        """
        try:
            return rsi(self.data, self.period)
        except Exception:
            logging.exception('')

    def sma(self):
        try:
            return sma(self.data, self.period)
        except Exception:
            logging.exception('')

    def bbands(self):
        try:
            return bbands(self.data, self.period, self.stddev)
        except Exception:
            logging.exception('')

    def ema(self):
        try:
            return ema(self.data, self.period)
        except Exception:
            logging.exception('')

    def macd(self):
        try:
            return macd(self.data, short_period=1, long_period=5, signal_period=10)
        except Exception:
            logging.exception('')


# TODO: For testing. Delete later.
s = Strategies(c.get_candles(), 14)
# s = Strategies(raw_data, 6)
# print(s.rsi())
# print(s.sma())
# print(s.bbands())
# print(s.ema())
#print(array_data)
