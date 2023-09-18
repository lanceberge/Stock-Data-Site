from flask import Flask, render_template, request, g
import requests
import json
from datetime import datetime, date
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
    g.db_table_name = "BalanceSheet"

    g.column_names = [
        "cashAndCashEquivalents",
        "shortTermInvestments",
        "netReceivables",
        "inventory",
        "otherCurrentAssets",
        "totalCurrentAssets",
        "propertyPlantEquipmentNet",
        "intangibleAssets",
        "otherNonCurrentLiabilities",
        "totalNonCurrentLiabilities",
        "longTermDebt",
        "accountPayables",
        "totalLiabilities"
    ]

    return_data = table_from_api_endpoint("balance-sheet-statement")
    return json.dumps(return_data)


@app.route("/income_statement")
def income_statement():
    g.db_table_name = "IncomeStatement"

    g.column_names = [
        "revenue",
        "costOfRevenue",
        "grossProfit",
        "grossProfitRatio",
        "operatingExpenses",
        "ebitda",
        "netIncome",
        "eps",
        "epsdiluted",
    ]

    thousands_bases = {
        "grossProfitRatio": 1,
        "eps":  1,
        "epsdiluted": 1
    }

    return_map = table_from_api_endpoint("income-statement", thousands_bases)
    return json.dumps(return_map)


@app.route("/cash_flow")
def cash_flow():
    g.db_table_name = "CashFlowStatement"

    g.column_names = [
        "netIncome",
        "operatingCashFlow",
        "netCashUsedForInvestingActivites",
        "freeCashFlow"
    ]
    
    return_map = table_from_api_endpoint("cash-flow-statement")
    return json.dumps(return_map)


def table_from_api_endpoint(api_endpoint_name, thousands_bases=None):
    g.ticker = request.args.get("ticker")
    g.period = request.args.get("period")

    query_columns = ["filingDate"] + g.column_names
    query_filters = f"WHERE filingPeriod='{g.period}' AND ticker='{g.ticker}' ORDER BY filingDate DESC LIMIT 5"
    db_data = select_from_table(g.db_table_name, query_columns, query_filters)

    # compute the number of entries needed to pull from the api
    most_recent_db_date = None

    api_entries_to_retrieve = 5
    if len(db_data) != 0:
        most_recent_db_date = datetime.strptime(db_data[0]["filingDate"], '%Y-%m-%d')
        todays_date = date.today()

        months_per_period = 3 if g.period == "monthly" else 12

        monthly_difference = get_month_difference(most_recent_db_date, todays_date)
        api_entries_to_retrieve = monthly_difference % months_per_period if monthly_difference >= months_per_period else 0
        
        if most_recent_db_date.month % months_per_period != 0:
            api_entries_to_retrieve += 1

    api_data = []
    if api_entries_to_retrieve > 0:
        api_data = retrieve_from_api(api_endpoint_name, g.ticker, args=[f"limit={api_entries_to_retrieve}", f"period={g.period}"])

        # rename date to filingDate
        for row in api_data:
            row['filingDate'] = row.pop('date')
        
        # if a date was pulled from the api that is already in the database
        oldest_api_date = datetime.strptime(api_data[-1]['filingDate'], '%Y-%m-%d')
        if most_recent_db_date and get_month_difference(most_recent_db_date, oldest_api_date) == 0:
            del api_data[-1]

        # set this as the data to be inserted into the database
        g.data = api_data
    
    # join db and api_data, then format them
    unformatted_data = db_data + api_data

    return_map = {}

    first_value = unformatted_data[-1][g.column_names[0]]
    default_thousands_base = get_thousands_base(first_value) - 1
    return_map["Base"] = default_thousands_base

    formatted_data = format_data(unformatted_data, thousands_bases, default_thousands_base)

    return_map["Data"] = formatted_data
    g.thousands_base = default_thousands_base

    return return_map


def format_data(data, thousands_bases, default_thousands_base):
    return_data = []
    
    for column in data:
        return_data_column = {}

        filingDate = column["filingDate"].split("-")
        month, year = filingDate[1], filingDate[0][-2:]
        return_data_column["filingDate"] = month + "/" + year

        for column_name in g.column_names:
            thousands_base = default_thousands_base
            if thousands_bases and column_name in thousands_bases:
                thousands_base = thousands_bases[column_name]

            return_data_column[column_name] = millify(column[column_name], thousands_base, include_suffix=False)

        return_data.insert(0, return_data_column)

    return return_data


@app.after_request
def after_request(response):
    included_endpoints = {"/balance_sheet", "/income_statement", "/cash_flow"}

    if request.path in included_endpoints:
        for row in g.data:
            column_names = ['filingDate', 'ticker', 'filingPeriod'] + g.column_names
            row['ticker'] = g.ticker
            row['filingPeriod'] = g.period
            values = [row[column_name] for column_name in column_names]
            insert_into_table(column_names, values, g.db_table_name)

    return response


@app.route("/")
def index():
    return render_template("index.html")


def get_month_difference(d1, d2):
    diff = (d2.year - d1.year) * 12 + (d2.month - d1.month)
    
    return diff if diff >= 0 else -diff


if __name__ == "__main__":
    app.run(debug=True)
