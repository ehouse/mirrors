def t2s(s):
    """Converts human readable time to seconds

    :param s: Human readable time string (ex. 5m or 2h)
    :returns int: Human readable time in seconds
    """
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(s[:-1]) * seconds_per_unit[s[-1]]
