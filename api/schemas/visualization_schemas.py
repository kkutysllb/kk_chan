#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据可视化API数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 请求模型
class ChartDataRequest(BaseModel):
    symbol: str = Field(..., description="股票代码")
    chart_type: str = Field(..., description="图表类型")
    timeframe: str = Field(..., description="时间周期")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    indicators: Optional[List[str]] = Field([], description="技术指标列表")
    structures: Optional[List[str]] = Field([], description="缠论结构列表")
    config: Optional[Dict[str, Any]] = Field({}, description="图表配置")

class KLineRequest(BaseModel):
    symbol: str = Field(..., description="股票代码")
    timeframe: str = Field(..., description="时间周期")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    limit: Optional[int] = Field(1000, description="数据点数量限制")
    include_volume: bool = Field(True, description="是否包含成交量")

class TechnicalIndicatorRequest(BaseModel):
    symbol: str = Field(..., description="股票代码")
    indicators: List[str] = Field(..., description="指标列表")
    timeframe: str = Field(..., description="时间周期")
    periods: Optional[Dict[str, Any]] = Field({}, description="指标参数")

# 响应模型
class ChartDataResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any] = {}
    chart_type: str
    symbol: str
    timeframe: str
    timestamp: datetime = Field(default_factory=datetime.now)

class KLineChartResponse(BaseModel):
    success: bool = True
    symbol: str
    timeframe: str
    data: Dict[str, Any] = {}
    data_points: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)

class TechnicalIndicatorResponse(BaseModel):
    success: bool = True
    symbol: str
    timeframe: str
    indicators: List[str]
    data: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)

class StructureOverlayResponse(BaseModel):
    success: bool = True
    symbol: str
    timeframe: str
    structures: List[str]
    overlay_data: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)

class HeatmapDataResponse(BaseModel):
    success: bool = True
    market: str
    metric: str
    timeframe: str
    data: List[Dict[str, Any]] = []
    chart_config: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)