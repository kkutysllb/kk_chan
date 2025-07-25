#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据可视化API路由
专为Vue3前端图表组件提供优化的数据接口
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import logging

from api.schemas.visualization_schemas import (
    ChartDataRequest, ChartDataResponse,
    KLineChartResponse, TechnicalIndicatorResponse,
    StructureOverlayResponse, HeatmapDataResponse
)
from api.core.dependencies import get_visualization_service, get_chan_service, VisualizationService, ChanAnalysisService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chart_data", response_model=ChartDataResponse)
async def get_chart_data(
    request: ChartDataRequest,
    viz_service: VisualizationService = Depends(get_visualization_service)
):
    """
    获取图表数据 - 通用接口
    支持K线、技术指标、缠论结构等多种图表类型
    """
    try:
        chart_data = await viz_service.get_chart_data(
            symbol=request.symbol,
            chart_type=request.chart_type,
            timeframe=request.timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            indicators=request.indicators,
            structures=request.structures,
            config=request.config
        )
        
        return ChartDataResponse(
            success=True,
            data=chart_data,
            chart_type=request.chart_type,
            symbol=request.symbol,
            timeframe=request.timeframe,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"获取图表数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取图表数据失败: {str(e)}")

@router.get("/kline/{symbol}", response_model=KLineChartResponse)
async def get_kline_chart_data(
    symbol: str,
    timeframe: str = Query("daily", description="时间周期"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(1000, description="数据点数量限制"),
    include_volume: bool = Query(True, description="包含成交量"),
    viz_service: VisualizationService = Depends(get_visualization_service)
):
    """
    K线图数据接口
    优化为ECharts/Chart.js格式
    """
    try:
        # 设置默认时间范围
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=365)
        
        kline_data = await viz_service.get_kline_chart_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            include_volume=include_volume
        )
        
        return KLineChartResponse(
            success=True,
            symbol=symbol,
            timeframe=timeframe,
            data=kline_data,
            data_points=len(kline_data.get('kline', [])),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"获取K线数据失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取K线数据失败: {str(e)}")

@router.get("/technical_indicators/{symbol}", response_model=TechnicalIndicatorResponse)
async def get_technical_indicators(
    symbol: str,
    indicators: List[str] = Query(["MA", "MACD", "RSI", "BOLL"], description="技术指标列表"),
    timeframe: str = Query("daily", description="时间周期"),
    viz_service: VisualizationService = Depends(get_visualization_service)
):
    """
    技术指标数据接口
    支持多种技术指标的图表展示
    """
    try:
        indicator_data = await viz_service.get_technical_indicators(
            symbol=symbol,
            indicators=indicators,
            timeframe=timeframe
        )
        
        return TechnicalIndicatorResponse(
            success=True,
            symbol=symbol,
            timeframe=timeframe,
            indicators=indicators,
            data=indicator_data,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"获取技术指标失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取技术指标失败: {str(e)}")

@router.get("/chan_structure_overlay/{symbol}", response_model=StructureOverlayResponse)
async def get_chan_structure_overlay(
    symbol: str,
    timeframe: str = Query("daily", description="时间周期"),
    structures: List[str] = Query(["fenxing", "bi", "xianduan"], description="结构类型"),
    show_signals: bool = Query(True, description="显示交易信号"),
    show_zhongshu: bool = Query(True, description="显示中枢"),
    chan_service: ChanAnalysisService = Depends(get_chan_service),
    viz_service: VisualizationService = Depends(get_visualization_service)
):
    """
    缠论结构叠加数据接口
    在K线图上叠加显示缠论结构
    """
    try:
        # 获取缠论分析结果
        analysis_result = await chan_service.get_cached_analysis(symbol, timeframe)
        
        if not analysis_result:
            # 如果没有缓存，执行快速分析
            analysis_result = await chan_service.quick_analysis(symbol, timeframe)
        
        # 转换为图表叠加格式
        overlay_data = await viz_service.convert_chan_structure_to_overlay(
            analysis_result=analysis_result,
            structures=structures,
            show_signals=show_signals,
            show_zhongshu=show_zhongshu
        )
        
        return StructureOverlayResponse(
            success=True,
            symbol=symbol,
            timeframe=timeframe,
            structures=structures,
            overlay_data=overlay_data,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"获取缠论结构叠加失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取缠论结构叠加失败: {str(e)}")

