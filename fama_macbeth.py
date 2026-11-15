"""Fama-MacBeth回归模块"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from data_fetcher import fetch_multi_stocks


def fama_macbeth_regression(
    codes: list,
    start_date: str,
    end_date: str,
    lookback_days: int = 5,
) -> dict:
    """
    Fama-MacBeth两步回归：
    第一步：每个时间截面，用过去收益对未来收益做截面回归
    第二步：对系数序列取均值和t统计量
    """
    stock_data = fetch_multi_stocks(codes, start_date, end_date)
    if len(stock_data) < 10:
        return {"error": f"股票数量不足（需要>=10只，当前{len(stock_data)}只）"}

    # 构建收益率矩阵
    returns_dict = {}
    for code, df in stock_data.items():
        df = df.copy()
        df["ret"] = df["close"].pct_change()
        returns_dict[code] = df.set_index("date")["ret"]

    returns_df = pd.DataFrame(returns_dict)
    returns_df = returns_df.dropna(how="all")

    # 计算过去收益和未来收益
    past_ret = returns_df.rolling(window=lookback_days).sum()
    future_ret = returns_df.shift(-lookback_days).rolling(window=lookback_days).sum()

    # 截面回归
    dates = returns_df.index
    betas = []

    for i in range(lookback_days, len(dates) - lookback_days):
        dt = dates[i]
        x = past_ret.loc[dt].dropna()
        y = future_ret.loc[dt].dropna()

        common = x.index.intersection(y.index)
        if len(common) < 10:
            continue

        x = x[common].values
        y = y[common].values
        x = sm.add_constant(x)

        try:
            model = sm.OLS(y, x).fit()
            betas.append(model.params[1])  # 斜率系数
        except Exception:
            continue

    if not betas:
        return {"error": "回归样本不足"}

    betas = np.array(betas)
    mean_beta = float(np.mean(betas))
    t_stat = float(mean_beta / (np.std(betas, ddof=1) / np.sqrt(len(betas))))
    from scipy import stats as scipy_stats

    return {
        "n_observations": len(betas),
        "mean_beta": mean_beta,
        "t_statistic": t_stat,
        "p_value": float(2 * (1 - scipy_stats.t.cdf(abs(t_stat), len(betas) - 1))),
        "is_significant": abs(t_stat) > 1.96,
        "interpretation": (
            f"过去{lookback_days}日收益对未来{lookback_days}日收益的截面回归系数为 {mean_beta:.4f}，"
            f"t统计量为 {t_stat:.2f}，"
            f"{'显著' if abs(t_stat) > 1.96 else '不显著'}。"
            f"系数为负说明存在短期反转效应。"
        ),
    }


def multi_factor_backtest(
    codes: list,
    start_date: str,
    end_date: str,
    factors: list = None,
    hold_days: int = 5,
) -> dict:
    """
    多因子分组回测
    factors: 可用因子 ['momentum', 'reversal', 'volatility', 'turnover']
    """
    from scipy import stats as scipy_stats

    stock_data = fetch_multi_stocks(codes, start_date, end_date)
    if len(stock_data) < 5:
        return {"error": f"股票数量不足"}

    returns_dict = {}
    for code, df in stock_data.items():
        df = df.copy()
        df["ret"] = df["close"].pct_change()
        df["vol"] = df["close"].rolling(20).std()
        returns_dict[code] = df.set_index("date")

    returns_df = pd.DataFrame({k: v["ret"] for k, v in returns_dict.items()})
    vol_df = pd.DataFrame({k: v["vol"] for k, v in returns_dict.items()})

    dates = returns_df.index
    factor_returns = {f: [] for f in factors}

    for i in range(20, len(dates) - hold_days, hold_days):
        dt = dates[i]
        end_dt = dates[min(i + hold_days, len(dates) - 1)]

        # 各因子的排序信号
        signals = {}
        if "reversal" in factors:
            signals["reversal"] = returns_df.loc[:dt].tail(5).sum()
        if "momentum" in factors:
            signals["momentum"] = returns_df.loc[:dt].tail(20).sum()
        if "volatility" in factors:
            signals["volatility"] = vol_df.loc[dt]
        if "turnover" in factors:
            signals["turnover"] = returns_df.loc[:dt].tail(5).abs().sum()

        hold_ret = returns_df.loc[dt:end_dt].sum()

        for factor, sig in signals.items():
            sig = sig.dropna()
            if len(sig) < 5:
                continue
            ranks = sig.rank(pct=True)
            losers = ranks[ranks < 0.3].index
            winners = ranks[ranks > 0.7].index
            if len(losers) > 0 and len(winners) > 0:
                if factor in ("reversal", "volatility"):
                    ret = hold_ret[losers].mean() - hold_ret[winners].mean()
                else:
                    ret = hold_ret[winners].mean() - hold_ret[losers].mean()
                factor_returns[factor].append(float(ret))

    result = {"factors": {}}
    for factor, rets in factor_returns.items():
        if rets:
            arr = np.array(rets)
            result["factors"][factor] = {
                "mean_return": float(np.mean(arr)),
                "t_stat": float(np.mean(arr) / (np.std(arr) / np.sqrt(len(arr)))),
                "sharpe": float(np.mean(arr) / np.std(arr) * np.sqrt(252 / hold_days)) if np.std(arr) > 0 else 0,
                "n_periods": len(arr),
            }

    return result
