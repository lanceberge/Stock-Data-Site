import math


# TODO return thousands_base

millnames = ["", "", "M", "B", "T"]


def get_thousands_base(n):
    n = float(n)

    return max(0, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3)))


def millify(n, thousands_base=None, include_suffix=True):
    n = float(n)

    if not thousands_base:
        thousands_base = get_thousands_base(n)

    if thousands_base > 1:
        n = n / 10 ** (3 * thousands_base)

    # return the string with no decimals if the number doesn't have any
    millnames_idx = min(thousands_base, len(millnames) - 1)

    rstring = None
    if n.is_integer():
        rstring =  "{:,.0f}".format(n)

    else:
        rstring = "{:,.2f}".format(n)

    if include_suffix:
        return rstring.append(millnames[millnames_idx])

    return rstring


def percentify(n):
    return "{:.2f}%".format(n * 100)


def two_decimals(n):
    return "{:.2f}".format(n)
