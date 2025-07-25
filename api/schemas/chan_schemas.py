#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论分析API数据模型
定义请求和响应的数据结构
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# 基础枚举
class TrendLevel(str, Enum):
    MIN1 = "1min"
    MIN5 = "5min"
    MIN30 = "30min"
    DAILY = "daily"
    WEEKLY = "weekly"

class FenXingType(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"

class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    SIDEWAYS = "sideways"

class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

# 请求模型
class ChanAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="股票代码")
    timeframes: List[str] = Field(default=["daily"], description="时间周期列表")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    include_ml_prediction: bool = Field(default=True, description="是否包含机器学习预测")
    include_signals: bool = Field(default=True, description="是否生成交易信号")
    force_refresh: bool = Field(default=False, description="是否强制刷新")
    config: Optional[Dict[str, Any]] = Field(None, description="分析配置参数")

class BatchAnalysisRequest(BaseModel):
    symbols: List[str] = Field(..., description="股票代码列表")
    timeframes: List[str] = Field(default=["daily"], description="时间周期列表")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    max_concurrent: Optional[int] = Field(5, description="最大并发数")

class RealTimePredictionRequest(BaseModel):
    symbol: str = Field(..., description="股票代码")
    timeframe: str = Field(default="daily", description="时间周期")
    include_confidence: bool = Field(default=True, description="是否包含置信度")

class MultiTimeframeRequest(BaseModel):
    symbol: str = Field(..., description="股票代码")
    timeframes: List[str] = Field(default=["daily", "30min", "5min"], description="时间周期列表")
    analysis_depth: str = Field(default="standard", description="分析深度")

# 数据模型
class FenXingData(BaseModel):
    id: str
    timestamp: datetime
    price: float
    fenxing_type: FenXingType
    index: int
    strength: float = 0.0
    confidence: float = 0.0
    volume_confirmation: bool = False
    position_in_trend: str = "unknown"
    next_target: Optional[float] = None
    support_resistance: float = 0.0
    ml_probability: float = 0.0
    historical_success_rate: float = 0.0

class BiData(BaseModel):
    id: str
    start_fenxing: FenXingData
    end_fenxing: FenXingData
    direction: TrendDirection
    strength: float = 0.0
    purity: float = 0.0
    duration: int = 0
    price_change: float = 0.0
    price_change_pct: float = 0.0
    volume_confirmation: bool = False
    validity_probability: float = 0.0

class ZhongShuData(BaseModel):
    id: str
    level: TrendLevel
    start_time: datetime
    end_time: datetime
    high: float
    low: float
    center: float = 0.0
    range_size: float = 0.0
    extension_count: int = 0
    breakout_probability: float = 0.0
    breakdown_probability: float = 0.0
    continuation_probability: float = 0.0

class TradingSignalData(BaseModel):
    id: str
    signal_type: SignalType
    signal_subtype: str
    timestamp: datetime
    price: float
    strength: float = 0.0
    confidence: float = 0.0
    priority: str = "medium"
    target_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    risk_reward_ratio: float = 0.0

class ChanStructureData(BaseModel):
    fenxings: List[FenXingData] = []
    bis: List[BiData] = []
    xianduan: List[Dict[str, Any]] = []
    zhongshus: List[ZhongShuData] = []

# 响应模型
class ChanAnalysisResponse(BaseModel):
    success: bool = True
    symbol: str
    analysis_date: datetime
    timeframes: List[str]
    timeframe_results: Dict[str, Any] = {}
    multi_timeframe_analysis: Dict[str, Any] = {}
    trading_signals: List[TradingSignalData] = []
    ml_predictions: Dict[str, Any] = {}
    risk_assessment: Dict[str, Any] = {}
    computation_time: float = 0.0
    data_quality_score: float = 0.0
    cache_hit: bool = False

class BatchAnalysisResponse(BaseModel):
    success: bool = True
    results: List[Dict[str, Any]] = []
    total_processed: int = 0
    processing_time: float = 0.0
    failed_symbols: List[str] = []

class RealTimePredictionResponse(BaseModel):
    success: bool = True
    symbol: str
    timeframe: str
    prediction: Dict[str, Any] = {}
    timestamp: datetime

class TradingSignalResponse(BaseModel):
    success: bool = True
    symbol: str
    signals: List[TradingSignalData] = []
    total_signals: int = 0
    timestamp: datetime

class StructureMappingResponse(BaseModel):
    success: bool = True
    symbol: str
    primary_timeframe: str
    secondary_timeframe: str
    mapping: Dict[str, Any] = {}
    timestamp: datetime

class MultiTimeframeResponse(BaseModel):
    success: bool = True
    symbol: str
    timeframes: List[str]
    analysis: Dict[str, Any] = {}
    consistency_score: float = 0.0
    timestamp: datetime

# 错误响应模型
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    status_code: int = 500
    timestamp: datetime = Field(default_factory=datetime.now)