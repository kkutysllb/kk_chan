#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论结构分析器
实现单周期的缠论结构识别：分型、笔、线段、中枢
基于缠论核心理论：次级走势与上一级走势的映射关系
"""

from datetime import datetime
from typing import List, Optional, Dict, Tuple
import pandas as pd
import numpy as np

import sys
import os

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
chan_theory_dir = os.path.dirname(current_dir)
sys.path.append(chan_theory_dir)

from analysis.chan_theory.models.chan_theory_models import (
    TrendLevel, FenXing, Bi, XianDuan, ZhongShu, BollingerBands,
    FenXingType, TrendDirection, ChanTheoryConfig
)


class ChanStructureAnalyzer:
    """缠论结构分析器"""
    
    def __init__(self, config: ChanTheoryConfig, level: TrendLevel):
        """初始化结构分析器"""
        self.config = config
        self.level = level
        
        # 分析结果存储
        self.processed_klines = None
        self.fenxing_list = []
        self.bi_list = []
        self.xianduan_list = []
        self.zhongshu_list = []
        self.bollinger_bands = None
        
        print(f"🔍 {level.value} 级别结构分析器初始化完成")
    
    def analyze_single_timeframe(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        单周期缠论结构分析
        
        Args:
            data: K线数据
            
        Returns:
            分析结果字典
        """
        print(f"📊 开始 {self.level.value} 级别结构分析...")
        
        if data.empty:
            return self._empty_result()
        
        # 1. 数据预处理
        self._preprocess_data(data)
        
        # 2. 处理包含关系
        self._process_containment_relationship()
        
        # 3. 计算布林带（模拟三线）
        self._calculate_bollinger_bands()
        
        # 4. 识别分型
        self._identify_fenxing()
        
        # 5. 构造笔
        self._construct_bi()
        
        # 6. 构造线段
        self._construct_xianduan()
        
        # 7. 识别中枢
        self._identify_zhongshu()
        
        # 8. 趋势分析
        trend_analysis = self._analyze_trend()
        
        # 9. 生成分析结果
        result = self._generate_analysis_result(trend_analysis)
        
        print(f"✅ {self.level.value} 级别结构分析完成")
        return result
    
    def _preprocess_data(self, data: pd.DataFrame) -> None:
        """数据预处理"""
        # 确保数据按时间排序
        self.original_data = data.sort_index()
        
        # 临时调试：检查日线数据的NaN情况
        import logging
        logger = logging.getLogger(__name__)
        
        if self.level == TrendLevel.DAILY and len(self.original_data) > 0:
            logger.info(f"🔍 {self.level.value} 级别数据预处理前调试:")
            logger.info(f"   数据形状: {self.original_data.shape}")
            logger.info(f"   列名: {list(self.original_data.columns)}")
            
            # 检查每列的NaN情况
            logger.info(f"   各列NaN统计:")
            for col in self.original_data.columns:
                nan_count = self.original_data[col].isna().sum()
                if nan_count > 0:
                    logger.info(f"     {col}: {nan_count}/{len(self.original_data)} 个NaN")
            
            # 检查核心K线字段
            required_cols = ['open', 'high', 'low', 'close']
            available_cols = [col for col in required_cols if col in self.original_data.columns]
            logger.info(f"   核心K线字段可用: {available_cols}")
            
            if available_cols:
                subset_df = self.original_data[available_cols]
                valid_rows = len(subset_df.dropna())
                logger.info(f"   仅检查核心字段后有效行数: {valid_rows}/{len(self.original_data)}")
        
        # 数据清洗 - 只对核心字段进行dropna
        required_fields = ['open', 'high', 'low', 'close']
        available_required = [col for col in required_fields if col in self.original_data.columns]
        
        if available_required:
            # 只删除核心字段为空的行
            self.clean_data = self.original_data.dropna(subset=available_required)
        else:
            # 如果没有找到核心字段，使用原始清洗方式
            self.clean_data = self.original_data.dropna()
        
        logger.info(f"📊 {self.level.value} 数据预处理: {len(self.original_data)} -> {len(self.clean_data)} 条")
    
    def _process_containment_relationship(self) -> None:
        """处理包含关系 - 缠论核心：合并包含K线"""
        if self.clean_data.empty:
            self.processed_klines = pd.DataFrame()
            return
        
        df = self.clean_data.copy()
        processed_data = []
        
        # 第一根K线直接加入
        if len(df) > 0:
            first_row = df.iloc[0]
            processed_data.append({
                'timestamp': first_row.name,
                'open': float(first_row['open']),
                'high': float(first_row['high']),
                'low': float(first_row['low']),
                'close': float(first_row['close']),
                'volume': float(first_row.get('volume', first_row.get('vol', 0)))
            })
        
        # 处理后续K线的包含关系
        for i in range(1, len(df)):
            current = df.iloc[i]
            last_processed = processed_data[-1]
            
            current_high = float(current['high'])
            current_low = float(current['low'])
            last_high = last_processed['high']
            last_low = last_processed['low']
            
            # 判断包含关系
            is_current_contains_last = (current_high >= last_high and current_low <= last_low)
            is_last_contains_current = (last_high >= current_high and last_low <= current_low)
            
            if is_current_contains_last or is_last_contains_current:
                # 存在包含关系，需要合并
                if len(processed_data) >= 2:
                    # 根据趋势方向决定合并规则
                    prev_processed = processed_data[-2]
                    is_uptrend = last_high > prev_processed['high']
                    
                    if is_uptrend:
                        # 上升趋势：取高高低高
                        merged_high = max(current_high, last_high)
                        merged_low = max(current_low, last_low)
                    else:
                        # 下降趋势：取低低高低
                        merged_high = min(current_high, last_high)
                        merged_low = min(current_low, last_low)
                else:
                    # 只有一根K线时，取极值
                    merged_high = max(current_high, last_high)
                    merged_low = min(current_low, last_low)
                
                # 更新最后一根处理过的K线
                processed_data[-1].update({
                    'high': merged_high,
                    'low': merged_low,
                    'close': float(current['close']),
                    'volume': last_processed['volume'] + float(current.get('volume', current.get('vol', 0)))
                })
            else:
                # 无包含关系，直接添加新K线
                processed_data.append({
                    'timestamp': current.name,
                    'open': float(current['open']),
                    'high': current_high,
                    'low': current_low,
                    'close': float(current['close']),
                    'volume': float(current.get('volume', current.get('vol', 0)))
                })
        
        # 转换为DataFrame
        self.processed_klines = pd.DataFrame(processed_data)
        if not self.processed_klines.empty:
            self.processed_klines.set_index('timestamp', inplace=True)
        
        print(f"📊 {self.level.value} 包含关系处理: {len(df)} -> {len(self.processed_klines)} 根K线")
    
    def _calculate_bollinger_bands(self) -> None:
        """计算布林带 - 模拟缠论三线"""
        if self.processed_klines.empty:
            return
        
        # 检查是否有现成的布林带数据
        if (self.level == TrendLevel.DAILY and 
            'boll_upper_qfq' in self.clean_data.columns and
            'boll_mid_qfq' in self.clean_data.columns and
            'boll_lower_qfq' in self.clean_data.columns):
            
            # 使用数据库中的布林带数据
            self.bollinger_bands = BollingerBands(
                upper=self.clean_data['boll_upper_qfq'],
                middle=self.clean_data['boll_mid_qfq'],
                lower=self.clean_data['boll_lower_qfq'],
                level=self.level
            )
            print(f"✅ {self.level.value} 使用数据库布林带数据")
        else:
            # 自己计算布林带
            close_prices = self.processed_klines['close']
            period = self.config.bollinger_period
            std_multiplier = self.config.bollinger_std
            
            # 计算中轨（移动平均）
            middle = close_prices.rolling(window=period).mean()
            
            # 计算标准差
            std = close_prices.rolling(window=period).std()
            
            # 计算上轨和下轨
            upper = middle + (std * std_multiplier)
            lower = middle - (std * std_multiplier)
            
            self.bollinger_bands = BollingerBands(
                upper=upper,
                middle=middle,
                lower=lower,
                level=self.level
            )
            print(f"✅ {self.level.value} 计算布林带数据: 周期{period}, 标准差{std_multiplier}")
    
    def _identify_fenxing(self) -> None:
        """识别分型 - 优化版本"""
        if len(self.processed_klines) < self.config.fenxing_window * 2 + 1:
            return
        
        self.fenxing_list = []
        window = self.config.fenxing_window
        
        # 获取分钟级别的分型强度阈值
        strength_threshold = (self.config.minute_fenxing_strength 
                            if self.level in [TrendLevel.MIN5, TrendLevel.MIN30]
                            else self.config.fenxing_strength)
        
        for i in range(window, len(self.processed_klines) - window):
            # 获取当前窗口的数据
            current_window = self.processed_klines.iloc[i-window:i+window+1]
            center_idx = window  # 中心点在窗口中的索引
            
            # 检查顶分型
            if self._is_top_fenxing(current_window, center_idx):
                strength = self._calculate_fenxing_strength(current_window, center_idx, 'top')
                
                # 应用强度阈值过滤
                if strength >= strength_threshold:
                    fenxing = FenXing(
                        index=i,
                        timestamp=self.processed_klines.index[i],
                        price=self.processed_klines.iloc[i]['high'],
                        fenxing_type=FenXingType.TOP,
                        strength=strength,
                        level=self.level,
                        confirmed=True
                    )
                    
                    # 检查分型间隔
                    if self._check_fenxing_gap(fenxing):
                        self.fenxing_list.append(fenxing)
            
            # 检查底分型
            if self._is_bottom_fenxing(current_window, center_idx):
                strength = self._calculate_fenxing_strength(current_window, center_idx, 'bottom')
                
                # 应用强度阈值过滤
                if strength >= strength_threshold:
                    fenxing = FenXing(
                        index=i,
                        timestamp=self.processed_klines.index[i],
                        price=self.processed_klines.iloc[i]['low'],
                        fenxing_type=FenXingType.BOTTOM,
                        strength=strength,
                        level=self.level,
                        confirmed=True
                    )
                    
                    # 检查分型间隔
                    if self._check_fenxing_gap(fenxing):
                        self.fenxing_list.append(fenxing)
        
        # 按时间排序
        self.fenxing_list.sort(key=lambda x: x.timestamp)
        
        print(f"📊 {self.level.value} 识别分型: {len(self.fenxing_list)} 个 (强度阈值: {strength_threshold})")
    
    def _is_top_fenxing(self, window_data: pd.DataFrame, center_idx: int) -> bool:
        """判断是否为顶分型"""
        center_high = window_data.iloc[center_idx]['high']
        
        # 标准缠论：中心K线的高点必须严格高于左右K线
        for i in range(len(window_data)):
            if i != center_idx:
                if window_data.iloc[i]['high'] >= center_high:
                    return False
        
        return True
    
    def _is_bottom_fenxing(self, window_data: pd.DataFrame, center_idx: int) -> bool:
        """判断是否为底分型"""
        center_low = window_data.iloc[center_idx]['low']
        
        # 标准缠论：中心K线的低点必须严格低于左右K线
        for i in range(len(window_data)):
            if i != center_idx:
                if window_data.iloc[i]['low'] <= center_low:
                    return False
        
        return True
    
    def _calculate_fenxing_strength(self, window_data: pd.DataFrame, center_idx: int, fenxing_type: str) -> float:
        """计算分型强度"""
        try:
            if fenxing_type == 'top':
                center_price = window_data.iloc[center_idx]['high']
                extreme_price = window_data['low'].min()
            else:
                center_price = window_data.iloc[center_idx]['low']
                extreme_price = window_data['high'].max()
            
            avg_price = window_data['close'].mean()
            
            if avg_price > 0:
                return abs(center_price - extreme_price) / avg_price
            return 0.0
        except:
            return 0.0
    
    def _check_fenxing_gap(self, new_fenxing: FenXing) -> bool:
        """检查分型间隔 - 修改版：允许连续同类型分型识别，在优化阶段处理"""
        if not self.fenxing_list:
            return True
        
        # 检查与最后一个分型（不分类型）的间隔，避免过于密集的分型
        last_fenxing = self.fenxing_list[-1]
        gap = new_fenxing.index - last_fenxing.index
        
        # 允许连续同类型分型，但要求至少有1个K线间隔
        return gap >= 1
    
    def _optimize_fenxing_sequence(self) -> List[FenXing]:
        """
        优化分型序列：处理连续同类型分型的情况
        
        缠论规则：
        - 连续顶分型：保留价格最高的那个
        - 连续底分型：保留价格最低的那个
        
        Returns:
            优化后的分型列表
        """
        if len(self.fenxing_list) < 2:
            return self.fenxing_list.copy()
        
        optimized_list = []
        i = 0
        
        while i < len(self.fenxing_list):
            current_fenxing = self.fenxing_list[i]
            
            # 查找严格连续的同类型分型
            consecutive_fenxings = [current_fenxing]
            j = i + 1
            
            while (j < len(self.fenxing_list) and 
                   self.fenxing_list[j].fenxing_type == current_fenxing.fenxing_type):
                consecutive_fenxings.append(self.fenxing_list[j])
                j += 1
            
            # 如果有连续同类型分型，选择最优的那个
            if len(consecutive_fenxings) > 1:
                if current_fenxing.fenxing_type == FenXingType.TOP:
                    # 连续顶分型：选择价格最高的
                    best_fenxing = max(consecutive_fenxings, key=lambda f: f.price)
                    print(f"🔄 {self.level.value} 优化连续顶分型: {len(consecutive_fenxings)}个 -> 选择最高价格 {best_fenxing.price:.2f}")
                else:
                    # 连续底分型：选择价格最低的
                    best_fenxing = min(consecutive_fenxings, key=lambda f: f.price)
                    print(f"🔄 {self.level.value} 优化连续底分型: {len(consecutive_fenxings)}个 -> 选择最低价格 {best_fenxing.price:.2f}")
                
                optimized_list.append(best_fenxing)
            else:
                # 没有连续同类型分型，直接添加
                optimized_list.append(current_fenxing)
            
            # 移动到下一组
            i = j
        
        print(f"📊 {self.level.value} 分型序列优化: {len(self.fenxing_list)} -> {len(optimized_list)}")
        return optimized_list
    
    def _optimize_strict_consecutive(self) -> List[FenXing]:
        """处理严格连续的同类型分型"""
        optimized_list = []
        i = 0
        
        while i < len(self.fenxing_list):
            current_fenxing = self.fenxing_list[i]
            
            # 查找连续同类型分型
            consecutive_fenxings = [current_fenxing]
            j = i + 1
            
            while (j < len(self.fenxing_list) and 
                   self.fenxing_list[j].fenxing_type == current_fenxing.fenxing_type):
                consecutive_fenxings.append(self.fenxing_list[j])
                j += 1
            
            # 如果有连续同类型分型，选择最优的那个
            if len(consecutive_fenxings) > 1:
                if current_fenxing.fenxing_type == FenXingType.TOP:
                    best_fenxing = max(consecutive_fenxings, key=lambda f: f.price)
                    print(f"🔄 {self.level.value} 优化连续顶分型: {len(consecutive_fenxings)}个 -> 选择最高价格 {best_fenxing.price:.2f}")
                else:
                    best_fenxing = min(consecutive_fenxings, key=lambda f: f.price)
                    print(f"🔄 {self.level.value} 优化连续底分型: {len(consecutive_fenxings)}个 -> 选择最低价格 {best_fenxing.price:.2f}")
                
                optimized_list.append(best_fenxing)
            else:
                optimized_list.append(current_fenxing)
            
            i = j
        
        return optimized_list
    
    def _optimize_weak_separated_fenxings(self, fenxings: List[FenXing]) -> List[FenXing]:
        """
        处理被弱分型分隔的同类型分型
        识别相近范围内的同类型分型，如果中间的分型相对较弱，则合并
        """
        if len(fenxings) < 3:
            return fenxings
        
        optimized = []
        i = 0
        
        while i < len(fenxings):
            current = fenxings[i]
            
            # 查找在合理范围内的同类型分型群组
            group = [current]
            j = i + 1
            
            # 在接下来的几个分型中寻找同类型分型
            max_look_ahead = min(6, len(fenxings) - i)  # 最多向前看6个分型
            
            while j < i + max_look_ahead and j < len(fenxings):
                candidate = fenxings[j]
                
                # 如果是同类型分型，检查是否应该合并
                if candidate.fenxing_type == current.fenxing_type:
                    # 检查中间是否有强有力的反向分型
                    has_strong_opposite = False
                    
                    for k in range(i + 1, j):
                        middle_fenxing = fenxings[k]
                        if middle_fenxing.fenxing_type != current.fenxing_type:
                            # 计算反向分型的强度
                            if current.fenxing_type == FenXingType.TOP:
                                # 对于顶分型群组，检查中间底分型的深度
                                min_price_in_group = min(f.price for f in group + [candidate])
                                depth_ratio = (current.price - middle_fenxing.price) / current.price
                                if depth_ratio > 0.02:  # 如果回调超过2%，认为是强分型
                                    has_strong_opposite = True
                                    break
                            else:
                                # 对于底分型群组，检查中间顶分型的高度
                                max_price_in_group = max(f.price for f in group + [candidate])
                                rise_ratio = (middle_fenxing.price - current.price) / current.price
                                if rise_ratio > 0.02:  # 如果反弹超过2%，认为是强分型
                                    has_strong_opposite = True
                                    break
                    
                    # 如果没有强反向分型，加入群组
                    if not has_strong_opposite:
                        group.append(candidate)
                
                j += 1
            
            # 如果群组有多个同类型分型，选择最优的
            if len(group) > 1:
                if current.fenxing_type == FenXingType.TOP:
                    best = max(group, key=lambda f: f.price)
                    print(f"🔄 {self.level.value} 优化弱分隔顶分型群组: {len(group)}个 -> 选择最高价格 {best.price:.2f}")
                else:
                    best = min(group, key=lambda f: f.price)
                    print(f"🔄 {self.level.value} 优化弱分隔底分型群组: {len(group)}个 -> 选择最低价格 {best.price:.2f}")
                
                optimized.append(best)
                
                # 跳过群组中的其他分型，但保留中间的反向分型
                next_i = i + 1
                for k in range(i + 1, len(fenxings)):
                    if fenxings[k] not in group:
                        next_i = k
                        break
                    else:
                        next_i = k + 1
                i = next_i
            else:
                optimized.append(current)
                i += 1
        
        return optimized
    
    def _construct_bi(self) -> None:
        """构造笔 - 优化版本（处理连续同类型分型）"""
        if len(self.fenxing_list) < 2:
            return
        
        self.bi_list = []
        
        # 第一步：优化分型序列，处理连续同类型分型
        optimized_fenxing = self._optimize_fenxing_sequence()
        
        if len(optimized_fenxing) < 2:
            return
        
        # 第二步：遍历优化后的分型构造笔
        for i in range(len(optimized_fenxing) - 1):
            current_fenxing = optimized_fenxing[i]
            next_fenxing = optimized_fenxing[i + 1]
            
            # 检查是否为有效笔：顶底分型交替
            if current_fenxing.fenxing_type != next_fenxing.fenxing_type:
                # 计算笔的长度
                length = next_fenxing.index - current_fenxing.index
                
                # 计算幅度
                amplitude = abs(next_fenxing.price - current_fenxing.price) / current_fenxing.price
                
                # 笔需要满足最小长度要求或有足够的强度
                if (length >= self.config.min_bi_length or 
                    amplitude >= self.config.bi_strength_threshold):
                    
                    # 确定笔的方向
                    if current_fenxing.fenxing_type == FenXingType.BOTTOM:
                        direction = TrendDirection.UP
                    else:
                        direction = TrendDirection.DOWN
                    
                    bi = Bi(
                        start_fenxing=current_fenxing,
                        end_fenxing=next_fenxing,
                        direction=direction,
                        length=length,
                        amplitude=amplitude,
                        level=self.level
                    )
                    
                    self.bi_list.append(bi)
        
        print(f"📊 {self.level.value} 构造笔: {len(self.bi_list)} 条 (优化后分型: {len(optimized_fenxing)}, 要求长度>={self.config.min_bi_length}或强度>={self.config.bi_strength_threshold})")
    
    def _construct_xianduan(self) -> None:
        """构造线段"""
        if len(self.fenxing_list) < 2:
            return
        
        self.xianduan_list = []
        
        # 遍历相邻分型构造线段（简化版：分型间至少1根K线）
        for i in range(len(self.fenxing_list) - 1):
            current_fenxing = self.fenxing_list[i]
            next_fenxing = self.fenxing_list[i + 1]
            
            # 检查是否为有效线段：顶底分型交替且至少有1根K线间隔
            if current_fenxing.fenxing_type != next_fenxing.fenxing_type:
                length = next_fenxing.index - current_fenxing.index
                
                if length >= 1:  # 至少1根K线间隔
                    # 确定线段方向
                    if current_fenxing.fenxing_type == FenXingType.BOTTOM:
                        direction = TrendDirection.UP
                    else:
                        direction = TrendDirection.DOWN
                    
                    # 找到相关的笔
                    related_bi = [bi for bi in self.bi_list 
                                 if (bi.start_fenxing.timestamp >= current_fenxing.timestamp and
                                     bi.end_fenxing.timestamp <= next_fenxing.timestamp)]
                    
                    xianduan = XianDuan(
                        start_fenxing=current_fenxing,
                        end_fenxing=next_fenxing,
                        direction=direction,
                        bi_list=related_bi,
                        level=self.level
                    )
                    
                    self.xianduan_list.append(xianduan)
        
        print(f"📊 {self.level.value} 构造线段: {len(self.xianduan_list)} 条")
    
    def _identify_zhongshu(self) -> None:
        """识别中枢"""
        if len(self.xianduan_list) < 3:
            return
        
        self.zhongshu_list = []
        
        # 遍历连续三段线段寻找中枢
        for i in range(len(self.xianduan_list) - 2):
            xd1 = self.xianduan_list[i]
            xd2 = self.xianduan_list[i + 1]
            xd3 = self.xianduan_list[i + 2]
            
            # 计算三段线段的重叠区间
            zhongshu = self._calculate_zhongshu_from_three_xd(xd1, xd2, xd3)
            
            if zhongshu:
                # 检查是否与已有中枢重叠
                merged = False
                for existing_zs in self.zhongshu_list:
                    if self._is_zhongshu_overlap(zhongshu, existing_zs):
                        # 扩展现有中枢
                        existing_zs.high = max(existing_zs.high, zhongshu.high)
                        existing_zs.low = min(existing_zs.low, zhongshu.low)
                        existing_zs.center = (existing_zs.high + existing_zs.low) / 2
                        existing_zs.end_time = zhongshu.end_time
                        existing_zs.extend_count += 1
                        merged = True
                        break
                
                if not merged:
                    self.zhongshu_list.append(zhongshu)
        
        print(f"📊 {self.level.value} 识别中枢: {len(self.zhongshu_list)} 个")
    
    def _calculate_zhongshu_from_three_xd(self, xd1: XianDuan, xd2: XianDuan, xd3: XianDuan) -> Optional[ZhongShu]:
        """计算三段线段的中枢 - 优化版本"""
        # 获取三段线段的高低点
        highs = [xd1.high_price, xd2.high_price, xd3.high_price]
        lows = [xd1.low_price, xd2.low_price, xd3.low_price]
        
        # 改进重叠区间计算：任意两段有重叠即可形成中枢
        overlap_high = float('inf')
        overlap_low = float('-inf')
        
        # 计算每两段的重叠区间
        overlaps = []
        for i in range(3):
            for j in range(i+1, 3):
                h1, l1 = highs[i], lows[i]
                h2, l2 = highs[j], lows[j]
                
                # 计算重叠
                overlap_h = min(h1, h2)
                overlap_l = max(l1, l2)
                
                if overlap_h > overlap_l:  # 存在重叠
                    overlaps.append((overlap_h, overlap_l))
        
        if overlaps:
            # 取所有重叠区间的交集
            overlap_high = min(h for h, l in overlaps)
            overlap_low = max(l for h, l in overlaps)
            
            # 如果交集有效
            if overlap_high > overlap_low:
                center_price = (overlap_high + overlap_low) / 2
                zhongshu_range = (overlap_high - overlap_low) / center_price if center_price > 0 else 0
                
                # 中枢区间检查（更宽松）
                if zhongshu_range >= self.config.min_zhongshu_overlap:
                    return ZhongShu(
                        high=overlap_high,
                        low=overlap_low,
                        center=center_price,
                        start_time=xd1.start_time,
                        end_time=xd3.end_time,
                        forming_xd=[xd1, xd2, xd3],
                        level=self.level
                    )
        
        return None
    
    def _is_zhongshu_overlap(self, zs1: ZhongShu, zs2: ZhongShu) -> bool:
        """判断两个中枢是否重叠"""
        return not (zs1.high < zs2.low or zs1.low > zs2.high)
    
    def _analyze_trend(self) -> Dict[str, any]:
        """趋势分析"""
        if not self.xianduan_list:
            return {
                'current_trend': TrendDirection.SIDEWAYS,
                'trend_strength': 0.5,
                'trend_duration': 0
            }
        
        # 分析最近的线段趋势
        recent_xd = self.xianduan_list[-3:] if len(self.xianduan_list) >= 3 else self.xianduan_list
        
        # 统计趋势方向
        up_count = sum(1 for xd in recent_xd if xd.direction == TrendDirection.UP)
        down_count = sum(1 for xd in recent_xd if xd.direction == TrendDirection.DOWN)
        
        # 确定主要趋势
        if up_count > down_count:
            current_trend = TrendDirection.UP
            trend_strength = up_count / len(recent_xd)
        elif down_count > up_count:
            current_trend = TrendDirection.DOWN
            trend_strength = down_count / len(recent_xd)
        else:
            current_trend = TrendDirection.SIDEWAYS
            trend_strength = 0.5
        
        # 计算趋势持续时间
        if recent_xd:
            trend_duration = (recent_xd[-1].end_time - recent_xd[0].start_time).days
        else:
            trend_duration = 0
        
        return {
            'current_trend': current_trend,
            'trend_strength': trend_strength,
            'trend_duration': trend_duration
        }
    
    def _generate_analysis_result(self, trend_analysis: Dict) -> Dict[str, any]:
        """生成分析结果"""
        # 分型统计
        top_fenxings = [f for f in self.fenxing_list if f.fenxing_type == FenXingType.TOP]
        bottom_fenxings = [f for f in self.fenxing_list if f.fenxing_type == FenXingType.BOTTOM]
        
        # 当前中枢
        current_zhongshu = self.zhongshu_list[-1] if self.zhongshu_list else None
        
        return {
            'level': self.level,
            'data_quality': {
                'original_count': len(self.original_data) if hasattr(self, 'original_data') else 0,
                'processed_count': len(self.processed_klines) if self.processed_klines is not None else 0,
                'has_bollinger': self.bollinger_bands is not None
            },
            'fenxing_count': len(self.fenxing_list),
            'fenxing_tops': top_fenxings,
            'fenxing_bottoms': bottom_fenxings,
            'bi_count': len(self.bi_list),
            'bi_list': self.bi_list,
            'xianduan_count': len(self.xianduan_list),
            'xianduan_list': self.xianduan_list,
            'zhongshu_count': len(self.zhongshu_list),
            'zhongshu_list': self.zhongshu_list,
            'current_zhongshu': current_zhongshu,
            'bollinger_bands': self.bollinger_bands,
            'current_trend': trend_analysis['current_trend'],
            'trend_strength': trend_analysis['trend_strength'],
            'trend_duration': trend_analysis['trend_duration']
        }
    
    def _empty_result(self) -> Dict[str, any]:
        """空结果"""
        return {
            'level': self.level,
            'data_quality': {'original_count': 0, 'processed_count': 0, 'has_bollinger': False},
            'fenxing_count': 0,
            'fenxing_tops': [],
            'fenxing_bottoms': [],
            'bi_count': 0,
            'bi_list': [],
            'xianduan_count': 0,
            'xianduan_list': [],
            'zhongshu_count': 0,
            'zhongshu_list': [],
            'current_zhongshu': None,
            'bollinger_bands': None,
            'current_trend': TrendDirection.SIDEWAYS,
            'trend_strength': 0.5,
            'trend_duration': 0
        }