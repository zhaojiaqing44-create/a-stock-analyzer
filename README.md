# AI驱动的A股数据分析可视化平台 v2.0

> 一个集**数据可视化、量化回测、AI智能解读**于一体的全栈Web应用

## ✨ v2.0 新增功能

- 📈 **技术指标**：MA、MACD、RSI、KDJ、布林带全套指标
- 📊 **更多市场数据**：6大指数 + 20只热门股 + 市场情绪
- 📉 **增强回测**：短期反转回测 + Fama-MacBeth回归 + 多因子分组回测
- 🤖 **AI增强**：个股分析、市场问答、情绪分析
- ⭐ **自选组合**：自选股管理、实时价格跟踪
- 🎨 **界面美化**：暗色/亮色主题、响应式设计

## 项目亮点

- 📊 **股票K线可视化**：支持20只热门A股，交互式K线图
- 🔄 **短期反转效应回测**：基于学术研究方法，分组构造多空组合
- 🤖 **AI智能解读**：集成大模型API，自动生成市场分析
- 🚀 **技术栈完整**：FastAPI + ECharts + Python量化分析

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.10+, FastAPI, Uvicorn |
| 数据 | akshare (腾讯数据源) |
| 分析 | pandas, numpy |
| 前端 | 原生HTML/CSS/JS, ECharts 5 |
| AI | DeepSeek / OpenAI API (可选) |

## 快速开始

### 方式一：本地运行

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 启动服务

```bash
python main.py
```

3. 访问 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 方式二：云端部署（Render 免费版）

#### 前置准备
- GitHub 账号
- Render 账号（render.com，可用GitHub登录）

#### 步骤

**1. 把项目上传到 GitHub**

在 GitHub 新建仓库，把 `成果` 文件夹里的所有文件 push 上去。

**2. 在 Render 上创建 Web Service**

1. 登录 [render.com](https://render.com)
2. 点击 **New → Web Service**
3. 选择你的 GitHub 仓库
4. 填写配置：

| 配置项 | 值 |
|--------|-----|
| Name | `a-stock-analyzer`（随便起） |
| Region | Singapore（亚洲） |
| Branch | `main` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

5. 点击 **Create Web Service**

**3. 等待部署**

- 大约 3-5 分钟
- 部署成功后会给你一个地址，类似 `https://a-stock-analyzer.onrender.com`
- 直接在浏览器打开就能用

#### 注意事项
- Render 免费版 15 分钟无请求会休眠，首次访问可能等 30 秒
- akshare 在云端可能能正常拉取数据，如果被限流可以切换数据源
- 项目文件已包含 `Procfile`、`requirements.txt`、`runtime.txt`，Render 会自动识别

## 功能说明

### 1. 股票K线图
- 选择股票和日期范围
- 查看K线走势、区间涨跌幅、高低价
- 支持缩放和拖拽

### 2. 短期反转效应回测
**策略逻辑**：
- 每隔 `hold_days` 天调仓
- 按过去 `lookback_days` 天收益率排序
- 分为 `n_groups` 组，做多最差组、做空最好组
- 输出各组累计净值曲线和多空组合夏普比率

**参数说明**：
- 回溯天数：排序用的过去收益窗口
- 持有天数：每次调仓的持有期
- 分组数：组合分组数量

### 3. AI智能解读
- 自动获取股票最新行情数据
- 调用大模型生成专业分析
- 不填API Key时使用本地分析模板

## API文档

启动后访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 查看完整API文档。

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/stocks` | GET | 获取股票列表 |
| `/api/stock/{code}` | GET | 获取K线数据 |
| `/api/backtest` | POST | 执行反转回测 |
| `/api/ai/analyze` | POST | AI个股分析 |

## 项目结构

```
├── main.py              # FastAPI主程序
├── data_fetcher.py      # 数据获取模块
├── backtest.py          # 反转效应回测模块
├── ai_analyzer.py       # AI分析模块
├── static/
│   └── index.html       # 前端页面
└── README.md
```

## 简历描述建议

**项目名称**：AI驱动的A股数据分析与可视化平台

**技术栈**：FastAPI, Python, Pandas, ECharts, LLM API

**项目描述**：
- 基于FastAPI构建RESTful API，实现A股行情数据的自动获取与清洗
- 实现短期反转效应量化回测引擎，支持分组多空组合构造与绩效评估
- 集成大模型API，提供个股AI智能解读功能
- 使用ECharts构建交互式可视化界面，展示K线图与回测净值曲线

## 可扩展方向

- [ ] 接入更多股票池（沪深300/中证500）
- [ ] 添加Fama-MacBeth回归分析
- [ ] 支持用户自定义策略回测
- [ ] 接入更多AI模型（通义千问、文心一言）
- [ ] 部署到云服务器（Render/ Railway）
