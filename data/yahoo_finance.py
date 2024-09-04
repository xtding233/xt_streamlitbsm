import yfinance as yf
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from click import option
import pandas as pd

class YahooFinance:
    def __init__(self, ticker):
        self.ticker = ticker
        self.yf_api = yf.Ticker(self.ticker)
        self.hist = None

    def available_hist_date(self):
        return self.yf_api.history().index

    def get_stock_price(self, dt : datetime = datetime.now(), col = 'Close'):
        data = self.yf_api.history(start=dt, end=dt + timedelta(days=1))[col]
        if len(data) == 0:
            data = self.yf_api.history(start=dt+timedelta(days=-1), end=dt + timedelta(days=1))[col]
            if len(data) == 0:
                data = self.yf_api.history(start=dt + timedelta(days=-2), end=dt + timedelta(days=1))[col]
        return data[0]

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

    def option_availble_date(self):
        return self.yf_api.options

    def get_vol(self, dt, backtrace_year=1, col = 'Close'):
        return self.yf_api.history(start=dt+relativedelta(years=-backtrace_year), end=dt)[col].std()