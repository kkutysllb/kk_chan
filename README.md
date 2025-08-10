# KK缠论量化分析平台

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Vue3](https://img.shields.io/badge/Vue3-3.3+-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-5.0+-green.svg)](https://www.mongodb.com/)

> 基于缠论理论的专业股票技术分析平台

## 项目概述

KK缠论量化分析平台是一个完整的股票技术分析系统，基于缠中说禅的缠论理论，提供专业的多周期技术分析功能和智能选股服务。

### 核心特性

- ✅ **缠论分析**：分型识别、笔段构造、中枢分析
- ✅ **多周期联立**：5分钟、30分钟、日线多级别分析  
- ✅ **交易信号**：买卖点自动识别和质量评估
- ✅ **智能选股**：基于MACD背驰的多级别选股策略
- ✅ **可视化展示**：基于ECharts的专业图表展示
- ✅ **前后端分离**：Vue3前端 + FastAPI后端

## 系统架构

```
                                                            
   Vue3 前端            FastAPI 后端            数据层      
                                                              
┌─ ECharts图表   ◄──── ┌─ api/main.py     ◄──── ┌─ MongoDB      
├─ Element UI         ├─ api/routers.py         ├─ 股票数据      
└─ 响应式布局         └─ api/chan_api_v2.py    └─ 本地存储    
                                                            
                                                         
                                 ▲                        ▼
                                  │                        │
                                                               
                          缠论分析引擎          MongoDB        
                          选股策略模块          本地数据库       
                                                               
```

## 功能实现状态

### 后端核心

#### 缠论引擎 (`chan_theory_v2/`)
- [x] **多周期数据获取** - 5分钟、30分钟、日线数据
- [x] **结构分析** - 分型识别、笔段构造
- [x] **中枢识别** - 中枢构造和延伸判断
- [x] **多周期联立** - 多级别走势分析
- [x] **交易信号** - 买卖点自动识别
- [x] **背驰分析** - MACD背驰识别与评分

#### 选股策略 (`chan_theory_v2/strategies/`)
- [x] **背驰选股** - 基于MACD背驰的选股策略
- [x] **信号评分** - 综合评分和信号强度判断
- [x] **关键价位** - 入场价、止损价和止盈价计算

#### API接口 (`api/`)
- [x] **FastAPI应用** - 标准FastAPI应用结构
- [x] **数据标准化** - ECharts兼容格式
- [x] **前端API** - 完整的JSON数据输出
- [x] **股票列表** - 动态股票代码获取
- [x] **参数配置** - 灵活的分析参数设置
- [x] **选股服务** - 智能选股API接口
- [x] **文档生成** - 自动生成API文档

### 前端界面

#### Vue3前端 (`frontend/`)
- [x] **分析页面** - 单股票多周期分析
- [x] **选股页面** - 智能选股结果展示
- [x] **图表集成** - ECharts专业图表
- [x] **响应式设计** - 适配不同设备

## 最新进展

### 智能选股功能完成 ✅

成功实现了基于MACD背驰的智能选股功能，支持多级别联立分析：

#### 功能特点
1. **30分钟底背驰筛选** - 识别中期趋势反转机会
2. **5分钟买点确认** - 通过短期买点信号确认入场时机
3. **信号评分系统** - 基于背驰可靠度、MACD金叉和信号类型的综合评分
4. **关键价位计算** - 自动计算入场价、止损价和止盈价

#### 技术实现
- 实现了 `SimpleBackchiStockSelector` 类用于执行选股策略
- 开发了 `StockSelectionPage.vue` 前端页面展示选股结果
- 通过 `api/` 模块提供了标准FastAPI选股接口
- 支持保守、平衡、激进三种预设配置

#### 选股结果示例
```
# 选股结果统计
✅ 筛选股票: 3600+ 只
✅ 信号总数: 120+ 个
✅ 强信号: 25+ 个
✅ 中等信号: 45+ 个
✅ 弱信号: 50+ 个
```

## 快速开始

### 环境要求

- Python 3.8+
- MongoDB 5.0+
- Node.js 16+ (用于前端开发)

### 安装依赖

```bash
# Python依赖
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 运行系统

```bash
# 启动后端API服务
cd api
python main.py

# 或者在项目根目录使用uvicorn启动
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端开发服务器
cd frontend
npm run dev

# 执行选股（可选）
python daily_stock_selection.py
```

> **注意**: 如果遇到模块导入错误，请确保在项目根目录(`kk_chan/`)执行uvicorn命令

### API服务访问

启动后端API服务后，可以通过以下地址访问：

- **服务地址**: http://localhost:8000
- **API文档**: http://localhost:8000/docs (Swagger UI)
- **API备用文档**: http://localhost:8000/redoc (ReDoc)
- **健康检查**: http://localhost:8000/health

### 数据库检查

```bash
# 检查数据库连接和集合
python database/quick_db_check.py

# 检查K线数据质量
python check_data_quality.py
```

## 项目结构

```
kk_chan/
├── api/                        # FastAPI后端服务
│   ├── main.py                 # FastAPI应用入口
│   ├── routers.py              # API路由定义
│   └── chan_api_v2.py          # 缠论分析API实现
├── chan_theory_v2/             # 缠论分析核心 v2
│   ├── core/                   # 核心引擎
│   │   ├── chan_engine.py      # 缠论分析引擎
│   │   ├── kline_processor.py  # K线处理器
│   │   └── trading_calendar.py # 交易日历
│   ├── models/                 # 数据模型
│   │   ├── kline.py            # K线模型
│   │   ├── fenxing.py          # 分型模型
│   │   ├── bi.py               # 笔模型
│   │   ├── seg.py              # 线段模型
│   │   ├── zhongshu.py         # 中枢模型
│   │   ├── simple_backchi.py   # 简化背驰模型
│   │   └── enums.py            # 枚举定义
│   └── strategies/             # 策略模块
│       └── backchi_stock_selector.py # 背驰选股策略
├── database/                   # 数据库模块
│   ├── db_handler.py           # 本地数据库处理器
│   └── check_kline_collections.py # 数据检查
├── frontend/                   # Vue3前端
│   ├── src/                    # 源代码
│   │   ├── components/         # 组件
│   │   ├── views/              # 页面
│   │   │   ├── AnalysisPage.vue # 分析页面
│   │   │   └── StockSelectionPage.vue # 选股页面
│   │   └── utils/              # 工具
│   │       └── api.js          # API调用
│   └── package.json            # 依赖配置
├── daily_stock_selection.py    # 每日选股脚本
└── README.md
```

## 开发计划

### 近期目标
- [ ] 集成Qlib量化框架

## 技术栈

### 后端
- **Python 3.8+** - 核心分析引擎
- **FastAPI** - Web API框架
- **MongoDB** - 数据存储
- **pandas** - 数据处理
- **NumPy** - 数值计算
- **TA-Lib** - 技术分析库

### 前端
- **Vue3** - 现代前端框架
- **ECharts** - 专业图表库
- **Element Plus** - UI组件库
- **Axios** - HTTP客户端
- **Vite** - 前端构建工具

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 相关文档

项目包含以下相关文档：

- `docs/缠论系统优化完善技术方案.md` - 系统优化技术方案
- `docs/INSTALL_TALIB.md` - TA-Lib安装指南
- `qlib_quantitative/README_QLIB_QUICKSTART.md` - Qlib快速入门

---

**注意**：本项目仅用于技术研究和学习交流，不构成投资建议。股市有风险，投资需谨慎。