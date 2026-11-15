"""FastAPI后端服务"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import pandas as pd
import os

from data_fetcher import fetch_stock_data, get_stock_list
from backtest import reversal_backtest, single_stock_reversal
from ai_analyzer import analyze_stock, mock_insight

app = FastAPI(title="AI驱动的A股数据分析平台", version="1.0.0")


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
    stocks = get_stock_list()
    return [{"code": c, "name": n} for c, n in stocks]


@app.get("/api/stock/{code}")
def stock_data(code: str, start_date: str = "20230101", end_date: str = "20241231"):
    """获取单只股票K线数据"""
    try:
        df = fetch_stock_data(code, start_date, end_date)
        if df.empty:
            raise HTTPException(status_code=404, detail="无数据")
        return {
            "code": code,
            "dates": df["date"].dt.strftime("%Y-%m-%d").tolist(),
            "open": df["open"].tolist(),
            "close": df["close"].tolist(),
            "high": df["high"].tolist(),
            "low": df["low"].tolist(),
            "volume": df["volume"].tolist(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/backtest")
def backtest(req: BacktestRequest):
    """反转效应回测"""
    codes = req.codes or ["000001", "600519", "000858", "601318", "600036"]
    result = reversal_backtest(
        codes=codes,
        start_date=req.start_date,
        end_date=req.end_date,
        lookback_days=req.lookback_days,
        hold_days=req.hold_days,
        n_groups=req.n_groups,
    )
    return result


@app.post("/api/ai/analyze")
def ai_analyze(req: AIAnalyzeRequest):
    """AI个股分析"""
    try:
        # 获取最新数据
        df = fetch_stock_data(req.code, "20240101", "20241231")
        if df.empty or len(df) < 20:
            return {"insight": mock_insight(f"{req.stock_name} 数据不足")}

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


@app.get("/")
def root():
    # 尝试多个可能的路径，兼容Render和本地
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html"),
        os.path.join(os.getcwd(), "static", "index.html"),
        "/opt/render/project/src/static/index.html",
    ]
    for html_path in candidates:
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                return HTMLResponse(f.read())
    # 调试：返回查找过的路径
    return HTMLResponse(f"<h1>index.html 未找到</h1><p>已搜索路径：</p><pre>{chr(10).join(candidates)}</pre><p>请查看 /docs 获取API文档</p>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
