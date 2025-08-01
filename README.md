# KK缠论量化分析平台

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Vue3](https://img.shields.io/badge/Vue3-3.3+-green.svg)](https://vuejs.org/)
[![Electron](https://img.shields.io/badge/Electron-27+-blue.svg)](https://www.electronjs.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-5.0+-green.svg)](https://www.mongodb.com/)

> 基于缠论理论的专业股票技术分析平台

## 项目概述

KK缠论量化分析平台是一个完整的股票技术分析系统，基于缠中说禅的缠论理论，提供专业的多周期技术分析功能。

### 核心特性

- ✅ **缠论分析**：分型识别、笔段构造、中枢分析
- ✅ **多周期联立**：5分钟、30分钟、日线多级别分析  
- ✅ **交易信号**：买卖点自动识别和质量评估
- ✅ **可视化展示**：基于ECharts的专业图表展示
- ✅ **桌面应用**：Vue3 + Electron桌面客户端

## 系统架构

```
                                                            
   Vue3 前端            Python API            数据层      
                                                              
┌─ ECharts图表   ◄──── ┌─ chan_api.py    ◄──── ┌─ MongoDB      
├─ Element UI         ├─ JSON数据格式        ├─ 股票数据      
└─ 响应式布局         └─ 多周期分析          └─ 实时更新    
                                                            
                                                         
                                 ▲                        ▼
                                  │                        │
                                                               
                            Electron            MongoDB        
                            桌面客户端         数据存储       
                                                               
```

## 功能实现状态

### 后端核心

#### 缠论引擎 (`chan_theory/`)
- [x] **多周期数据获取** - 5分钟、30分钟、日线数据
- [x] **结构分析** - 分型识别、笔段构造
- [x] **中枢识别** - 中枢构造和延伸判断
- [x] **多周期联立** - 多级别走势分析
- [x] **交易信号** - 买卖点自动识别

#### API接口 (`chan_api.py`)
- [x] **数据标准化** - ECharts兼容格式
- [x] **前端API** - 完整的JSON数据输出
- [x] **股票列表** - 动态股票代码获取
- [x] **参数配置** - 灵活的分析参数设置

### 前端界面

#### 桌面GUI (`desktop_gui/`)
- [x] **PyQt6界面** - 基础桌面应用框架
- [x] **图表集成** - matplotlib图表显示
- [x] **中文字体** - 完整的中文显示支持

## 最新进展

### 2025-07-28 数据传递问题修复 ✅

经过详细调试，成功解决了可视化数据传递的关键问题：

#### 修复内容
1. **TrendLevel枚举导入问题** - 统一所有模块使用绝对导入
2. **数据格式转换错误** - 修复分型、笔段、中枢数据格式化方法
3. **前端API数据访问** - 解决键值不匹配导致的数据获取失败

#### 技术细节
- 修复了 `chan_theory_engine.py` 中的双导入路径问题
- 修复了 `data_fetcher.py`、`structure_analyzer.py` 等模块的导入不一致
- 完善了 `_format_fenxing_for_viz`、`_format_bi_for_viz`、`_format_zhongshu_for_viz` 方法
- 确保 `VisualizationData` 正确传递多周期K线数据

#### 验证结果
```bash
# 测试结果示例 (000001.SZ 日线30天)
✅ K线数据: 21 条
✅ 分型数据: 1 个  
✅ 笔段数据: 0 个
✅ 中枢数据: 0 个
✅ 交易信号: 7 个
✅ JSON文件: frontend_data_000001.SZ_daily_20250728_231111.json
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

# 前端依赖 (如果使用Vue版本)
cd frontend
npm install
```

### 运行测试

```bash
# 测试缠论分析引擎
python debug_data_conversion.py

# 生成前端JSON数据
python chan_api.py --symbol 000001.SZ --timeframe daily --days 30

# 运行桌面GUI
python desktop_gui/main.py
```

## 项目结构

```
kk_chan/
├── chan_theory/                 # 缠论分析核心
│   ├── core/                   # 核心引擎
│   │   └── chan_theory_engine.py
│   ├── models/                 # 数据模型
│   │   └── chan_theory_models.py
│   ├── analyzers/              # 分析器
│   │   ├── structure_analyzer.py
│   │   └── multi_timeframe_analyzer.py
│   └── utils/                  # 工具类
│       ├── data_fetcher.py
│       └── visualization.py
├── desktop_gui/                # 桌面GUI
│   ├── main.py                # 主程序入口
│   └── components/            # UI组件
├── frontend/                   # Vue3前端 (开发中)
├── chan_api.py                # 前端API接口
└── README.md
```

## 开发计划

### 近期目标 (Q3 2025)
- [ ] 完成Vue3前端界面开发
- [ ] 实现Electron桌面打包
- [ ] 增加更多技术指标集成
- [ ] 优化图表交互体验

### 中期目标 (Q4 2025)  
- [ ] 实时数据流更新
- [ ] 策略回测功能
- [ ] 多股票组合分析
- [ ] 云端数据同步

## 技术栈

### 后端
- **Python 3.8+** - 核心分析引擎
- **MongoDB** - 数据存储
- **pandas** - 数据处理
- **NumPy** - 数值计算

### 前端
- **Vue3** - 现代前端框架
- **ECharts** - 专业图表库
- **Element Plus** - UI组件库
- **Electron** - 桌面应用打包

### 桌面GUI
- **PyQt6** - Python GUI框架
- **matplotlib** - 图表绘制
- **中文字体支持** - 完整显示

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者：[你的姓名]
- 邮箱：[你的邮箱]
- 项目链接：[GitHub仓库地址]

---

**注意**：本项目仅用于技术研究和学习交流，不构成投资建议。股市有风险，投资需谨慎。