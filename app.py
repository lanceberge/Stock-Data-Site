from flask import Flask, render_template, request, g
import sqlite3
import requests
import json
from util.number_formatting import *
from util.database_management import *

app = Flask(__name__)
base_url = "https://financialmodelingprep.com/api/v3/"
api_key = None
with open(".api_key", "r") as f:
    api_key = f.read()


# TODO error handling for empty data or erroneous response
def retrieve_from_api(metric, ticker, args=None):
    url = f"{base_url}{metric}/{ticker}?apikey={api_key}"

    if args:
        args = "&".join(args)
        url = f"{base_url}{metric}/{ticker}?{args}&apikey={api_key}"

    data = requests.get(url)
    data_dict = json.loads(data.text)
    return data_dict


@app.route("/key_statistics")
def key_statistics():
    ticker = request.args.get("ticker")
    
    # TODO profit margins, EPS, FCF
    price_data = retrieve_from_api("quote-short", ticker)[0]
    ttm_data = retrieve_from_api("key-metrics-ttm", ticker)[0]
    market_cap_data = retrieve_from_api("market-capitalization", ticker)[0]

    data = {}
    data["price"] = millify(price_data["price"])
    data["enterpriseValueOverEBITDATTM"] = millify(ttm_data["enterpriseValueOverEBITDATTM"], accounting_style=False)
    data["peRatioTTM"] = two_decimals(ttm_data["peRatioTTM"])
    data["pbRatioTTM"] = two_decimals(ttm_data["pbRatioTTM"])
    data["priceToSalesRatioTTM"] = two_decimals(ttm_data["priceToSalesRatioTTM"])
    data["roicTTM"] = percentify(ttm_data["roicTTM"])
    data["dividendYieldTTM"] = percentify(ttm_data["dividendYieldTTM"])
    data["payoutRatioTTM"] = percentify(ttm_data["payoutRatioTTM"])
    data["marketCap"] = millify(market_cap_data["marketCap"], include_suffix=True)

    g.ticker = ticker
    g.data = data

    return_map = {}
    return_map["Data"] = [data]
    return json.dumps(return_map)


@app.route("/balance_sheet")
def balance_sheet():
    g.ticker = request.args.get("ticker")
    g.period = request.args.get("period")
    
    # TODO identify the number of periods needed based on the most recent date in the db
    api_data = retrieve_from_api("balance-sheet-statement", g.ticker, args=["limit=5", f"period={g.period}"])

    first_value = api_data[-1]["cashAndCashEquivalents"]
    g.thousands_base = get_thousands_base(first_value) - 1
    
    format_function = lambda n: millify(
        n, g.thousands_base, include_suffix=False)

    api_ids_to_keep = [
        ("cashAndCashEquivalents", format_function),
        ("shortTermInvestments", format_function),
        ("netReceivables", format_function),
        ("inventory", format_function),
        ("otherCurrentAssets", format_function),
        ("totalCurrentAssets", format_function),
        ("propertyPlantEquipmentNet", format_function),
        ("intangibleAssets", format_function),
        ("otherNonCurrentLiabilities", format_function),
        ("totalNonCurrentLiabilities", format_function),
        ("longTermDebt", format_function),
        ("accountPayables", format_function),
        ("totalLiabilities", format_function)
    ]

    return_data = table_from_api_data(api_ids_to_keep, api_data)
    return json.dumps(return_data)


@app.route("/income_statement")
def income_statement():
    g.ticker = request.args.get("ticker")
    g.period = request.args.get("period")
    api_data = retrieve_from_api("income-statement", g.ticker, args=["limit=5", f"period={g.period}"])

    first_value = api_data[-1]["revenue"]
    g.thousands_base = get_thousands_base(first_value) - 1
    
    format_function = lambda n: millify(
        n, g.thousands_base, include_suffix=False)

    format_function_base_1 = lambda n: millify(
        n, 1, include_suffix=False)

    # TODO gross profit ratio
    api_data_ids = [
        ("revenue", format_function),
        ("costOfRevenue", format_function),
        ("grossProfit", format_function),
        ("operatingExpenses", format_function),
        ("ebitda", format_function),
        ("netIncome", format_function),
        ("eps",  format_function_base_1),
        ("epsdiluted", format_function_base_1)
    ]

    return_map = table_from_api_data(api_data_ids, api_data)

    return json.dumps(return_map)


@app.route("/cash_flow")
def cash_flow():
    g.ticker = request.args.get("ticker")
    g.period = request.args.get("period")
    api_data = retrieve_from_api("cash-flow-statement", g.ticker, args=["limit=5", f"period={g.period}"])

    first_value = api_data[-1]["netIncome"]
    g.thousands_base = get_thousands_base(first_value) - 1
    
    format_function = lambda n: millify(
        n, g.thousands_base, include_suffix=False)
    
    api_data_ids = [
        ("netIncome", format_function),
        ("operatingCashFlow", format_function),
        ("netCashUsedForInvestingActivites", format_function),
        ("freeCashFlow", format_function)
    ]
    
    return_map = table_from_api_data(api_data_ids, api_data)
    return json.dumps(return_map)


# TODO refactor to allow different format_functions
# TODO move request.args.get stuff into here
def table_from_api_data(api_ids_and_format_functions, api_data):
    return_map = {}
    return_map["Base"] = g.thousands_base

    return_data = []
    for api_data_column in api_data:
        return_data_column = {}

        date = api_data_column["date"].split("-")
        month, year = date[1], date[0][-2:]
        return_data_column["filingDate"] = month + "/" + year

        for row_name, format_function in api_ids_and_format_functions:
            return_data_column[row_name] = format_function(api_data_column[row_name])

        return_data.insert(0, return_data_column)

    return_map["Data"] = return_data
    g.data = return_map["Data"]

    return return_map


@app.after_request
def after_request(response):
    def after_balance_sheet():
        for row in g.data:
            row['base'] = g.thousands_base
            row['ticker'] = g.ticker
            row['filingPeriod'] = g.period
            # insert_into_database(row, 'BalanceSheet')

    request_to_function_map = {"/balance_sheet": after_balance_sheet}

    if request.path in request_to_function_map:
        request_to_function_map[request.path]()

    return response


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
