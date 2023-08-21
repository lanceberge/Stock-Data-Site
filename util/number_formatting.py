import math


millnames = ["", "", "M", "B", "T"]


def get_thousands_base(n):
    n = float(n)

    return max(0, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3)))


def millify(n, thousands_base=None, include_suffix=True, accounting_style=True):
    n = float(n)

    if not thousands_base:
        thousands_base = get_thousands_base(n)

    if thousands_base > 1:
        n = n / 10 ** (3 * thousands_base)

    # return the string with no decimals if the number doesn't have any
    millnames_idx = min(thousands_base, len(millnames) - 1)

    rstring = two_decimals(n)
    
    if accounting_style and n < 0:
        rstring = "({})".format(rstring[1:])

    if include_suffix:
        rstring = rstring + " " + millnames[millnames_idx]

    return rstring


def percentify(n):
    return two_decimals(n)+"%"


def two_decimals(n):
    return "{:,.2f}".format(n).rstrip('0').rstrip('.')
