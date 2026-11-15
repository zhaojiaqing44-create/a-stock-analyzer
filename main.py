"""FastAPI主服务 v2.0"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import (
    fetch_stock_data, get_stock_list, get_index_list, fetch_index_data,
)
from backtest import reversal_backtest
from ai_analyzer import get_ai_insight, analyze_stock, market_sentiment, ai_chat, mock_insight
from indicators import calc_all_indicators
from fama_macbeth import fama_macbeth_regression, multi_factor_backtest

app = FastAPI(title="AI驱动的A股数据分析平台", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class BacktestRequest(BaseModel):
    codes: list = None
    start_date: str = "20230101"
    end_date: str = "20241231"
    lookback_days: int = 5
    hold_days: int = 5
    n_groups: int = 5


class AIAnalyzeRequest(BaseModel):
    code: str
    stock_name: str = ""
    api_key: str = ""
    provider: str = "mock"


@app.get("/api/stocks")
def stock_list():
    """获取股票列表"""
    return [{"code": c, "name": n} for c, n in get_stock_list()]


@app.get("/api/indices")
def index_list():
    """获取指数列表"""
    return get_index_list()


@app.get("/api/stock/{code}")
def stock_data(code: str, start_date: str = "20230101", end_date: str = "20241231"):
    """获取股票K线数据 + 技术指标"""
    try:
        df = fetch_stock_data(code, start_date, end_date)
        if df.empty:
            raise HTTPException(status_code=404, detail="无数据")

        indicators = calc_all_indicators(df)

        return {
            "code": code,
            "dates": df["date"].dt.strftime("%Y-%m-%d").tolist(),
            "open": df["open"].tolist(),
            "close": df["close"].tolist(),
            "high": df["high"].tolist(),
            "low": df["low"].tolist(),
            "volume": df["volume"].tolist(),
            "amount": df.get("amount", pd.Series()).tolist() if "amount" in df.columns else [],
            "indicators": indicators,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/index/{symbol}")
def index_data(symbol: str, start_date: str = "20230101", end_date: str = "20241231"):
    """获取指数数据"""
    try:
        df = fetch_index_data(symbol, start_date, end_date)
        return {
            "symbol": symbol,
            "dates": df["date"].dt.strftime("%Y-%m-%d").tolist(),
            "close": df["close"].tolist(),
            "volume": df["volume"].tolist(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/backtest")
def backtest(req: BacktestRequest):
    """短期反转效应回测"""
    codes = req.codes or [c for c, _ in get_stock_list()]
    result = reversal_backtest(
        codes=codes,
        start_date=req.start_date,
        end_date=req.end_date,
        lookback_days=req.lookback_days,
        hold_days=req.hold_days,
        n_groups=req.n_groups,
    )
    return result


@app.get("/api/fama-macbeth")
def fama_macbeth(start_date: str = "20230101", end_date: str = "20241231", lookback: int = 5):
    """Fama-MacBeth截面回归"""
    try:
        codes = [c for c, _ in get_stock_list()]
        result = fama_macbeth_regression(codes, start_date, end_date, lookback)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/multi-factor")
def multi_factor(start_date: str = "20230101", end_date: str = "20241231", hold_days: int = 5):
    """多因子分组回测"""
    try:
        codes = [c for c, _ in get_stock_list()]
        result = multi_factor_backtest(codes, start_date, end_date, ["reversal", "momentum", "volatility"], hold_days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/analyze")
def ai_analyze(req: AIAnalyzeRequest):
    """AI个股分析"""
    try:
        df = fetch_stock_data(req.code, "20240101", "20241231")
        if df.empty or len(df) < 20:
            return {"insight": mock_insight(f"{req.stock_name} 数据不足"), "data": {}}

        close = df["close"].iloc[-1]
        change_5d = (df["close"].iloc[-1] / df["close"].iloc[-6] - 1) * 100 if len(df) >= 6 else 0
        change_20d = (df["close"].iloc[-1] / df["close"].iloc[-21] - 1) * 100 if len(df) >= 21 else 0
        vol_recent = df["volume"].iloc[-5:].mean()
        vol_prev = df["volume"].iloc[-10:-5].mean()
        vol_trend = "放量" if vol_recent > vol_prev * 1.1 else ("缩量" if vol_recent < vol_prev * 0.9 else "持平")

        recent_data = {
            "close": round(close, 2),
            "change_5d": round(change_5d, 2),
            "change_20d": round(change_20d, 2),
            "volume_trend": vol_trend,
        }
        insight = analyze_stock(req.code, req.stock_name, recent_data, req.api_key or None)
        return {"insight": insight, "data": recent_data}
    except Exception as e:
        return {"insight": f"分析失败: {str(e)}", "data": {}}


@app.get("/api/ai/sentiment")
def sentiment():
    """市场情绪分析"""
    return market_sentiment()


@app.post("/api/ai/chat")
def chat_endpoint(data: dict):
    """AI市场问答"""
    question = data.get("question", "")
    api_key = data.get("api_key", "") or None
    answer = ai_chat(question, api_key)
    return {"answer": answer}


@app.get("/")
def root():
    candidates = [
        os.path.join(os.getcwd(), "index.html"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"),
        "/opt/render/project/src/index.html",
        os.path.join(os.getcwd(), "static", "index.html"),
        "/opt/render/project/src/static/index.html",
    ]
    for html_path in candidates:
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                return HTMLResponse(f.read())
    return HTMLResponse("<h1>index.html 未找到</h1>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
