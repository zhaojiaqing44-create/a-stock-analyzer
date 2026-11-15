"""技术指标计算模块"""
import pandas as pd
import numpy as np


def calc_ma(close: pd.Series, window: int) -> pd.Series:
    """移动平均线"""
    return close.rolling(window=window).mean()


def calc_ema(close: pd.Series, window: int) -> pd.Series:
    """指数移动平均线"""
    return close.ewm(span=window, adjust=False).mean()


def calc_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD指标"""
    ema_fast = calc_ema(close, fast)
    ema_slow = calc_ema(close, slow)
    dif = ema_fast - ema_slow
    dea = calc_ema(dif, signal)
    macd_hist = (dif - dea) * 2
    return dif, dea, macd_hist


def calc_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """RSI相对强弱指标"""
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calc_kdj(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 9, m1: int = 3, m2: int = 3):
    """KDJ随机指标"""
    lowest_low = low.rolling(window=n).min()
    highest_high = high.rolling(window=n).max()
    rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
    k = rsv.ewm(com=m1 - 1, adjust=False).mean()
    d = k.ewm(com=m2 - 1, adjust=False).mean()
    j = 3 * k - 2 * d
    return k, d, j


def calc_boll(close: pd.Series, window: int = 20, num_std: int = 2):
    """布林带"""
    mid = close.rolling(window=window).mean()
    std = close.rolling(window=window).std()
    upper = mid + num_std * std
    lower = mid - num_std * std
    return upper, mid, lower


def calc_all_indicators(df: pd.DataFrame) -> dict:
    """计算所有技术指标"""
    close = df["close"]
    high = df["high"]
    low = df["low"]

    dif, dea, macd_hist = calc_macd(close)
    k, d, j = calc_kdj(high, low, close)
    upper, mid, lower = calc_boll(close)

    return {
        "ma5": calc_ma(close, 5).tolist(),
        "ma10": calc_ma(close, 10).tolist(),
        "ma20": calc_ma(close, 20).tolist(),
        "ma60": calc_ma(close, 60).tolist(),
        "dif": dif.tolist(),
        "dea": dea.tolist(),
        "macd": macd_hist.tolist(),
        "rsi": calc_rsi(close).tolist(),
        "k": k.tolist(),
        "d": d.tolist(),
        "j": j.tolist(),
        "boll_upper": upper.tolist(),
        "boll_mid": mid.tolist(),
        "boll_lower": lower.tolist(),
    }
