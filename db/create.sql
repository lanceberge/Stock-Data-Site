-- TODO Foreign Key
CREATE TABLE BalanceSheet (
    filingDate DATE,
    ticker VARCHAR(6) NOT NULL,
    filingPeriod VARCHAR(10) CHECK (filingPeriod IN ('yearly', 'quarterly')),
            cashAndCashEquivalents VARCHAR(50),
            shortTermInvestments VARCHAR(50),
            netReceivables VARCHAR(50), 
            inventory VARCHAR(50),
            otherCurrentAssets VARCHAR(50),
            totalCurrentAssets VARCHAR(50),
            propertyPlantEquipmentNet VARCHAR(50),
            intangibleAssets VARCHAR(50),
            otherNonCurrentLiabilities VARCHAR(50),
            totalNonCurrentLiabilities VARCHAR(50),
            longTermDebt VARCHAR(50),
            accountPayables VARCHAR(50),
            totalLiabilities VARCHAR(50),
            PRIMARY KEY (filingDate, ticker, filingPeriod)
);


CREATE TABLE IncomeStatement (
    filingDate DATE,
    ticker VARCHAR(6) NOT NULL,
    filingPeriod VARCHAR(10) CHECK (filingPeriod IN ('yearly', 'quarterly')),
            revenue VARCHAR(50),
            costOfRevenue VARCHAR(50),
            grossProfit VARCHAR(50),
            grossProfitRatio VARCHAR(50),
            eps VARCHAR(50),
            epsDiluted VARCHAR(50),
            operatingExpenses VARCHAR(50),
            ebitda VARCHAR(50),
            netIncome VARCHAR(50),
            PRIMARY KEY (filingDate, ticker, filingPeriod)
);

CREATE TABLE CashFlowStatement (
    filingDate DATE,
    ticker VARCHAR(6) NOT NULL,
    filingPeriod VARCHAR(10) CHECK (filingPeriod IN ('yearly', 'quarterly')),
            netIncome VARCHAR(50),
            operatingCashFlow VARCHAR(50),
            netCashUsedForInvestingActivites VARCHAR(50),
            freeCashFlow VARCHAR(50),
            PRIMARY KEY (filingDate, ticker, filingPeriod)
);