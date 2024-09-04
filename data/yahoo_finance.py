import yfinance as yf
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
from click import option
import pandas as pd

class YahooFinance:
    def __init__(self, ticker, years_back_trace=10):
        self.ticker = ticker
        self.yf_api = yf.Ticker(self.ticker)
        self.hist = None
        self.years_back_trace = years_back_trace
        test_data = self.yf_api.history(period='5d', interval='1d')
        if (len(test_data) == 0):
            raise NameError("Incorrect stock ticker")

    def available_hist_date(self):
        return self.yf_api.history().index

    def get_stock_price(self, dt : datetime = datetime.now(), col = 'Close'):
        is_found = False
        time_back = 0
        while not is_found:
            try:
                data = self.yf_api.history(start=dt + timedelta(days=-time_back), end=dt + timedelta(days=1))[col][0]
                is_found = True
            except:
                time_back += 1
        return data

    def get_stock_price_history(self, start : datetime, end : datetime.now(), cols=['Close']):
        return self.yf_api.history(start=start, end=end)[cols]

    def fetch_options_data(self, dt, option_type='ALL'):
        options_data = self.yf_api.option_chain(date=dt)
        calls = pd.DataFrame(options_data.calls)
        puts = pd.DataFrame(options_data.puts)
        calls['Option Type'] = 'Call'
        puts['Option Type'] = 'Put'
        if option_type == 'ALL':
            return pd.concat([calls, puts])
        elif option_type.upper() == 'CALL':
            return calls
        elif option_type.upper() == 'PUT':
            return puts
        else:
            return pd.concat([calls, puts])

    def option_available_date(self):
        return self.yf_api.options

    def get_closet_available_date(self, dt : datetime):
        option_available_date = self.option_available_date()
        lst_dt = [datetime.strptime(x, r'%Y-%m-%d') for x in option_available_date]
        lst_dt = np.sort(lst_dt)
        for i in range(len(lst_dt)-1):
            if lst_dt[i].date() < (dt + timedelta(days=1)):
                continue
            else:
                return lst_dt[i].date()
        return dt

    def get_vol(self, dt, col = 'Close'):
        data = self.yf_api.history(start=dt+relativedelta(years=-self.years_back_trace), end=dt)[col].pct_change()

        # Calculate daily returns
        #data['Daily_Return'] = data['Adj Close'].pct_change()

        # std of daily returns
        daily_volatility = data.std()
        annualized_volatility = daily_volatility * np.sqrt(252)

        return annualized_volatility
        #return self.yf_api.history(start=dt+relativedelta(years=-backtrace_year), end=dt)[col].std()

    def get_10yr_treasury_rate(self):
        # 10 year treasury ticker symbol
        treasury_ticker = "^TNX"

        now = datetime.now()
        ten_years_ago = now.replace(year=now.year - 10)

        treasury_data = yf.download(treasury_ticker, start=ten_years_ago, end=now)
        last_yield = treasury_data['Close'].iloc[-1]
        return last_yield / 100

    def get_risk_free_rate(self):
        return self.get_10yr_treasury_rate()