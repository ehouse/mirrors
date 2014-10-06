def t2s(s):
    """Converts human readable time to seconds.

    :param str s: Human readable time string (ex. 5m or 2h)
    :rtype: int
    :returns: int time converted to seconds
    """
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(s[:-1]) * seconds_per_unit[s[-1]]
