"""数据获取模块 - 基于akshare腾讯数据源"""
import akshare as ak
import pandas as pd
import time
from functools import lru_cache

# 股票池 - 按行业分类，共80只
# 格式：(代码, 名称, 行业)
HOT_STOCKS = [
    # 白酒/食品饮料
    ("600519", "贵州茅台"),
    ("000858", "五粮液"),
    ("000568", "泸州老窖"),
    ("600809", "山西汾酒"),
    ("002304", "洋河股份"),
    ("600887", "伊利股份"),
    ("000895", "双汇发展"),
    ("603288", "海天味业"),
    # 银行
    ("601318", "中国平安"),
    ("000001", "平安银行"),
    ("600036", "招商银行"),
    ("601166", "兴业银行"),
    ("601398", "工商银行"),
    ("601288", "农业银行"),
    ("601988", "中国银行"),
    ("601939", "建设银行"),
    # 证券/保险
    ("600030", "中信证券"),
    ("601688", "华泰证券"),
    ("600837", "海通证券"),
    ("601336", "新华保险"),
    ("601601", "中国太保"),
    # 家电
    ("000333", "美的集团"),
    ("000651", "格力电器"),
    ("600690", "海尔智家"),
    ("002032", "苏泊尔"),
    # 医药
    ("600276", "恒瑞医药"),
    ("000538", "云南白药"),
    ("300760", "迈瑞医疗"),
    ("002007", "华兰生物"),
    ("000963", "华东医药"),
    ("600196", "复星医药"),
    # 新能源
    ("002594", "比亚迪"),
    ("300750", "宁德时代"),
    ("601012", "隆基绿能"),
    ("300274", "阳光电源"),
    ("002459", "晶澳科技"),
    ("600438", "通威股份"),
    # 科技/电子
    ("002475", "立讯精密"),
    ("002230", "科大讯飞"),
    ("000725", "京东方A"),
    ("002241", "歌尔股份"),
    ("300433", "蓝思科技"),
    ("600703", "三安光电"),
    # 互联网/传媒
    ("300059", "东方财富"),
    ("002230", "科大讯飞"),
    ("002415", "海康威视"),
    ("002405", "四维图新"),
    # 房地产/建筑
    ("600048", "保利发展"),
    ("000002", "万科A"),
    ("601668", "中国建筑"),
    # 汽车
    ("600104", "上汽集团"),
    ("601238", "广汽集团"),
    ("000625", "长安汽车"),
    # 能源/化工
    ("601857", "中国石油"),
    ("600028", "中国石化"),
    ("601899", "紫金矿业"),
    ("600519", "贵州茅台"),
    ("600900", "长江电力"),
    # 交通运输
    ("600009", "上海机场"),
    ("601111", "中国国航"),
    ("601021", "春秋航空"),
    ("601872", "招商轮船"),
    # 公用事业
    ("600900", "长江电力"),
    ("600886", "国投电力"),
    # 农业
    ("300498", "温氏股份"),
    ("002714", "牧原股份"),
    # 钢铁/有色
    ("600019", "宝钢股份"),
    ("000898", "鞍钢股份"),
    # 零售/消费
    ("002027", "分众传媒"),
    ("601933", "永辉超市"),
    # 机械设备
    ("000333", "美的集团"),
    ("600031", "三一重工"),
]

# 去重
HOT_STOCKS = list(dict.fromkeys(HOT_STOCKS))

# 主要指数
INDICES = [
    ("000001", "上证指数", "sh000001"),
    ("399001", "深证成指", "sz399001"),
    ("399006", "创业板指", "sz399006"),
    ("000300", "沪深300", "sh000300"),
    ("000905", "中证500", "sh000905"),
    ("000852", "中证1000", "sh000852"),
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


def fetch_index_data(symbol: str, start_date: str = "20230101", end_date: str = "20241231") -> pd.DataFrame:
    """获取指数数据"""
    df = ak.stock_zh_a_hist_tx(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        adjust="",
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


def get_index_list() -> list:
    """返回指数列表"""
    return [{"code": c, "name": n, "symbol": s} for c, n, s in INDICES]


if __name__ == "__main__":
    df = fetch_stock_data("000001", "20240101", "20240131")
    print(df.head())
    print(f"共 {len(df)} 条记录")
