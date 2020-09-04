#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Class Imports
from strategy import Strategies
from candles import Candles
from __init__ import UserVals

# Standard library imports
import datetime
import pytz
import smtplib
import logging
import re
import json
from time import sleep

# Non-Standard Imports
# import cutie # Used for currency menu on initial start up not used for now

# OandapyV20 specific imports
import oandapyV20
from oandapyV20 import API
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest
import oandapyV20.endpoints.trades as trades
from oandapyV20.exceptions import V20Error
import oandapyV20.types as tp


logging.basicConfig(format='\n%(asctime)s %(levelname)s : %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    filename="/home/rob/git/pyfor/function_based/log/pyfor.log",
                    filemode='a', level=logging.WARNING)

#############
# VARIABLES #
#############
# Used for Cutie menu, not being used now, maybe later
# Major and minor pairs. No exotics at this time
# pairsList = ["EUR/USD", "USD/JPY", "GBP/USD", "USD/CHF", "USD/CAD", "AUD/USD", "NZD/USD", "EUR/GBP", "EUR/AUD",
#              "GBP/JPY", "CHF/JPY", "NZD/JPY", "GBP/CAD"]

# Oanda global variables for use by multiple functions
client = API(access_token=UserVals.key)
acct_sum = accounts.AccountSummary(UserVals.accountID)
u = UserVals()
c = Candles()
s = Strategies(c.get_candles(), u.count)

#############
# FUNCTIONS #
#############


def get_balance():
    """
    Retrieve various information from the AccountSummary call found at https://bit.ly/2E2hoAz
    :return: acct balance
    """
    try:
        client.request(acct_sum)
        balance = float(acct_sum.response.get("account", {}).get("balance"))
        return float(format(balance, '.2f'))
    except Exception:
        logging.exception('Getting account balance failed...')


def check_open_trades():
    acct_deets = accounts.AccountDetails(UserVals.accountID)

    # TRADE TIME CALCULATIONS
    # Correctly gets trade open time
    trade_open_time = client.request(acct_deets).get("account").get("trades")[0].get("openTime")

    # Converts the above string into a useful datetime object
    fixed_trade_time = " ".join(re.split('T|Z|\.', trade_open_time)[:2])
    trade_time_dt = datetime.datetime.strptime(fixed_trade_time, '%Y-%m-%d %H:%M:%S')

    # Gets current UTC time & formats it into useful datetime object
    split_utc = re.split("\.", str(datetime.datetime.utcnow()))
    fixed_utc = "".join(split_utc[0])
    fixed_utc_dt = datetime.datetime.strptime(fixed_utc, '%Y-%m-%d %H:%M:%S')

    """Returns True/False depending how far open trade time is from current
    utc time"""
    compare_times = ((fixed_utc_dt) >= (trade_time_dt +
                     datetime.timedelta(hours=24)))
    ###########################################################################

    # TRADE P/L CALCULATIONS
    profit_loss = float(client.request(acct_deets).get("account").get("trades")
                        [0].get("unrealizedPL"))
    ###########################################################################

    """If the trade is 24 or more hours old and at least $12 profitable close
    75% of the trade."""
    if compare_times is True and profit_loss >= 12:
        open_trade_id = client.request(acct_deets).get("account").get("trades")[0].get('id')
        """ Data is only required if you want to partially close a trade.
        Adding now just in case."""
        units = int(client.request(acct_deets).get("account").get("trades")
                    [0].get('currentUnits'))
        units_to_close = (units * 0.75)
        data = {"units": str(units_to_close)}
        ct = trades.TradeClose(accountID=u.accountID, tradeID=open_trade_id,
                               data=data)
        client.request(ct)
        sleep(5)
        trade()

    # If the trade is positive but low performing close it out in it's entirety
    elif compare_times is True and profit_loss >= 1 and profit_loss < 10:
        open_trade_id = client.request(acct_deets).get("account").get("trades")[0].get('id')
        """Data is only required if you want to partially close a trade.
        Adding now just in case."""
        data = {
            "units": client.request(acct_deets).get("account").get("trades")
            [0].get('currentUnits')
            }
        ct = trades.TradeClose(accountID=u.accountID, tradeID=open_trade_id,
                               data=data)
        client.request(ct)
        sleep(5)
        trade()

    # If the trade is 36 hours old and negative close it out in it's entirety
    elif compare_times is True and profit_loss < 0:
        open_trade_id = client.request(acct_deets).get("account").get("trades")[0].get('id')
        """ Data is only required if you want to partially close a trade.
        Adding now just in case. """
        data = {"units": client.request(acct_deets).get("account").get("trades")[0].get('currentUnits')}
        ct = trades.TradeClose(accountID=u.accountID, tradeID=open_trade_id,
                               data=data)
        client.request(ct)
        sleep(5)
        trade()

    # IF IT DOESN'T MEET THE ABOVE THEN

    else:
        print("Open trade didn't meet any requirements.")
        sleep(60)
        trade()


