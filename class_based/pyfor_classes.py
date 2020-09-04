#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Goal is $5864.50/year so $18.80/day, roughly 16 pips/day if using EUR/USD
"""
# Class Imports
from strategy import Strategies
from candles import Candles
from __init__ import UserVals

# Standard library imports
from time import sleep
import smtplib

"""Logging libraries go here.
from datetime import date
import logging
"""
# Non-Standard Imports
import cutie

# OandapyV20 specific imports
import oandapyV20
from oandapyV20 import API
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.instruments as instruments

# TODO: Define logging
# logging.basicConfig(filename=f"{date.today()}.log", level=logging.INFO)

# Major and minor pairs. No exotics at this time
pairsList = ["EUR/USD", "USD/JPY", "GBP/USD", "USD/CHF", "USD/CAD", "AUD/USD", "NZD/USD", "EUR/GBP", "EUR/AUD",
             "GBP/JPY", "CHF/JPY", "NZD/JPY", "GBP/CAD"]

client = API(access_token=UserVals.key)
r = accounts.AccountSummary(UserVals.accountID)
s = accounts.AccountDetails(UserVals.accountID)


class Trader:

    def __init__(self):
        #s = Strategies()
        c = Candles()

        self.resistance = 0
        self.support = 0
        self.status = "Not trading"
        self.current_trade = ""
        self.killswitch = False
        self.data = c.get_candles()

        # Initialize Indicators
        self.current_close = self.data[-1]
        self.lotSize = ()

        """self.SMA1 = s.SMA(self.data, userVals.count, userVals.SMAbig)
        self.SMA1previous = s.SMAprev(self.data, userVals.count, userVals.SMAbig)
        self.SMA2 = s.SMA(self.data, userVals.count, userVals.SMAsmall)
        self.SMA2previous = s.SMAprev(self.data, userVals.count, userVals.SMAsmall)"""

        # TODO Get account info and balance
    def get_balance(self):
        """ Retrieve various information from the AccountSummary call found at https://bit.ly/2E2hoAz
        :return: acct balance
        """
        client.request(r)
        starting_balance = int(float(r.response.get("account", {}).get("balance")))
        #working_balance = starting_balance
        return starting_balance

    def long(self):
        pass

    def short(self):
        pass

    def position_size(self):
        """
        Calculates the position size before opening a trade based on
        info from Babypips.com http://bit.ly/2Mx11B8

        This should be calculated before each trade is placed and based on current account balance.
        :return: position size
        """
        current_balance = int(float(r.response.get("account", {}).get("balance")))
        risk_amt = current_balance * 0.01
        pip_value = (risk_amt / 50)  # 50 being the amount of pips I'm willing to lose.
        position_size = int((pip_value * (10000 / 1)))
        return position_size

    def open_trades(self):
        """
        Find open number of trades on account
        """
        get_deets = client.request(s)
        return get_deets.get("account").get("openTradeCount")

    def trade(self):
        """
        Checks for a viable trade and executes one, else it sleeps for 60 seconds
        """

        position_size = self.position_size()


if __name__ == "__main__":
    # Ask for input from user as to which currency pair they want to trade then assign it to UserVals
    u = UserVals
    t = Trader
    print(t.open_trades(self))
    # print("What pair are you trading today?")
    # chosen_pair = pairsList[cutie.select(pairsList)]
    # u.pair = chosen_pair
    # u.count = input("Candle count: ")

    # print(f"\nYou're trading {u.pair}...")
    # print(f"Candle count is {u.count}")
