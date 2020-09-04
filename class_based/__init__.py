class UserVals:
    # int below empty for production runs. set here for testing. otherwise a user entered value.
    count = int(50)  # candle count 50-75 is recommended http://bit.ly/33mY89Y
    granularity = "H4"
    key = "31baca4f6148e7489920aeff23c0921e-49b676bc6896eecd4f9ce6b438ccc6bd"
    risk = 0.01 # 1% risk
    accountID = "101-001-7200076-004"
    pair = "" # Left empty because it's user entered value
    params = {
        "count": count,
        "granularity": granularity
    }
