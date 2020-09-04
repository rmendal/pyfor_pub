class UserVals:
    """20 here because only using close and it's faster than...candle count
    50-75 is recommended http://bit.ly/33mY89Y"""
    count = int(20)
    granularity = "H1"
    key = "3df254039c4fbe0aa6fdb5f096619c72-f4f00b53f651666b48336e6a35b1580f"
    risk = 0.02  # 2% risk
    accountID = "101-001-7200076-001"
    pair = "EUR_USD"  # Leave empty for user entered value
    delta = float(0.00013)  # aka spread
    params = {
        "count": count,
        "granularity": granularity
    }