@router.get("/market_heatmap")
async def get_market_heatmap(
    market: str = Query("A股", description="市场类型"),
    metric: str = Query("chan_strength", description="热力图指标"),
    timeframe: str = Query("daily", description="时间周期"),
    sectors: List[str] = Query([], description="行业筛选"),
    viz_service: VisualizationService = Depends(get_visualization_service)
):
    """
    市场热力图数据接口
    显示市场整体缠论结构强度分布
    """
    try:
        heatmap_data = await viz_service.get_market_heatmap(
            market=market,
            metric=metric,
            timeframe=timeframe,
            sectors=sectors
        )
        
        return {
            "success": True,
            "market": market,
            "metric": metric,
            "timeframe": timeframe,
            "data": heatmap_data.get("data", []) if isinstance(heatmap_data, dict) else heatmap_data,
            "chart_config": {
                "color_scale": "RdYlBu_r",
                "show_text": True,
                "aspect": "auto"
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"获取市场热力图失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取市场热力图失败: {str(e)}")

@router.get("/signal_distribution/{symbol}")
async def get_signal_distribution(
    symbol: str,
    timeframe: str = Query("daily", description="时间周期"),
    signal_type: str = Query("all", description="信号类型: buy/sell/all"),
    period_days: int = Query(365, description="统计周期天数"),
    viz_service: VisualizationService = Depends(get_visualization_service)
):
    """
    信号分布统计接口
    分析买卖点信号的时间分布和成功率
    """
    try:
        distribution_data = await viz_service.get_signal_distribution(
            symbol=symbol,
            timeframe=timeframe,
            signal_type=signal_type,
            period_days=period_days
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "signal_type": signal_type,
            "period_days": period_days,
            "distribution": distribution_data,
            "statistics": {
                "total_signals": distribution_data.get('total_signals', 0),
                "success_rate": distribution_data.get('success_rate', 0),
                "avg_return": distribution_data.get('avg_return', 0)
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"获取信号分布失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取信号分布失败: {str(e)}")

@router.get("/structure_evolution/{symbol}")
async def get_structure_evolution(
    symbol: str,
    timeframe: str = Query("daily", description="时间周期"),
    structure_type: str = Query("zhongshu", description="结构类型"),
    period_days: int = Query(180, description="观察周期天数"),
    viz_service: VisualizationService = Depends(get_visualization_service)
):
    """
    结构演化分析接口
    追踪缠论结构的演化过程
    """
    try:
        evolution_data = await viz_service.get_structure_evolution(
            symbol=symbol,
            timeframe=timeframe,
            structure_type=structure_type,
            period_days=period_days
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "structure_type": structure_type,
            "evolution": evolution_data,
            "chart_config": {
                "animation": True,
                "show_transitions": True,
                "highlight_changes": True
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"获取结构演化失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取结构演化失败: {str(e)}")

@router.get("/performance_dashboard/{symbol}")
async def get_performance_dashboard(
    symbol: str,
    timeframes: List[str] = Query(["daily", "30min"], description="时间周期列表"),
    metrics: List[str] = Query(["return", "sharpe", "max_drawdown"], description="性能指标"),
    benchmark: str = Query("000300.SH", description="基准指数"),
    viz_service: VisualizationService = Depends(get_visualization_service)
):
    """
    性能仪表板数据接口
    提供缠论策略的综合性能分析
    """
    try:
        dashboard_data = await viz_service.get_performance_dashboard(
            symbol=symbol,
            timeframes=timeframes,
            metrics=metrics,
            benchmark=benchmark
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "timeframes": timeframes,
            "metrics": metrics,
            "benchmark": benchmark,
            "dashboard": dashboard_data,
            "summary": {
                "overall_score": dashboard_data.get('overall_score', 0),
                "risk_level": dashboard_data.get('risk_level', 'medium'),
                "recommendation": dashboard_data.get('recommendation', 'hold')
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"获取性能仪表板失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取性能仪表板失败: {str(e)}")

@router.get("/real_time_chart/{symbol}")
async def get_real_time_chart_data(
    symbol: str,
    timeframe: str = Query("1min", description="时间周期"),
    indicators: List[str] = Query(["MA5", "MA20"], description="实时指标"),
    include_chan: bool = Query(True, description="包含缠论结构"),
    viz_service: VisualizationService = Depends(get_visualization_service)
):
    """
    实时图表数据接口
    为实时图表更新提供WebSocket友好的数据格式
    """
    try:
        real_time_data = await viz_service.get_real_time_chart_data(
            symbol=symbol,
            timeframe=timeframe,
            indicators=indicators,
            include_chan=include_chan
        )
        
        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "data": real_time_data,
            "update_frequency": "1min",  # 更新频率
            "websocket_endpoint": f"/ws/real_time/{symbol}",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"获取实时图表数据失败 {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取实时图表数据失败: {str(e)}")