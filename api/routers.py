#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由定义
直接使用现有的chan_api_v2业务逻辑
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入现有的缠论分析模块
from api.chan_api_v2 import ChanDataAPIv2

# 初始化缠论API（使用现有业务逻辑）
chan_api = ChanDataAPIv2()

# 创建路由实例
router = APIRouter()

# 请求模型
class AnalysisRequest(BaseModel):
    symbol: str
    timeframe: str = "daily"
    days: int = 90
    min_bi_length: Optional[int] = 5
    min_xd_bi_count: Optional[int] = 3
    fenxing_threshold: Optional[float] = 0.001

class StockInfo(BaseModel):
    value: str
    label: str
    name: str

class StockSelectionRequest(BaseModel):
    max_results: int = 50
    custom_config: Optional[Dict[str, Any]] = None

class StockSelectionConfigRequest(BaseModel):
    config: Dict[str, Any]

# ==================== 基础接口 ====================

@router.get("/")
async def root():
    """根路径"""
    return {
        "message": "KK缠论分析API服务",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ==================== 股票接口 ====================

@router.get("/stocks", response_model=List[StockInfo])
async def get_stocks(query: str = Query("", description="搜索关键字")):
    """获取股票列表"""
    return chan_api.get_symbols_list(query)

# ==================== 分析接口 ====================

@router.get("/analysis")
async def get_analysis(
    symbol: str = Query(..., description="股票代码"),
    timeframe: str = Query("daily", description="时间级别"),
    days: int = Query(90, description="分析天数")
):
    """获取缠论分析数据"""
    return chan_api.analyze_symbol_complete(symbol, timeframe, days, "complete")

@router.post("/analysis")
async def post_analysis(request: AnalysisRequest):
    """POST方式获取缠论分析数据"""
    return chan_api.analyze_symbol_complete(request.symbol, request.timeframe, request.days, "complete")

@router.get("/analysis/multi-level")
async def get_multi_level_analysis(
    symbol: str = Query(..., description="股票代码"),
    levels: str = Query("daily,30min,5min", description="分析级别，逗号分隔"),
    days: int = Query(90, description="分析天数")
):
    """获取多级别缠论分析数据"""
    level_list = [level.strip() for level in levels.split(",")]
    return chan_api.analyze_multi_level(symbol, level_list, days)

@router.post("/analysis/save")
async def save_analysis(data: Dict[str, Any]):
    """保存分析结果"""
    return chan_api.save_analysis_result(data)

@router.get("/analysis/history")
async def get_analysis_history():
    """获取历史分析记录"""
    return chan_api.get_analysis_history()

# ==================== 选股接口 ====================

@router.get("/stock-selection")
async def get_stock_selection(
    max_results: int = Query(50, description="最大返回结果数量"),
    min_backchi_strength: Optional[float] = Query(None, description="最小背驰强度阈值"),
    min_area_ratio: Optional[float] = Query(None, description="绿柱面积比阈值"),
    max_area_shrink_ratio: Optional[float] = Query(None, description="红柱面积缩小比例"),
    confirm_days: Optional[int] = Query(None, description="金叉确认天数"),
    death_cross_confirm_days: Optional[int] = Query(None, description="死叉确认天数")
):
    """执行缠论多级别背驰选股"""
    custom_config = {}
    if min_backchi_strength is not None:
        custom_config['min_backchi_strength'] = min_backchi_strength
    if min_area_ratio is not None:
        custom_config['min_area_ratio'] = min_area_ratio
    if max_area_shrink_ratio is not None:
        custom_config['max_area_shrink_ratio'] = max_area_shrink_ratio
    if confirm_days is not None:
        custom_config['confirm_days'] = confirm_days
    if death_cross_confirm_days is not None:
        custom_config['death_cross_confirm_days'] = death_cross_confirm_days
    
    return chan_api.run_stock_selection(max_results, custom_config if custom_config else None)

@router.post("/stock-selection")
async def post_stock_selection(request: StockSelectionRequest):
    """POST方式执行缠论多级别背驰选股"""
    return chan_api.run_stock_selection(request.max_results, request.custom_config)

@router.get("/stock-selection/config")
async def get_stock_selection_config():
    """获取当前选股配置"""
    return chan_api.get_stock_selection_config()

@router.put("/stock-selection/config")
async def update_stock_selection_config(request: StockSelectionConfigRequest):
    """更新选股配置"""
    result = chan_api.update_stock_selection_config(request.config)
    if not result.get('success', False):
        raise HTTPException(status_code=400, detail=result.get('message', '配置更新失败'))
    return result

@router.get("/stock-selection/history")
async def get_stock_selection_history(limit: int = Query(20, description="返回记录数量限制")):
    """获取选股历史记录"""
    return chan_api.get_stock_selection_history(limit)