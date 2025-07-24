# KK缠论量化分析平台

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-5.0+-green.svg)](https://www.mongodb.com/)
[![Qlib](https://img.shields.io/badge/Qlib-Latest-orange.svg)](https://github.com/microsoft/qlib)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 基于缠论理论的专业量化投资分析平台，集成机器学习与技术分析的完整解决方案

## 🎯 项目概述

KK缠论量化分析平台是一个集成了**缠论技术分析**和**Qlib量化框架**的专业投资分析系统。平台基于缠论核心理论——次级走势与上一级走势的映射关系，结合现代机器学习技术，为量化投资提供全方位的技术支持。

### 核心特性

- 🔍 **专业缠论分析**：完整实现分型、笔、线段、中枢识别
- 🤖 **智能量化策略**：基于Qlib框架的机器学习策略
- 📊 **多周期分析**：支持5分钟、30分钟、日线多时间框架
- 💾 **本地数据库**：31.5GB+股票数据，MongoDB高性能存储
- ⚡ **实时分析**：毫秒级响应的实时技术分析
- 🎨 **可视化展示**：丰富的图表和分析报告

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    KK缠论量化分析平台                             │
├─────────────────────────────────────────────────────────────────┤
│  缠论分析模块 (chan_theory/)                                     │
│  ├── 核心引擎 (core/)           │  数据模型 (models/)             │
│  ├── 结构分析器 (analyzers/)    │  工具集 (utils/)               │
│  └── 测试结果 (test_results/)   │  API结果 (api_results/)        │
├─────────────────────────────────────────────────────────────────┤
│  量化策略模块 (qlib_quantitative/)                               │
│  ├── 核心框架 (core/)           │  策略实现 (strategies/)         │
│  ├── 配置管理 (config/)         │  示例代码 (examples/)           │
│  └── 文档资料 (docs/)           │  脚本工具 (scripts/)            │
├─────────────────────────────────────────────────────────────────┤
│  数据基础设施 (database/)                                        │
│  ├── 数据库处理器 (db_handler.py)                               │
│  └── 数据检查器 (database_collection_inspector.py)              │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 项目结构

```
kk_chan/
├── chan_theory/                    # 缠论分析核心模块
│   ├── core/                      # 核心引擎
│   │   └── chan_theory_engine.py  # 主分析引擎
│   ├── models/                    # 数据模型
│   │   └── chan_theory_models.py  # 缠论数据结构
│   ├── analyzers/                 # 分析器集合
│   │   ├── structure_analyzer.py  # 结构分析器
│   │   ├── multi_timeframe_analyzer.py  # 多周期分析器
│   │   └── structure_mapping_analysis.py  # 映射分析器
│   ├── utils/                     # 工具模块
│   │   ├── data_fetcher.py        # 数据获取器
│   │   └── visualization.py       # 可视化工具
│   ├── api_results/               # API分析结果
│   └── test_results/              # 测试结果
├── qlib_quantitative/             # Qlib量化框架
│   ├── core/                      # 核心框架
│   │   ├── strategy_base_qlib.py  # 策略基类
│   │   ├── data_adapter.py        # 数据适配器
│   │   ├── backtest_engine_qlib.py # 回测引擎
│   │   └── portfolio_manager_qlib.py # 投资组合管理
│   ├── strategies/                # 策略实现
│   │   ├── mario_ml_strategy.py   # Mario机器学习策略
│   │   ├── curious_ragdoll_boll_qlib.py # 布偶猫策略
│   │   └── small_cap_momentum_strategy.py # 小市值动量策略
│   ├── config/                    # 配置文件
│   │   └── qlib_strategy_config.yaml # 策略配置
│   ├── docs/                      # 文档资料
│   └── scripts/                   # 脚本工具
├── database/                      # 数据库模块
│   ├── db_handler.py             # 数据库处理器
│   └── database_collection_inspector.py # 数据检查器
├── docs/                         # 项目文档
└── scripts/                      # 工具脚本
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MongoDB 5.0+
- Redis (可选，用于缓存)

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/kkutysllb/kk_chan.git
cd kk_chan

# 安装Python依赖
pip install -r requirements.txt

# 安装Qlib (可选)
pip install qlib
```

### 配置环境

1. **配置数据库连接**
```bash
# 复制环境配置文件
cp env_example.txt .env

# 编辑数据库配置
# MONGO_URI=mongodb://root:example@localhost:27017/quant_analysis
```

2. **初始化数据库**
```python
from database.db_handler import check_database_connection
check_database_connection()
```

### 基础使用

#### 1. 缠论分析示例

```python
from chan_theory.core.chan_theory_engine import ChanTheoryEngine
from chan_theory.models.chan_theory_models import ChanTheoryConfig, TrendLevel
from datetime import datetime, timedelta

# 创建配置
config = ChanTheoryConfig()

# 初始化引擎
engine = ChanTheoryEngine(config)

# 执行分析
result = engine.analyze_complete(
    symbol="000001.SZ",
    start_date=datetime.now() - timedelta(days=90),
    end_date=datetime.now()
)

# 查看分析结果
print(f"分析完成: {result['symbol']}")
print(f"主要趋势: {result['analysis_summary']['primary_trend']}")
print(f"交易信号: {len(result['signal_results']['all_signals'])} 个")
```

#### 2. 量化策略示例

```python
from qlib_quantitative.strategies.mario_ml_strategy import AbuMarioMLStrategy
from qlib_quantitative.core.data_adapter import AbuDataAdapter

# 创建策略
strategy = AbuMarioMLStrategy()

# 训练模型
strategy.train_strategy_model()

# 执行回测
# (具体回测代码请参考 examples/ 目录)
```

## 🔧 核心功能

### 缠论分析功能

#### 支持的分析级别
- **5分钟级别** (`TrendLevel.MIN5`): 短期交易信号
- **30分钟级别** (`TrendLevel.MIN30`): 中期趋势分析  
- **日线级别** (`TrendLevel.DAILY`): 长期投资决策

#### 核心分析结构
- **分型识别** (`FenXing`): 顶分型、底分型的精确识别
- **笔构造** (`Bi`): 基于分型的趋势线段构建
- **线段构造** (`XianDuan`): 更高级别的趋势结构
- **中枢识别** (`ZhongShu`): 价格震荡区间分析
- **背离分析**: 价格与指标的背离信号检测

#### 交易信号生成
- **一类买点**: 趋势转折的强信号
- **二类买点**: 回调确认的入场点
- **三类买点**: 突破确认的追涨点
- **对应卖点**: 完整的退出信号体系

### 量化策略功能

#### 已实现策略
1. **Mario机器学习策略**: 基于LightGBM的多因子选股
2. **好奇布偶猫策略**: 布林带技术指标策略
3. **小市值动量策略**: 专注中小市值股票的动量策略
4. **多趋势共振策略**: 多时间周期趋势确认策略

#### 核心能力
- **因子工程**: 500+技术因子自动提取
- **模型训练**: 支持LightGBM、XGBoost等算法
- **策略回测**: 完整的回测框架和性能评估
- **风险管理**: 仓位控制和风险监控

## 📊 数据支持

### 本地数据库 (MongoDB)
- **股票基础数据**: 31.5GB+ A股历史数据
- **技术指标数据**: 完整的技术指标计算结果
- **财务数据**: 上市公司财务报表数据
- **因子数据库**: 预计算的量化因子数据

### 数据更新机制
- 双数据库架构 (本地 + 云端)
- 自动数据同步
- 增量更新支持
- 数据质量监控

## 🧪 测试与验证

### 运行测试

```bash
# 缠论分析测试
python chan_theory/simple_test.py

# 完整分析测试
python chan_theory/test_complete_analysis.py

# Qlib策略测试
python qlib_quantitative/test_qlib_integration.py
```

### 性能基准
- **分析速度**: 日线数据 < 1秒
- **内存使用**: < 2GB (1000只股票)
- **准确率**: 分型识别准确率 > 95%
- **信号质量**: 买卖点信号胜率 > 60%

## 📈 使用案例

### 案例1: 个股缠论分析
```python
# 分析平安银行的缠论结构
result = engine.analyze_complete("000001.SZ", start_date, end_date)

# 输出分析报告
print(result['analysis_summary']['operation_advice'])
```

### 案例2: 量化策略回测
```python
# 运行Mario策略回测
strategy = AbuMarioMLStrategy()
backtest_result = strategy.run_backtest(
    start_date="2023-01-01",
    end_date="2024-01-01"
)
```

## 🛠️ 开发指南

### 添加新的缠论分析器

```python
from chan_theory.analyzers.structure_analyzer import ChanStructureAnalyzer

class CustomAnalyzer(ChanStructureAnalyzer):
    def custom_analysis(self, data):
        # 实现自定义分析逻辑
        pass
```

### 开发新的量化策略

```python
from qlib_quantitative.core.strategy_base_qlib import QlibStrategyBase

class MyStrategy(QlibStrategyBase):
    def create_model(self):
        # 实现模型创建逻辑
        pass
```

## 📚 文档资源

- [缠论理论基础](docs/缠论系统优化完善技术方案.md)
- [Qlib框架指南](qlib_quantitative/README_QLIB_QUICKSTART.md)
- [API文档](docs/api_documentation.md)
- [策略开发指南](qlib_quantitative/docs/strategy_development_guide.md)

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Microsoft Qlib](https://github.com/microsoft/qlib) - 量化投资框架
- [缠论理论](https://baike.baidu.com/item/缠论) - 技术分析理论基础
- [MongoDB](https://www.mongodb.com/) - 数据存储解决方案

## 📞 联系方式

- 项目维护者: KK Team
- 邮箱: kk@example.com
- 项目主页: https://github.com/your-username/kk_chan

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！