def check_time():
    # http://bit.ly/2NHitjE

    tz = pytz.timezone('US/Eastern')
    now = datetime.datetime.now(tz)
    year = now.strftime('%Y')
    holidays = [f"{year}-12-25", f"{year}-12-31", f"{year}-12-24", f"{year}-01-01"]

    # If Christmas Eve, Christmas, New Years Eve or New Years Day don't trade.
    if now.strftime('%Y-%m-%d') in holidays:
        print("It's a holiday. No trading today. The app will sleep.")
        sleep(600)
        trade()

    """If it's Friday after 5pm EST, Saturday, or Sunday before 5pm EST then
    the market is closed."""
    elif ((now.weekday() == 5) or (now.weekday() == 4 and now.hour >= 16) or
          (now.weekday() == 6 and now.hour < 17)):
        print("The market is currently closed. The app will sleep.")
        sleep(600)
        trade()
    # Else trade
    else:
        return True


def position_size():
    """
    Calculates the position size before opening a trade based on
    info from Babypips.com http://bit.ly/2Mx11B8

    This should be calculated before each trade is placed and based on current
    account balance.
    :return: position size
    """
    current_balance = get_balance()
    risk_amt = (current_balance * u.risk)
    pip_value = (risk_amt / 50)  # 50 being amt of pips I'm willing to lose.
    position_size = int((pip_value * (10000 / 1)))
    return position_size


def go_long():
    # TODO: refactor this
    params = {"instruments": u.pair}
    r = pricing.PricingInfo(accountID=u.accountID, params=params)
    client.request(r)
    price_list = r.response.get('prices', {})
    price_dict = price_list[0]
    asks = price_dict.get('asks')
    current_asks = asks[0]
    current_ask_price = float(current_asks.get('price'))

    take_profit = (current_ask_price + 0.0050)  # equivalent to 50 pips
    position = position_size()

    try:
        order_data = MarketOrderRequest(instrument=u.pair,
                                        units=position,  # tp.Units(position).value
                                        takeProfitOnFill={
                                            "price": tp.PriceValue(take_profit).value
                                            },
                                        trailingStopLossOnFill={
                                            "distance": "0.00500"
                                            })

        r = orders.OrderCreate(u.accountID, data=order_data.data)
        client.request(r)
        sleep(5)
        trade()
    except Exception:
        print("Placing long order failed, check the logs.")
        logging.exception('Placing long order failed.')


