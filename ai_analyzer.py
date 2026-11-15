"""AI市场解读模块 - 支持多种LLM API"""
import os
import json
import requests
import random


def get_ai_insight(data_summary: str, api_key: str = None, provider: str = "deepseek") -> str:
    """
    调用大模型生成市场解读
    provider: deepseek, openai, mock
    """
    if not api_key or provider == "mock":
        return mock_insight(data_summary)

    prompt = f"""你是一个专业的A股市场分析师。请根据以下数据生成一段简洁的市场解读（200字以内）：

{data_summary}

要求：
1. 分析当前市场趋势
2. 指出值得关注的板块或个股
3. 给出风险提示
4. 语气专业但易懂"""

    if provider == "deepseek":
        url = "https://api.deepseek.com/v1/chat/completions"
    elif provider == "openai":
        url = "https://api.openai.com/v1/chat/completions"
    else:
        return mock_insight(data_summary)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat" if provider == "deepseek" else "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI接口调用失败: {str(e)}\n\n{mock_insight(data_summary)}"


def mock_insight(data_summary: str) -> str:
    """本地mock解读（无API Key时使用）"""
    insights = [
        "从数据来看，市场近期呈现震荡整理态势。建议关注业绩确定性较强的龙头标的，控制仓位，注意风险。",
        "当前市场情绪偏谨慎，资金在板块间轮动较快。可逢低布局景气度向上的行业，避免追高。",
        "技术面上，指数在关键位置获得支撑，但成交量未能有效放大。短期需观察量能配合情况，中期趋势尚未走坏。",
        "从估值角度看，部分蓝筹股已具备配置价值。建议采用定投或分批建仓策略，分散风险。",
    ]
    return random.choice(insights)


def analyze_stock(code: str, stock_name: str, recent_data: dict, api_key: str = None) -> str:
    """对单只股票进行AI分析"""
    summary = f"""股票：{stock_name}（{code}）
最新收盘价：{recent_data.get('close', 'N/A')}
近5日涨跌幅：{recent_data.get('change_5d', 'N/A')}%
近20日涨跌幅：{recent_data.get('change_20d', 'N/A')}%
成交量变化：{recent_data.get('volume_trend', 'N/A')}"""
    return get_ai_insight(summary, api_key)


def market_sentiment(api_key: str = None) -> dict:
    """市场情绪分析"""
    sentiments = [
        {"score": 0.65, "label": "偏乐观", "desc": "市场情绪偏暖，资金入场意愿较强，但需警惕过热风险。"},
        {"score": 0.45, "label": "中性", "desc": "市场情绪平稳，多空分歧不大，等待方向选择。"},
        {"score": 0.30, "label": "偏悲观", "desc": "市场情绪偏冷，投资者风险偏好下降，建议防御为主。"},
    ]
    s = random.choice(sentiments)
    return {
        "sentiment_score": s["score"],
        "sentiment_label": s["label"],
        "description": s["desc"],
        "indicators": {
            "fear_greed_index": random.randint(20, 80),
            "market_breadth": f"{random.randint(40, 70)}%",
            "turnover_rate": f"{random.uniform(0.5, 2.0):.2f}%",
        }
    }


def ai_chat(question: str, api_key: str = None) -> str:
    """AI市场问答"""
    if not api_key:
        mock_answers = {
            "反转效应": "短期反转效应是指过去表现差的股票在未来短期内反而表现好的现象。学术界通常用组合排序法验证，将股票按过去收益分组，做多输家组合做空赢家组合。",
            "MACD": "MACD是趋势跟踪指标，由DIF线、DEA线和柱状图组成。DIF上穿DEA为金叉买入信号，下穿为死叉卖出信号。",
            "RSI": "RSI相对强弱指标取值0-100，高于70为超买可能回调，低于30为超卖可能反弹。",
        }
        for key, ans in mock_answers.items():
            if key in question:
                return ans
        return "这是一个好问题。建议结合技术指标和基本面综合分析。如需更专业的解答，请配置DeepSeek API Key。"

    prompt = f"作为A股市场专家，请回答以下问题：{question}\n要求：专业、简洁、有数据支撑。"
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI调用失败: {str(e)}"

