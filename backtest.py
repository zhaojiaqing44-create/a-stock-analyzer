"""反转效应回测模块"""
import pandas as pd
import numpy as np
from data_fetcher import fetch_multi_stocks


def calc_returns(df: pd.DataFrame) -> pd.Series:
    """计算日收益率"""
    return df["close"].pct_change()


def reversal_backtest(
    codes: list,
    start_date: str,
    end_date: str,
    lookback_days: int = 5,
    hold_days: int = 5,
    n_groups: int = 5,
) -> dict:
    """
    短期反转效应回测：
    - 每持有期结束时，按过去lookback_days收益率排序
    - 分组构造多空组合，计算各组收益
    """
    # 获取所有股票数据
    stock_data = fetch_multi_stocks(codes, start_date, end_date)
    if not stock_data:
        return {"error": "无法获取股票数据"}

    # 构建收益率矩阵
    returns_dict = {}
    for code, df in stock_data.items():
        df = df.copy()
        df["ret"] = calc_returns(df)
        returns_dict[code] = df.set_index("date")["ret"]

    returns_df = pd.DataFrame(returns_dict)
    returns_df = returns_df.dropna(how="all")

    # 构建累计收益率矩阵（用于排序）
    lookback_ret = returns_df.rolling(window=lookback_days).sum()

    # 按持有期取样
    dates = returns_df.index
    group_returns = {i: [] for i in range(1, n_groups + 1)}
    long_short_returns = []
    rebalance_dates = []

    for i in range(lookback_days, len(dates) - hold_days, hold_days):
        sort_date = dates[i]
        end_date_idx = min(i + hold_days, len(dates) - 1)
        end_dt = dates[end_date_idx]

        # 获取排序日的过去收益
        past_ret = lookback_ret.loc[sort_date].dropna()
        if len(past_ret) < n_groups:
            continue

        # 排序分组
        ranks = past_ret.rank(pct=True)
        groups = pd.cut(ranks, bins=n_groups, labels=False) + 1

        # 计算持有期收益
        hold_ret = returns_df.loc[sort_date:end_dt].sum()

        for g in range(1, n_groups + 1):
            group_stocks = groups[groups == g].index
            if len(group_stocks) > 0:
                group_ret = hold_ret[group_stocks].mean()
                group_returns[g].append(group_ret)

        # 多空组合：做多第1组（过去最差），做空第n组（过去最好）
        loser_stocks = groups[groups == 1].index
        winner_stocks = groups[groups == n_groups].index
        if len(loser_stocks) > 0 and len(winner_stocks) > 0:
            ls_ret = hold_ret[loser_stocks].mean() - hold_ret[winner_stocks].mean()
            long_short_returns.append(ls_ret)

        rebalance_dates.append(sort_date.strftime("%Y-%m-%d"))

    # 统计结果
    result = {
        "dates": rebalance_dates,
        "group_mean_returns": {},
        "long_short_returns": long_short_returns,
        "summary": {},
    }

    for g in range(1, n_groups + 1):
        rets = group_returns[g]
        result["group_mean_returns"][f"group_{g}"] = rets
        if rets:
            result["summary"][f"group_{g}_mean"] = float(np.mean(rets))
            result["summary"][f"group_{g}_tstat"] = float(np.mean(rets) / (np.std(rets) / np.sqrt(len(rets)))) if len(rets) > 1 else 0

    if long_short_returns:
        ls_arr = np.array(long_short_returns)
        result["summary"]["long_short_mean"] = float(np.mean(ls_arr))
        result["summary"]["long_short_tstat"] = float(np.mean(ls_arr) / (np.std(ls_arr) / np.sqrt(len(ls_arr)))) if len(ls_arr) > 1 else 0
        result["summary"]["long_short_sharpe"] = float(np.mean(ls_arr) / np.std(ls_arr) * np.sqrt(252 / hold_days)) if np.std(ls_arr) > 0 else 0

    return result


def single_stock_reversal(code: str, start_date: str, end_date: str, lookback_days: int = 5) -> dict:
    """单只股票反转效应分析"""
    from data_fetcher import fetch_stock_data
    df = fetch_stock_data(code, start_date, end_date)
    if df.empty:
        return {"error": "无数据"}

    df["ret"] = df["close"].pct_change()
    df["past_ret"] = df["ret"].rolling(lookback_days).sum()
    df["future_ret"] = df["ret"].shift(-lookback_days)

    df = df.dropna()
    corr = df["past_ret"].corr(df["future_ret"])

    return {
        "dates": df["date"].dt.strftime("%Y-%m-%d").tolist(),
        "past_returns": df["past_ret"].tolist(),
        "future_returns": df["future_ret"].tolist(),
        "correlation": float(corr),
        "message": f"过去{lookback_days}日收益与未来{lookback_days}日收益的相关系数为 {corr:.4f}",
    }