def go_short():
    # TODO: refactor this
    params = {"instruments": u.pair}
    r = pricing.PricingInfo(accountID=u.accountID, params=params)
    client.request(r)
    price_list = r.response.get('prices', {})
    price_dict = price_list[0]
    bids = price_dict.get('bids')
    current_bids = bids[0]
    current_bid_price = float(current_bids.get('price'))

    take_profit = (current_bid_price-0.0050)  # equivalent to 50 pips
    # TODO: Adjust the above and below
    position = position_size()

    try:
        order_data = MarketOrderRequest(instrument=u.pair,
                                        units=-position,  # tp.Units(position).value
                                        takeProfitOnFill={
                                            "price": tp.PriceValue(take_profit).value
                                            },
                                        trailingStopLossOnFill={
                                            "distance": "0.00500"
                                            })

        r = orders.OrderCreate(u.accountID, data=order_data.data)
        client.request(r)
        sleep(5)
        trade()
    except Exception:
        print("Placing short order failed, check the logs.")
        logging.exception('Placing short order failed.')


def trade():
    """
    Checks for a viable trade and if conditions are met it will call the
    appropriate function, else it sleeps for 120 seconds then checks again
    """
    acct_deets = accounts.AccountDetails(UserVals.accountID)
    open_trades = client.request(acct_deets).get("account").get("openTradeCount")

    # While market is open, trade, else sleep
    if check_time() is True and open_trades == 0:
        print("Market is open. Looking for trades.")
        params = {"instruments": u.pair}

        r = pricing.PricingInfo(accountID=u.accountID, params=params)
        client.request(r)  # "rv =" ?
        price_list = r.response.get('prices', {})
        price_dict = price_list[0]

        # CANDLE DATA
        ema_data = s.ema()
        sma_data = s.sma()
        rsi_data = s.rsi()

        # CANDLE DATA CONVERTED TO LISTS ###
        # ema_list = [round(data, 5) for data in ema_data.tolist()]
        # sma_list = [round(data, 5) for data in sma_data.tolist()]
        # rsi_list = [round(data, 5) for data in rsi_data.tolist()]
        close_candle_list = [round(data, 5) for data in c.get_candles().tolist()]

        # If spread is greater than delta move to first set of conditions
        if ((abs(float(price_dict.get('closeoutAsk')) -
             float(price_dict.get('closeoutBid')))) > u.delta):
            print("Delta looks good. Checking other conditions...")
            # If ema > sma and rsi < 50 | Conditions for buy/long
            if (round(ema_data[-1], 5) > round(sma_data[-1], 5) and int(round
               (rsi_data[-1], 0)) < 50):
                print("Conditions for a long trade will be evaluated further.")
                """ Further investigation looks for trend. Last 2 close
                candles should be higher than the previous one."""
                if close_candle_list[-2] < close_candle_list[-1]:
                    go_long()
                else:
                    print("No long trend spotted. Will keep looking")
                    sleep(120)
                    trade()

            # If ema < sma and rsi > 50 | Conditions for short/sell
            elif (round(ema_data[-1], 5) < round(sma_data[-1], 5) and
                    int(round(rsi_data[-1], 0)) > 50):
                print("Conditions for a short trade will be evaluated further.")
                """ Further investigation looks for trend. Last 2 close candles
                should be lower than the previous one."""
                if close_candle_list[-2] > close_candle_list[-1]:
                    go_short()
                else:
                    print("No short trend spotted. Will keep looking")
                    sleep(120)
                    trade()

            # What happens if long or short conditions aren't met?
            else:
                print("""Delta looked good but nothing else did. Will keep
                       looking.""")
                sleep(120)
                trade()
        else:
            print("No potential trades found. Will keep looking.")
            sleep(120)
            trade()

    elif check_time is False:
        print("Market is closed. Will keep checking...")
        sleep(300)  # 5 mins
        trade()

    # Evalutate open trades
    elif open_trades == 1:
        print("Checking open trades...")
        check_open_trades()


if __name__ == "__main__":
    """
    This is for choosing the pair when the app starts as opposed to setting it
    manually in init. I don't want this to be interactive for now.
    u = UserVals()
    print("What pair are you trading today?")
    chosen_pair = pairsList[cutie.select(pairsList)]
    u.pair = chosen_pair.replace("/", "_")
    trade()
    """
    trade()
