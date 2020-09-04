class UserVals:
    # int below empty for production runs. set here for testing. otherwise a user entered value.
    count = int(50)  # candle count 50-75 is recommended http://bit.ly/33mY89Y
    granularity = "H4"
    key = ""
    risk = 0.01 # 1% risk
    accountID = ""
    pair = "" # Left empty because it's user entered value
    params = {
        "count": count,
        "granularity": granularity
    }
