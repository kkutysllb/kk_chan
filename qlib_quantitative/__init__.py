# -*- coding: utf-8 -*-
"""
Qlib量化分析模块
基于Microsoft Qlib框架的量化交易和投资分析系统

主要功能:
- 数据获取和处理 (基于Qlib数据接口)
- 策略开发和回测 (基于Qlib回测框架)
- 风险管理和分析 (基于Qlib投资组合管理)
- 可视化和报告生成
"""

__version__ = "2.0.0"
__author__ = "KK Stock Backend Team"

# 导入Qlib核心模块
try:
    from .core.data_adapter import QlibDataAdapter
    from .core.portfolio_manager_qlib import QlibPortfolioManager
    from .strategies.curious_ragdoll_boll_qlib import (
        CuriousRagdollBollModel, 
        CuriousRagdollBollStrategy,
        CuriousRagdollBollConfig,
        CuriousRagdollBollBacktester
    )
except ImportError as e:
    print(f"警告: 部分模块导入失败: {e}")

__all__ = [
    'QlibDataAdapter',
    'QlibPortfolioManager',
    'CuriousRagdollBollModel',
    'CuriousRagdollBollStrategy', 
    'CuriousRagdollBollConfig',
    'CuriousRagdollBollBacktester'
]