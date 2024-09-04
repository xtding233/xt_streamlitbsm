from difflib import get_close_matches

import numpy as np
from scipy.stats import norm
import streamlit as st
from model.bsm import call_price, put_price, d1, d2, standard_normal_cdf, black_scholes_calc
from data.yahoo_finance import YahooFinance
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.title("Black Scholes Calculator")

# creates a horizontal line
st.write("---")

st.header("Enter Option Information")
col1, col2 = st.columns(2, gap = 'small')
with col1:
    try:
        ticker = st.text_input(label='Stock symbol', value='AAPL')
        prev_ticker = ticker
    except ValueError:
        ticker = st.text_input(label='Stock symbol', value=prev_ticker)
    yf = YahooFinance(ticker)
    pricing_date = st.date_input('Pricing date',
                                 value=yf.available_hist_date()[-1], max_value=datetime.now())

    S0_ = yf.get_stock_price(pricing_date)
    sigma_ = yf.get_vol(pricing_date, backtrace_year=1)
    col11, col12 = st.columns(2, gap = 'small')
    with col11:
        st.text('Hist Stock price')
        st.text(str(S0_))
        st.text('Hist Volatility')
        st.text(str(sigma_))
    with col12:
        S0 = st.number_input(label="Stock price", value=S0_)
        sigma = st.number_input(label="Volatility", value=sigma_)

with col2:
    # get ticker
    K = st.number_input(label="Strike price", value=S0)
    col21, col22 = st.columns(2, gap = 'small')
    with col21:
        st.text('10yr T-rate')
        rt = yf.get_10yr_treasury_rate()
        st.text(str(rt))
    with col22:
        r = st.number_input(label="Risk-Free rate", value=rt)
    T = st.number_input(label="Time to option expiration", value=3 / 12)
    option_type = st.selectbox(
        'Option type',
        ('Call', 'Put'))
    # Run
    # input parameters
    calc = black_scholes_calc(S0, K, r, T, sigma, option_type)

st.header("Results")
expire_date = yf.get_closet_available_date(pricing_date + relativedelta(days=T*365)).strftime('%Y-%m-%d')

st.write(f"Closest Expiration Date = " + str(expire_date))
st.write(f"BSM Option Price ({option_type}) = {calc}".format(option_type=option_type,calc=str(calc)))


st.header('Market Option Price')

option_available_date = yf.option_available_date()
option_available_date = ['<select>'] + list(option_available_date)
default_ix = option_available_date.index(expire_date)
# option_date = st.selectbox(label='Available Option Date',
#                            options=yf.option_available_date(),
#                            index=default_ix)

data = yf.fetch_options_data(expire_date, option_type=option_type)
st.text("Expire Date = " + str(expire_date))
st.dataframe(data, height=500, width=2000)

st.header("Historical Stock Price - " + ticker)
st.line_chart(yf.get_stock_price_history(start=pricing_date+relativedelta(years=-1), end=pricing_date, cols=['Open', 'High', 'Low',
                                                                                                             'Close']))
# with col4:
#     st.header('Step by step calculation')
#
#     d1 = d1(S0, K, r, T, sigma)
#     d2 = d2(S0, K, r, T, sigma)
#     nd1 = norm.cdf(d1)
#     nd2 = norm.cdf(d2)
#     n_d1 = norm.cdf(-d1)
#     n_d2 = norm.cdf(-d2)
#
#     c = nd1 * S0 - nd2 * K * np.exp(-r * T)
#     p = K * np.exp(-r * T) * n_d2 - S0 * n_d1
#
#     st.latex(
#         r'''d_1 = \frac{1}{\sigma\sqrt{T}} \left(\ln\left(\frac{S_0}{K}\right) + \left(r + \frac{\sigma^2}{2}\right)T\right)''')
#     st.write(fr"d_1 = {d1}")
#
#     st.latex(r'''d_2 = d_1 - \sigma\sqrt{T}''')
#     st.write(f"d_2 = {d2}")
#
#     st.latex(r'''c = N(d_1)S_0 - N(d_2)Ke^{-rT}''')
#     st.write(f"Call Option Value (c) = {c}")
#
#     st.latex(r'''p = Ke^{-rT}N(-d_2) - S_0N(-d_1)''')
#     st.write(f"Put Option Value (p) = {p}")

