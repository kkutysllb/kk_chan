#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论分析API路由
提供完整的缠论分析功能接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import logging

from api.schemas.chan_schemas import (
    ChanAnalysisRequest, ChanAnalysisResponse,
    BatchAnalysisRequest, BatchAnalysisResponse,
    RealTimePredictionResponse, TradingSignalResponse,
    StructureMappingResponse, MultiTimeframeResponse
)
from api.core.dependencies import get_chan_service, get_cache_service
from api.core.dependencies import ChanAnalysisService, CacheService
from api.middleware.rate_limiter import rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/comprehensive_analysis", response_model=ChanAnalysisResponse)
@rate_limit(calls=100, period=3600)  # 每小时100次
async def comprehensive_chan_analysis(
    request: ChanAnalysisRequest,
    background_tasks: BackgroundTasks,
    chan_service: ChanAnalysisService = Depends(get_chan_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """
    全面缠论分析接口
    
    功能：
    - 多时间周期联立分析
    - 智能分型笔段识别
    - 中枢结构分析
    - 买卖点信号生成
    - 机器学习预测增强
    """
    try:
        # 构建缓存键
        cache_key = f"chan_analysis:{request.symbol}:{hash(str(request.dict()))}"
        
        # 检查缓存
        cached_result = await cache_service.get(cache_key)
        if cached_result and not request.force_refresh:
            logger.info(f"从缓存返回分析结果: {request.symbol}")
            return ChanAnalysisResponse(
                success=True,
                symbol=request.symbol,
                analysis_date=datetime.now(),
                timeframes=request.timeframes,
                timeframe_results=cached_result.get('timeframe_results', cached_result.get('kline_data', {})),
                multi_timeframe_analysis=cached_result.get('multi_timeframe_analysis', {}),
                trading_signals=cached_result.get('trading_signals', []),
                ml_predictions=cached_result.get('ml_predictions', {}),
                risk_assessment=cached_result.get('risk_assessment', {}),
                computation_time=0,
                data_quality_score=cached_result.get('data_quality_score', 0.8),
                cache_hit=True
            )
        
        # 执行分析
        start_time = datetime.now()
        
        analysis_result = await chan_service.comprehensive_analysis(
            symbol=request.symbol,
            timeframes=request.timeframes,
            start_date=request.start_date,
            end_date=request.end_date,
            include_ml_prediction=request.include_ml_prediction,
            include_signals=request.include_signals,
            config=request.config
        )
        
        computation_time = (datetime.now() - start_time).total_seconds()
        analysis_result['computation_time'] = computation_time
        
        # 后台缓存结果
        background_tasks.add_task(
            cache_service.set,
            cache_key,
            analysis_result,
            expire=3600  # 1小时过期
        )
        
        # 后台保存到数据库
        background_tasks.add_task(
            chan_service.save_analysis_result,
            request.symbol,
            analysis_result
        )
        
        # 调试输出
        logger.info(f"分析结果键: {list(analysis_result.keys())}")
        logger.info(f"timeframe_results内容: {analysis_result.get('timeframe_results', {})}")
        logger.info(f"kline_data内容: {len(analysis_result.get('kline_data', []))}")
        
        return ChanAnalysisResponse(
            success=True,
            symbol=request.symbol,
            analysis_date=datetime.now(),
            timeframes=request.timeframes,
            timeframe_results=analysis_result.get('timeframe_results', {}),
            multi_timeframe_analysis=analysis_result.get('multi_timeframe_analysis', {}),
            trading_signals=analysis_result.get('trading_signals', []),
            ml_predictions=analysis_result.get('ml_predictions', {}),
            risk_assessment=analysis_result.get('risk_assessment', {}),
            computation_time=computation_time,
            data_quality_score=analysis_result.get('data_quality_score', 0.8),
            cache_hit=False
        )
        
    except Exception as e:
        logger.error(f"缠论分析失败 {request.symbol}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )

@router.post("/batch_analysis", response_model=BatchAnalysisResponse)
@rate_limit(calls=10, period=3600)  # 每小时10次批量分析
async def batch_chan_analysis(
    request: BatchAnalysisRequest,
    chan_service: ChanAnalysisService = Depends(get_chan_service)
):
    """批量缠论分析接口"""
    try:
        start_time = datetime.now()
        
        # 并行分析
        results = await chan_service.batch_analysis(
            symbols=request.symbols,
            timeframes=request.timeframes,
            start_date=request.start_date,
            end_date=request.end_date,
            max_concurrent=request.max_concurrent or 5
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return BatchAnalysisResponse(
            success=True,
            results=results,
            total_processed=len(results),
            processing_time=processing_time,
            failed_symbols=[r['symbol'] for r in results if not r.get('success', True)]
        )
        
    except Exception as e:
        logger.error(f"批量分析失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"批量分析失败: {str(e)}")

@router.get("/real_time_prediction/{symbol}", response_model=RealTimePredictionResponse)
@rate_limit(calls=1000, period=3600)  # 每小时1000次实时预测
async def real_time_prediction(
    symbol: str,
    timeframe: str = Query("daily", description="时间周期"),
    include_confidence: bool = Query(True, description="包含置信度"),
    chan_service: ChanAnalysisService = Depends(get_chan_service)
):
    """实时缠论预测接口"""
    try:
        prediction = await chan_service.real_time_prediction(
            symbol=symbol,
            timeframe=timeframe,
            include_confidence=include_confidence
        )
        
        return RealTimePredictionResponse(
            success=True,
            symbol=symbol,
            timeframe=timeframe,
            prediction=prediction,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"实时预测失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"实时预测失败: {str(e)}")

@router.get("/trading_signals/{symbol}", response_model=TradingSignalResponse)
async def get_trading_signals(
    symbol: str,
    timeframes: List[str] = Query(["daily"], description="时间周期列表"),
    signal_types: List[str] = Query(["buy", "sell"], description="信号类型"),
    limit: int = Query(50, description="返回信号数量限制"),
    chan_service: ChanAnalysisService = Depends(get_chan_service)
):
    """获取交易信号接口"""
    try:
        signals = await chan_service.get_trading_signals(
            symbol=symbol,
            timeframes=timeframes,
            signal_types=signal_types,
            limit=limit
        )
        
        return TradingSignalResponse(
            success=True,
            symbol=symbol,
            signals=signals,
            total_signals=len(signals),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"获取交易信号失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取交易信号失败: {str(e)}")

@router.get("/structure_mapping/{symbol}", response_model=StructureMappingResponse)
async def get_structure_mapping(
    symbol: str,
    primary_timeframe: str = Query("daily", description="主时间周期"),
    secondary_timeframe: str = Query("30min", description="次时间周期"),
    chan_service: ChanAnalysisService = Depends(get_chan_service)
):
    """获取结构映射分析"""
    try:
        mapping = await chan_service.get_structure_mapping(
            symbol=symbol,
            primary_timeframe=primary_timeframe,
            secondary_timeframe=secondary_timeframe
        )
        
        return StructureMappingResponse(
            success=True,
            symbol=symbol,
            primary_timeframe=primary_timeframe,
            secondary_timeframe=secondary_timeframe,
            mapping=mapping,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"结构映射分析失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"结构映射分析失败: {str(e)}")

@router.get("/multi_timeframe/{symbol}", response_model=MultiTimeframeResponse)
async def multi_timeframe_analysis(
    symbol: str,
    timeframes: List[str] = Query(["5min", "30min", "daily"], description="时间周期列表"),
    analysis_depth: str = Query("standard", description="分析深度: simple/standard/deep"),
    chan_service: ChanAnalysisService = Depends(get_chan_service)
):
    """多时间周期分析接口"""
    try:
        analysis = await chan_service.multi_timeframe_analysis(
            symbol=symbol,
            timeframes=timeframes,
            analysis_depth=analysis_depth
        )
        
        return MultiTimeframeResponse(
            success=True,
            symbol=symbol,
            timeframes=timeframes,
            analysis=analysis,
            consistency_score=analysis.get('consistency_score', 0),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"多时间周期分析失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"多时间周期分析失败: {str(e)}")

@router.get("/market_structure/{symbol}")
async def get_market_structure(
    symbol: str,
    timeframe: str = Query("daily", description="时间周期"),
    structure_type: str = Query("all", description="结构类型: fenxing/bi/xianduan/zhongshu/all"),
    chan_service: ChanAnalysisService = Depends(get_chan_service)
):
    """获取市场结构数据 - 专为前端图表优化"""
    try:
        structure_data = await chan_service.get_market_structure_for_chart(
            symbol=symbol,
            timeframe=timeframe,
            structure_type=structure_type
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "structure_type": structure_type,
            "data": structure_data,
            "chart_config": {
                "color_scheme": "professional",
                "show_labels": True,
                "highlight_signals": True
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"获取市场结构失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取市场结构失败: {str(e)}")

@router.post("/backtest")
async def backtest_strategy(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    strategy_config: Dict[str, Any],
    chan_service: ChanAnalysisService = Depends(get_chan_service)
):
    """缠论策略回测接口"""
    try:
        backtest_result = await chan_service.backtest_chan_strategy(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            strategy_config=strategy_config
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "backtest_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "strategy_config": strategy_config,
            "results": backtest_result,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"策略回测失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"策略回测失败: {str(e)}")