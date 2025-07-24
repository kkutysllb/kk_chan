# -*- coding: utf-8 -*-
"""
Qlib量化核心模块
包含基础的数据处理、策略框架和回测引擎
基于Microsoft Qlib框架重构
"""

try:
    from .data_adapter import QlibDataAdapter
    from .portfolio_manager_qlib import QlibPortfolioManager
    from .strategy_base_qlib import QlibStrategyBase
    from .backtest_engine_qlib import QlibBacktestEngine
except ImportError as e:
    print(f"警告: 部分核心模块导入失败: {e}")

__all__ = [
    'QlibDataAdapter',
    'QlibPortfolioManager',
    'QlibStrategyBase',
    'QlibBacktestEngine'
]