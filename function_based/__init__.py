class UserVals:
    """Fill empty strings with your acct info"""
    count = int(20)
    granularity = "H1"
    key = ""
    risk = 0.02  # 2% risk
    accountID = ""
    pair = "EUR_USD"  # Leave empty for user entered value
    delta = float(0.00013)  # aka spread
    params = {
        "count": count,
        "granularity": granularity
    }
