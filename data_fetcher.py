"""数据获取模块 - 基于akshare腾讯数据源"""
import akshare as ak
import pandas as pd
import time
from functools import lru_cache

# 热门股票列表（代码, 名称）
HOT_STOCKS = [
    ("600519", "贵州茅台"),
    ("000858", "五粮液"),
    ("601318", "中国平安"),
    ("000001", "平安银行"),
    ("600036", "招商银行"),
    ("000333", "美的集团"),
    ("600276", "恒瑞医药"),
    ("601888", "中国中免"),
    ("002594", "比亚迪"),
    ("300750", "宁德时代"),
    ("600030", "中信证券"),
    ("601166", "兴业银行"),
    ("000651", "格力电器"),
    ("600887", "伊利股份"),
    ("002475", "立讯精密"),
    ("601012", "隆基绿能"),
    ("000725", "京东方A"),
    ("600009", "上海机场"),
    ("601899", "紫金矿业"),
    ("002230", "科大讯飞"),
]


def code_to_txsymbol(code: str) -> str:
    """将6位股票代码转为腾讯接口格式"""
    code = code.strip()
    if code.startswith(("6", "9")):
        return f"sh{code}"
    return f"sz{code}"


def fetch_stock_data(code: str, start_date: str = "20230101", end_date: str = "20241231") -> pd.DataFrame:
    """获取单只股票日线数据（前复权）"""
    symbol = code_to_txsymbol(code)
    df = ak.stock_zh_a_hist_tx(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        adjust="qfq",
    )
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def fetch_multi_stocks(codes: list, start_date: str, end_date: str) -> dict:
    """批量获取多只股票数据，带延迟避免限流"""
    result = {}
    for code in codes:
        try:
            df = fetch_stock_data(code, start_date, end_date)
            if not df.empty:
                result[code] = df
        except Exception as e:
            print(f"获取 {code} 失败: {e}")
        time.sleep(0.3)
    return result


def get_stock_list() -> list:
    """返回股票列表"""
    return HOT_STOCKS


if __name__ == "__main__":
    df = fetch_stock_data("000001", "20240101", "20240131")
    print(df.head())
    print(f"共 {len(df)} 条记录")
