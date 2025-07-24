#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论多周期趋势分析模块
基于缠中说禅理论的个股多周期趋势分析
支持5分钟、30分钟、日线多周期联立分析
包含次级走势与上一级走势的映射关系分析
"""

from .models.chan_theory_models import (
    ChanTheoryConfig,
    TrendLevel,
    FenXing,
    Bi,
    XianDuan,
    ZhongShu,
    TrendAnalysisResult,
    FenXingType,
    TrendDirection,
    BollingerBands
)

from .analyzers.structure_analyzer import ChanStructureAnalyzer
from .analyzers.multi_timeframe_analyzer import MultiTimeframeAnalyzer

__all__ = [
    'ChanTheoryConfig',
    'TrendLevel',
    'FenXing',
    'Bi',
    'XianDuan',
    'ZhongShu',
    'TrendAnalysisResult',
    'FenXingType',
    'TrendDirection',
    'BollingerBands',
    'ChanStructureAnalyzer',
    'MultiTimeframeAnalyzer',
]