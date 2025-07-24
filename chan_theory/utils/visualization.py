#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论分析可视化模块
提供完整的缠论结构可视化功能
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import seaborn as sns

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 修复导入路径
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
chan_theory_dir = os.path.dirname(current_dir)
sys.path.append(chan_theory_dir)

try:
    from models.chan_theory_models import TrendLevel, FenXing, Bi, XianDuan, ZhongShu, FenXingType
except ImportError:
    from analysis.chan_theory.models.chan_theory_models import TrendLevel, FenXing, Bi, XianDuan, ZhongShu, FenXingType


class ChanTheoryVisualizer:
    """缠论分析可视化器"""
    
    def __init__(self):
        """初始化可视化器"""
        self.colors = {
            'up': '#FF6B6B',      # 上涨红色
            'down': '#4ECDC4',    # 下跌青色
            'fenxing_top': '#FF4444',    # 顶分型
            'fenxing_bottom': '#44FF44', # 底分型
            'bi': '#FFD93D',      # 笔
            'xd': '#6BCF7F',      # 线段
            'zhongshu': '#A8E6CF', # 中枢
            'bollinger': '#DDA0DD' # 布林带
        }
        
        print("📊 缠论可视化器初始化完成")
    
    def create_multi_timeframe_chart(self, symbol: str, multi_data: Dict[TrendLevel, pd.DataFrame],
                                   analysis_results: Dict, save_path: str = None) -> None:
        """
        创建多周期缠论分析图表
        
        Args:
            symbol: 股票代码
            multi_data: 多周期数据
            analysis_results: 分析结果
            save_path: 保存路径
        """
        print(f"📊 创建 {symbol} 多周期缠论分析图表...")
        
        # 创建子图
        fig, axes = plt.subplots(3, 1, figsize=(16, 12))
        fig.suptitle(f'{symbol} 缠论多周期趋势分析', fontsize=16, fontweight='bold')
        
        # 绘制各个周期（新的多周期分析）
        timeframes = [TrendLevel.MIN5, TrendLevel.MIN30, TrendLevel.DAILY]
        titles = ['5分钟级别', '30分钟级别', '日线级别']
        
        for i, (level, title) in enumerate(zip(timeframes, titles)):
            if level in multi_data and level in analysis_results.get('level_results', {}):
                self._plot_single_timeframe(
                    axes[i], 
                    multi_data[level], 
                    analysis_results['level_results'][level],
                    title,
                    level
                )
            else:
                axes[i].text(0.5, 0.5, f'{title}\n暂无数据', 
                           ha='center', va='center', transform=axes[i].transAxes)
                axes[i].set_title(title)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 多周期图表已保存: {save_path}")
            plt.close()  # 关闭图表释放内存
        else:
            plt.show()
    
    def _plot_single_timeframe(self, ax, data: pd.DataFrame, analysis_result: Dict,
                              title: str, level: TrendLevel) -> None:
        """绘制单个周期的缠论分析"""
        
        # 绘制K线图
        self._plot_candlestick(ax, data)
        
        # 绘制布林带（支持数据库和自计算的布林带）
        if 'bollinger_bands' in analysis_result:
            self._plot_bollinger_bands(ax, data, analysis_result['bollinger_bands'])
        elif self._has_bollinger_data(data):
            # 如果数据中直接包含布林带字段（分钟级别自计算）
            self._plot_bollinger_from_data(ax, data)
        
        # 绘制移动平均线（分钟级别自计算）
        if self._has_ma_data(data):
            self._plot_moving_averages(ax, data)
        
        # 绘制分型
        if 'fenxing_tops' in analysis_result and 'fenxing_bottoms' in analysis_result:
            self._plot_fenxing(ax, analysis_result['fenxing_tops'], analysis_result['fenxing_bottoms'])
        
        # 绘制笔
        if 'bi_list' in analysis_result:
            self._plot_bi(ax, analysis_result['bi_list'])
        
        # 绘制线段
        if 'xd_list' in analysis_result:
            self._plot_xd(ax, analysis_result['xd_list'])
        
        # 绘制中枢
        if 'zhongshu_list' in analysis_result:
            self._plot_zhongshu(ax, analysis_result['zhongshu_list'])
        
        # 设置标题和格式
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # 格式化x轴（根据不同周期调整）
        if len(data) > 0:
            if level == TrendLevel.MIN5:
                # 5分钟级别：显示小时和分钟
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            elif level == TrendLevel.MIN30:
                # 30分钟级别：显示日期和小时
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            else:
                # 日级：显示月日
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_candlestick(self, ax, data: pd.DataFrame) -> None:
        """绘制K线图"""
        if data.empty:
            return
        
        # 计算涨跌
        up = data['close'] >= data['open']
        down = ~up
        
        # 根据数据量动态调整K线宽度
        data_length = len(data)
        if data_length > 1000:
            width = 0.3  # 分钟级别数据量大，使用细K线
        elif data_length > 200:
            width = 0.6  # 30分钟级别
        else:
            width = 0.8  # 日级数据
        
        # 绘制实体
        ax.bar(data.index[up], data['close'][up] - data['open'][up], 
               bottom=data['open'][up], color=self.colors['up'], alpha=0.8, width=width)
        ax.bar(data.index[down], data['open'][down] - data['close'][down], 
               bottom=data['close'][down], color=self.colors['down'], alpha=0.8, width=width)
        
        # 绘制影线（根据数据量调整线宽）
        linewidth = 0.3 if data_length > 500 else 0.5
        ax.vlines(data.index, data['low'], data['high'], colors='black', alpha=0.5, linewidth=linewidth)
    
    def _plot_bollinger_bands(self, ax, data: pd.DataFrame, bollinger_data) -> None:
        """绘制布林带"""
        if not bollinger_data or data.empty:
            return
        
        try:
            # 处理BollingerBands对象
            if hasattr(bollinger_data, 'upper'):
                # 这是一个BollingerBands对象
                upper = bollinger_data.upper
                middle = bollinger_data.middle
                lower = bollinger_data.lower
            elif isinstance(bollinger_data, dict):
                # 这是一个字典
                if 'upper' not in bollinger_data or 'middle' not in bollinger_data or 'lower' not in bollinger_data:
                    return
                upper = bollinger_data['upper']
                middle = bollinger_data['middle']
                lower = bollinger_data['lower']
            else:
                return
            
            # 确保数据不为空
            if upper is None or middle is None or lower is None:
                return
            
            # 处理pandas Series（有索引）
            if hasattr(upper, 'index') and hasattr(upper, 'dropna'):
                try:
                    # 找到K线数据和布林带数据的共同索引
                    data_index = set(data.index)
                    upper_index = set(upper.index)
                    middle_index = set(middle.index) 
                    lower_index = set(lower.index)
                    
                    # 找到所有数据都存在的索引
                    common_indices = data_index & upper_index & middle_index & lower_index
                    
                    if len(common_indices) > 5:
                        # 排序索引
                        sorted_indices = sorted(common_indices)
                        
                        # 只保留所有指标都有有效值的索引
                        valid_indices = []
                        upper_values = []
                        middle_values = []
                        lower_values = []
                        
                        for idx in sorted_indices:
                            u_val = upper.loc[idx]
                            m_val = middle.loc[idx]
                            l_val = lower.loc[idx]
                            
                            # 检查所有值都是有效的数字
                            if (pd.notna(u_val) and pd.notna(m_val) and pd.notna(l_val) and
                                not pd.isna(u_val) and not pd.isna(m_val) and not pd.isna(l_val)):
                                valid_indices.append(idx)
                                upper_values.append(float(u_val))
                                middle_values.append(float(m_val))
                                lower_values.append(float(l_val))
                        
                        # 检查是否有足够的有效数据
                        if len(valid_indices) > 5:
                            ax.plot(valid_indices, upper_values, 
                                   color=self.colors['bollinger'], alpha=0.7, linewidth=1, label='布林上轨')
                            ax.plot(valid_indices, middle_values, 
                                   color=self.colors['bollinger'], alpha=0.8, linewidth=1.5, label='布林中轨')
                            ax.plot(valid_indices, lower_values, 
                                   color=self.colors['bollinger'], alpha=0.7, linewidth=1, label='布林下轨')
                            
                            # 填充布林带区域
                            ax.fill_between(valid_indices, upper_values, lower_values, 
                                           color=self.colors['bollinger'], alpha=0.1)
                            
                            print(f"✅ 布林带绘制成功，{len(valid_indices)} 个有效数据点")
                        else:
                            print(f"⚠️ 布林带有效数据点不足: {len(valid_indices)} (原始: {len(sorted_indices)})")
                    else:
                        print(f"⚠️ 布林带共同数据点不足: {len(common_indices)}")
                except Exception as detail_error:
                    print(f"⚠️ 布林带详细处理失败: {detail_error}")
            else:
                print("⚠️ 布林带数据格式不正确，缺少索引")
                
        except Exception as e:
            print(f"⚠️ 绘制布林带失败: {e}")
    
    def _has_bollinger_data(self, data: pd.DataFrame) -> bool:
        """检查数据中是否包含布林带字段"""
        bollinger_fields = ['boll_upper', 'boll_mid', 'boll_lower']
        return all(field in data.columns for field in bollinger_fields)
    
    def _plot_bollinger_from_data(self, ax, data: pd.DataFrame) -> None:
        """从数据帧中绘制布林带"""
        try:
            # 获取有效数据
            mask = (data['boll_upper'].notna() & 
                   data['boll_mid'].notna() & 
                   data['boll_lower'].notna())
            
            if mask.sum() < 5:  # 至少需要50个有效数据点
                return
            
            valid_data = data[mask]
            
            # 绘制布林带线条
            ax.plot(valid_data.index, valid_data['boll_upper'], 
                   color=self.colors['bollinger'], alpha=0.7, linewidth=1, label='上轨')
            ax.plot(valid_data.index, valid_data['boll_mid'], 
                   color=self.colors['bollinger'], alpha=0.8, linewidth=1.5, label='中轨')
            ax.plot(valid_data.index, valid_data['boll_lower'], 
                   color=self.colors['bollinger'], alpha=0.7, linewidth=1, label='下轨')
            
            # 填充布林带区域
            ax.fill_between(valid_data.index, valid_data['boll_upper'], valid_data['boll_lower'], 
                           color=self.colors['bollinger'], alpha=0.1)
            
            print(f"✅ 从数据中绘制布林带成功，{len(valid_data)} 个有效数据点")
            
        except Exception as e:
            print(f"⚠️ 从数据中绘制布林带失败: {e}")
    
    def _has_ma_data(self, data: pd.DataFrame) -> bool:
        """检查数据中是否包含移动平均线数据"""
        ma_fields = [col for col in data.columns if col.startswith('ma') and col[2:].isdigit()]
        return len(ma_fields) > 0
    
    def _plot_moving_averages(self, ax, data: pd.DataFrame) -> None:
        """绘制移动平均线"""
        try:
            ma_fields = [col for col in data.columns if col.startswith('ma') and col[2:].isdigit()]
            ma_colors = ['#FF9900', '#0099FF', '#00FF99', '#FF0099', '#9900FF']
            
            for i, ma_field in enumerate(ma_fields[:5]):  # 最多显示5条均线
                if ma_field in data.columns:
                    valid_data = data[data[ma_field].notna()]
                    if len(valid_data) > 5:
                        color = ma_colors[i % len(ma_colors)]
                        ax.plot(valid_data.index, valid_data[ma_field], 
                               color=color, alpha=0.8, linewidth=1, 
                               label=f'{ma_field.upper()}')
            
            print(f"✅ 绘制移动平均线成功，共 {len(ma_fields)} 条")
            
        except Exception as e:
            print(f"⚠️ 绘制移动平均线失败: {e}")
    
    def _plot_fenxing(self, ax, fenxing_tops: List, fenxing_bottoms: List) -> None:
        """绘制分型"""
        # 绘制顶分型
        for fenxing in fenxing_tops:
            if hasattr(fenxing, 'timestamp') and hasattr(fenxing, 'price'):
                ax.scatter(fenxing.timestamp, fenxing.price, 
                          color=self.colors['fenxing_top'], s=100, marker='v', 
                          label='顶分型' if fenxing == fenxing_tops[0] else "", zorder=5)
            elif isinstance(fenxing, dict):
                timestamp = fenxing.get('index') or fenxing.get('timestamp')
                price = fenxing.get('price')
                if timestamp and price:
                    ax.scatter(timestamp, price, 
                              color=self.colors['fenxing_top'], s=100, marker='v', 
                              label='顶分型' if fenxing == fenxing_tops[0] else "", zorder=5)
        
        # 绘制底分型
        for fenxing in fenxing_bottoms:
            if hasattr(fenxing, 'timestamp') and hasattr(fenxing, 'price'):
                ax.scatter(fenxing.timestamp, fenxing.price, 
                          color=self.colors['fenxing_bottom'], s=100, marker='^', 
                          label='底分型' if fenxing == fenxing_bottoms[0] else "", zorder=5)
            elif isinstance(fenxing, dict):
                timestamp = fenxing.get('index') or fenxing.get('timestamp')
                price = fenxing.get('price')
                if timestamp and price:
                    ax.scatter(timestamp, price, 
                              color=self.colors['fenxing_bottom'], s=100, marker='^', 
                              label='底分型' if fenxing == fenxing_bottoms[0] else "", zorder=5)
    
    def _plot_bi(self, ax, bi_list: List) -> None:
        """绘制笔"""
        for i, bi in enumerate(bi_list):
            try:
                if hasattr(bi, 'start_time') and hasattr(bi, 'end_time'):
                    start_time = bi.start_time
                    end_time = bi.end_time
                    start_price = bi.start_price
                    end_price = bi.end_price
                elif isinstance(bi, dict):
                    start_time = bi.get('start_time')
                    end_time = bi.get('end_time')
                    start_price = bi.get('start_price')
                    end_price = bi.get('end_price')
                else:
                    continue
                
                # 检查时间戳是否有效，过滤掉NaT
                if (start_time is not None and end_time is not None and 
                    start_price is not None and end_price is not None and
                    pd.notna(start_time) and pd.notna(end_time) and
                    pd.notna(start_price) and pd.notna(end_price)):
                    
                    ax.plot([start_time, end_time], [start_price, end_price], 
                           color=self.colors['bi'], linewidth=2, alpha=0.8,
                           label='笔' if i == 0 else "", zorder=3)
            except Exception as e:
                print(f"⚠️ 绘制笔失败: {e}")
                continue
    
    def _plot_xd(self, ax, xd_list: List) -> None:
        """绘制线段"""
        for i, xd in enumerate(xd_list):
            try:
                if hasattr(xd, 'start_time') and hasattr(xd, 'end_time'):
                    start_time = xd.start_time
                    end_time = xd.end_time
                    start_price = xd.start_price
                    end_price = xd.end_price
                elif isinstance(xd, dict):
                    start_time = xd.get('start_time')
                    end_time = xd.get('end_time')
                    start_price = xd.get('start_price')
                    end_price = xd.get('end_price')
                else:
                    continue
                
                # 检查时间戳是否有效，过滤掉NaT
                if (start_time is not None and end_time is not None and 
                    start_price is not None and end_price is not None and
                    pd.notna(start_time) and pd.notna(end_time) and
                    pd.notna(start_price) and pd.notna(end_price)):
                    
                    ax.plot([start_time, end_time], [start_price, end_price], 
                           color=self.colors['xd'], linewidth=3, alpha=0.9,
                           label='线段' if i == 0 else "", zorder=4)
            except Exception as e:
                print(f"⚠️ 绘制线段失败: {e}")
                continue
    
    def _plot_zhongshu(self, ax, zhongshu_list: List) -> None:
        """绘制中枢"""
        for i, zs in enumerate(zhongshu_list):
            try:
                if hasattr(zs, 'start_time') and hasattr(zs, 'end_time'):
                    start_time = zs.start_time
                    end_time = zs.end_time
                    high = zs.high
                    low = zs.low
                elif isinstance(zs, dict):
                    start_time = zs.get('start_time')
                    end_time = zs.get('end_time')
                    high = zs.get('high')
                    low = zs.get('low')
                else:
                    continue
                
                # 检查时间戳和价格是否有效
                if (start_time is not None and end_time is not None and 
                    high is not None and low is not None and
                    pd.notna(start_time) and pd.notna(end_time) and
                    pd.notna(high) and pd.notna(low)):
                    
                    # 绘制中枢矩形
                    try:
                        width = (end_time - start_time).total_seconds() / 86400  # 转换为天数
                        rect = Rectangle((mdates.date2num(start_time), low), 
                                       width, high - low,
                                       facecolor=self.colors['zhongshu'], 
                                       alpha=0.3, edgecolor='blue', linewidth=1,
                                       label='中枢' if i == 0 else "")
                        ax.add_patch(rect)
                        
                        # 添加中枢标签
                        center_time = start_time + (end_time - start_time) / 2
                        center_price = (high + low) / 2
                        if pd.notna(center_time) and pd.notna(center_price):
                            ax.text(center_time, center_price, f'中枢{i+1}', 
                                   ha='center', va='center', fontsize=8, 
                                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
                    except Exception as e:
                        print(f"⚠️ 绘制中枢矩形失败: {e}")
            except Exception as e:
                print(f"⚠️ 绘制中枢失败: {e}")
                continue
    
    def create_structure_summary_chart(self, symbol: str, analysis_results: Dict, 
                                     save_path: str = None) -> None:
        """创建结构汇总图表"""
        print(f"📊 创建 {symbol} 结构汇总图表...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'{symbol} 缠论结构分析汇总', fontsize=16, fontweight='bold')
        
        # 1. 各级别结构数量对比
        self._plot_structure_counts(ax1, analysis_results)
        
        # 2. 趋势一致性分析
        self._plot_trend_consistency(ax2, analysis_results)
        
        # 3. 中枢分布分析
        self._plot_zhongshu_distribution(ax3, analysis_results)
        
        # 4. 信号强度分析
        self._plot_signal_strength(ax4, analysis_results)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 结构汇总图表已保存: {save_path}")
            plt.close()  # 关闭图表释放内存
        else:
            plt.show()
    
    def _plot_structure_counts(self, ax, analysis_results: Dict) -> None:
        """绘制结构数量对比"""
        levels = []
        fenxing_counts = []
        bi_counts = []
        xd_counts = []
        zhongshu_counts = []
        
        level_results = analysis_results.get('level_results', {})
        for level_key, result in level_results.items():
            if isinstance(level_key, str):
                levels.append(level_key)
            else:
                levels.append(level_key.value if hasattr(level_key, 'value') else str(level_key))
            
            fenxing_counts.append(result.get('fenxing_count', 0))
            bi_counts.append(result.get('bi_count', 0))
            xd_counts.append(result.get('xd_count', 0))
            zhongshu_counts.append(result.get('zhongshu_count', 0))
        
        x = np.arange(len(levels))
        width = 0.2
        
        ax.bar(x - 1.5*width, fenxing_counts, width, label='分型', color='#FF6B6B')
        ax.bar(x - 0.5*width, bi_counts, width, label='笔', color='#4ECDC4')
        ax.bar(x + 0.5*width, xd_counts, width, label='线段', color='#45B7D1')
        ax.bar(x + 1.5*width, zhongshu_counts, width, label='中枢', color='#96CEB4')
        
        ax.set_xlabel('时间级别')
        ax.set_ylabel('数量')
        ax.set_title('各级别缠论结构数量对比')
        ax.set_xticks(x)
        ax.set_xticklabels(levels)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_trend_consistency(self, ax, analysis_results: Dict) -> None:
        """绘制趋势一致性分析"""
        multi_analysis = analysis_results.get('multi_analysis', {})
        trend_directions = multi_analysis.get('trend_directions', {})
        
        if not trend_directions:
            ax.text(0.5, 0.5, '暂无趋势数据', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('趋势一致性分析')
            return
        
        levels = []
        trends = []
        colors = []
        
        for level_key, trend in trend_directions.items():
            if isinstance(level_key, str):
                levels.append(level_key)
            else:
                levels.append(level_key.value if hasattr(level_key, 'value') else str(level_key))
            
            if hasattr(trend, 'value'):
                trend_str = trend.value
            else:
                trend_str = str(trend)
            trends.append(trend_str)
            
            # 根据趋势方向设置颜色
            if trend_str == 'up':
                colors.append('#FF6B6B')
            elif trend_str == 'down':
                colors.append('#4ECDC4')
            else:
                colors.append('#FFD93D')
        
        ax.bar(levels, [1]*len(levels), color=colors, alpha=0.7)
        ax.set_ylabel('趋势方向')
        ax.set_title('多周期趋势一致性')
        ax.set_ylim(0, 1.2)
        
        # 添加趋势标签
        for i, (level, trend) in enumerate(zip(levels, trends)):
            ax.text(i, 0.5, trend, ha='center', va='center', fontweight='bold')
        
        # 添加一致性评分
        consistency = multi_analysis.get('trend_consistency', 0)
        ax.text(0.02, 0.98, f'一致性评分: {consistency:.2f}', 
               transform=ax.transAxes, va='top', 
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    def _plot_zhongshu_distribution(self, ax, analysis_results: Dict) -> None:
        """绘制中枢分布分析"""
        level_results = analysis_results.get('level_results', {})
        
        zhongshu_ranges = []
        levels = []
        
        for level_key, result in level_results.items():
            zhongshu_list = result.get('zhongshu_list', [])
            if zhongshu_list:
                for zs in zhongshu_list:
                    if isinstance(zs, dict):
                        range_ratio = zs.get('range_ratio', 0)
                    else:
                        range_ratio = getattr(zs, 'range_ratio', 0)
                    
                    zhongshu_ranges.append(range_ratio)
                    if isinstance(level_key, str):
                        levels.append(level_key)
                    else:
                        levels.append(level_key.value if hasattr(level_key, 'value') else str(level_key))
        
        if zhongshu_ranges:
            ax.scatter(levels, zhongshu_ranges, s=100, alpha=0.7, c=zhongshu_ranges, 
                      cmap='viridis')
            ax.set_ylabel('中枢区间比例')
            ax.set_title('中枢分布分析')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, '暂无中枢数据', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('中枢分布分析')
    
    def _plot_signal_strength(self, ax, analysis_results: Dict) -> None:
        """绘制信号强度分析"""
        comprehensive = analysis_results.get('comprehensive_assessment', {})
        
        if not comprehensive:
            ax.text(0.5, 0.5, '暂无信号数据', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('信号强度分析')
            return
        
        # 提取各项评分
        metrics = {
            '趋势强度': comprehensive.get('overall_trend_strength', 0),
            '趋势可靠性': comprehensive.get('trend_reliability', 0),
            '置信度': comprehensive.get('confidence_score', 0)
        }
        
        # 创建雷达图效果
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
        values = list(metrics.values())
        
        # 闭合图形
        angles += angles[:1]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#FF6B6B')
        ax.fill(angles, values, alpha=0.25, color='#FF6B6B')
        
        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics.keys())
        ax.set_ylim(0, 1)
        ax.set_title('信号强度分析')
        ax.grid(True)
        
        # 添加数值标签
        for angle, value, label in zip(angles[:-1], values[:-1], metrics.keys()):
            ax.text(angle, value + 0.05, f'{value:.2f}', ha='center', va='center')
    
    def create_mapping_relationship_chart(self, symbol: str, analysis_results: Dict,
                                        save_path: str = None) -> None:
        """创建映射关系图表"""
        print(f"📊 创建 {symbol} 映射关系图表...")
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        fig.suptitle(f'{symbol} 次级走势与上一级走势映射关系', fontsize=16, fontweight='bold')
        
        # 绘制映射关系网络图
        self._plot_mapping_network(ax, analysis_results)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 映射关系图表已保存: {save_path}")
            plt.close()  # 关闭图表释放内存
        else:
            plt.show()
    
    def _plot_mapping_network(self, ax, analysis_results: Dict) -> None:
        """绘制映射关系网络"""
        # 这里可以实现更复杂的网络图
        # 暂时用简化的方式展示
        
        trend_relationships = analysis_results.get('trend_relationships', {})
        
        if not trend_relationships:
            ax.text(0.5, 0.5, '暂无映射关系数据', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('映射关系分析')
            return
        
        # 绘制映射关系表格
        y_pos = 0.9
        ax.text(0.1, y_pos, '映射关系分析结果:', fontsize=14, fontweight='bold', transform=ax.transAxes)
        
        for relationship_name, relationship in trend_relationships.items():
            y_pos -= 0.15
            
            higher_level = relationship.get('higher_level', '未知')
            lower_level = relationship.get('lower_level', '未知')
            is_consistent = relationship.get('is_consistent', False)
            is_correction = relationship.get('is_correction', False)
            quality = relationship.get('relationship_quality', 0)
            
            status = "✅ 一致" if is_consistent else ("🔄 修正" if is_correction else "❌ 背离")
            
            text = f"{higher_level} ← → {lower_level}: {status} (质量: {quality:.2f})"
            ax.text(0.1, y_pos, text, fontsize=10, transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')