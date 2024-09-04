from math import sqrt, log, pow, erf, e
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import norm

def standard_normal_cdf(x):
    return 0.5 * (1 + erf(x / sqrt(2)))

def d1(S, K, t, r, vol):
    numerator = log(S/K) + (r + pow(vol, 2)/2) * t
    denominator = vol * sqrt(t)
    return numerator / denominator

def d2(S, K, t, r, vol):
    return d1(S, K, t, r, vol) - vol * sqrt(t)

def call_price(S, K, t, r, vol):
    Nd1 = standard_normal_cdf(d1(S, K, t, r, vol))
    Nd2 = standard_normal_cdf(d2(S, K, t, r, vol))
    return Nd1 * S - Nd2 * K * pow(e, -1 * r * t)

def put_price(S, K, t, r, vol):
    Nd1 = standard_normal_cdf(- 1 * d1(S, K, t, r, vol))
    Nd2 = standard_normal_cdf(- 1 * d2(S, K, t, r, vol))
    return Nd2 * K * pow(e, -1 * r * t) - S * Nd1