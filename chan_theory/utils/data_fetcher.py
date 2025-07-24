#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论数据获取器
从真实数据库获取多周期K线数据和技术因子数据
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import pandas as pd
import numpy as np

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

# 添加API路径
api_path = os.path.join(project_root, 'api')
sys.path.append(api_path)

try:
    from db_handler import DBHandler
except ImportError:
    # 如果还是导入失败，尝试完整路径
    sys.path.append('/Users/libing/kk_Projects/kk_Stock/kk_stock_backend/api')
    from db_handler import DBHandler
# 添加缠论目录路径
chan_theory_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(chan_theory_dir)

from analysis.chan_theory.models.chan_theory_models import TrendLevel


class ChanDataFetcher:
    """缠论数据获取器"""
    
    
    def __init__(self, db_handler=None):
        """初始化数据获取器"""
        if db_handler:
            self.db_handler = db_handler
        else:
            self.db_handler = DBHandler()
        
        # 数据库集合映射
        self.collection_mapping = {
            TrendLevel.MIN5: 'stock_kline_5min',
            TrendLevel.MIN30: 'stock_kline_30min',
            TrendLevel.DAILY: 'stock_kline_daily'
        }
        
        # 时间字段映射（分钟级别使用trade_time，日级使用trade_date）
        self.time_field_mapping = {
            TrendLevel.MIN5: 'trade_time',
            TrendLevel.MIN30: 'trade_time', 
            TrendLevel.DAILY: 'trade_date'
        }
        
        # 技术因子集合
        self.factor_collection = 'stock_factor_pro'
        
        print("📊 缠论数据获取器初始化完成")
    
    def get_kline_data(self, symbol: str, level: TrendLevel, 
                      start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        获取指定周期的K线数据
        
        Args:
            symbol: 股票代码
            level: 时间周期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            K线数据DataFrame
        """
        try:
            collection_name = self.collection_mapping[level]
            collection = self.db_handler.get_collection(collection_name)
            
            # 根据不同级别使用不同的时间字段和格式
            time_field = self.time_field_mapping[level]
            
            if level in [TrendLevel.MIN5, TrendLevel.MIN30]:
                # 分钟级别使用trade_time字段，格式为"YYYY-MM-DD HH:MM:SS"
                start_time_str = start_date.strftime('%Y-%m-%d 09:30:00')
                end_time_str = end_date.strftime('%Y-%m-%d 15:00:00')
                query = {
                    'ts_code': symbol,
                    time_field: {
                        '$gte': start_time_str,
                        '$lte': end_time_str
                    }
                }
            else:
                # 日级使用trade_date字段，格式为YYYYMMDD
                query = {
                    'ts_code': symbol,
                    time_field: {
                        '$gte': start_date.strftime('%Y%m%d'),
                        '$lte': end_date.strftime('%Y%m%d')
                    }
                }
            
            print(f"🔍 查询 {symbol} {level.value} 级别数据...")
            cursor = collection.find(query).sort(time_field, 1)
            data_list = list(cursor)
            
            if not data_list:
                print(f"⚠️ 未找到 {symbol} {level.value} 级别的K线数据")
                # 尝试查看数据库中是否有该股票的任何数据
                test_query = {'ts_code': symbol}
                test_cursor = collection.find(test_query).limit(1)
                test_data = list(test_cursor)
                if test_data:
                    print(f"💡 数据库中存在 {symbol} 的数据，但可能日期范围不匹配")
                else:
                    print(f"❌ 数据库中完全没有 {symbol} 的数据")
                return pd.DataFrame()
            
            # 转换为DataFrame
            df = pd.DataFrame(data_list)
            
            # 临时调试：输出原始数据信息
            if level == TrendLevel.DAILY and len(df) > 0:
                print(f"🔍 {symbol} 日线原始数据调试信息:")
                print(f"   列名: {list(df.columns)}")
                print(f"   前3行数据:")
                for i, (index, row) in enumerate(df.head(3).iterrows()):
                    if i < 3:
                        print(f"     行{i}: trade_date={row.get('trade_date', 'N/A')}, open={row.get('open', 'N/A')}, high={row.get('high', 'N/A')}, low={row.get('low', 'N/A')}, close={row.get('close', 'N/A')}")
            
            # 数据清洗和格式化
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🔍 {symbol} {level.value} 级别数据清洗前: {len(df)} 条记录")
            df = self._clean_kline_data(df, level)
            logger.info(f"🔍 {symbol} {level.value} 级别数据清洗后: {len(df)} 条记录")
            
            print(f"✅ 获取 {symbol} {level.value} K线数据: {len(df)} 条记录")
            return df
            
        except Exception as e:
            print(f"❌ 获取K线数据失败: {e}")
            return pd.DataFrame()
    
    def get_factor_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        获取技术因子数据（包含布林带）
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            技术因子数据DataFrame
        """
        try:
            collection = self.db_handler.get_collection(self.factor_collection)
            
            # 构建查询条件
            query = {
                'ts_code': symbol,
                'trade_date': {
                    '$gte': start_date.strftime('%Y%m%d'),
                    '$lte': end_date.strftime('%Y%m%d')
                }
            }
            
            # 查询数据
            cursor = collection.find(query).sort('trade_date', 1)
            data_list = list(cursor)
            
            if not data_list:
                print(f"⚠️ 未找到 {symbol} 的技术因子数据")
                return pd.DataFrame()
            
            # 转换为DataFrame
            df = pd.DataFrame(data_list)
            
            # 数据清洗和格式化
            df = self._clean_factor_data(df)
            
            print(f"✅ 获取 {symbol} 技术因子数据: {len(df)} 条记录")
            return df
            
        except Exception as e:
            print(f"❌ 获取技术因子数据失败: {e}")
            return pd.DataFrame()
    
    def get_multi_timeframe_data(self, symbol: str, start_date: datetime, 
                                end_date: datetime) -> Dict[TrendLevel, pd.DataFrame]:
        """
        获取多周期数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            多周期数据字典
        """
        print(f"📊 获取 {symbol} 多周期数据...")
        
        multi_data = {}
        
        # 获取各个周期的K线数据
        for level in TrendLevel:
            kline_data = self.get_kline_data(symbol, level, start_date, end_date)
            if not kline_data.empty:
                # 为分钟级别计算技术因子
                if level in [TrendLevel.MIN5, TrendLevel.MIN30]:
                    kline_data = self._calculate_minute_technical_factors(kline_data, level)
                
                multi_data[level] = kline_data
        
        # 获取日线技术因子数据
        if TrendLevel.DAILY in multi_data:
            factor_data = self.get_factor_data(symbol, start_date, end_date)
            
            # 将技术因子数据合并到日线数据中
            if not factor_data.empty:
                daily_data = multi_data[TrendLevel.DAILY]
                
                # 按交易日期合并（处理类型不匹配问题）
                if 'original_time_field' in daily_data.columns:
                    try:
                        daily_data_with_date = daily_data.copy()
                        
                        # 确保两个数据源的trade_date字段类型一致
                        daily_data_with_date['trade_date'] = daily_data_with_date['original_time_field'].astype(str)
                        factor_data_copy = factor_data.copy()
                        factor_data_copy['trade_date'] = factor_data_copy['trade_date'].astype(str)
                        
                        merged_data = pd.merge(
                            daily_data_with_date, 
                            factor_data_copy, 
                            on='trade_date', 
                            how='left',
                            suffixes=('', '_factor')
                        )
                        
                        # 移除临时的trade_date列
                        merged_data = merged_data.drop('trade_date', axis=1, errors='ignore')
                        multi_data[TrendLevel.DAILY] = merged_data
                        print(f"✅ 日线数据与数据库技术因子合并完成")
                    except Exception as merge_error:
                        print(f"⚠️ 数据合并失败，使用原始日线数据: {merge_error}")
                        # 如果合并失败，为日线计算技术因子
                        multi_data[TrendLevel.DAILY] = self._calculate_minute_technical_factors(
                            multi_data[TrendLevel.DAILY], TrendLevel.DAILY
                        )
            else:
                # 如果没有数据库中的技术因子，为日线计算基础技术因子
                multi_data[TrendLevel.DAILY] = self._calculate_minute_technical_factors(
                    multi_data[TrendLevel.DAILY], TrendLevel.DAILY
                )
                print(f"✅ 日线数据计算技术因子完成")
        
        print(f"✅ 多周期数据获取完成，包含 {len(multi_data)} 个周期")
        return multi_data
    
    def _clean_kline_data(self, df: pd.DataFrame, level: TrendLevel) -> pd.DataFrame:
        """清洗K线数据"""
        if df.empty:
            return df
        
        # 根据不同级别处理时间字段
        time_field = self.time_field_mapping[level]
        required_fields = [time_field, 'open', 'high', 'low', 'close', 'vol']
        missing_fields = [field for field in required_fields if field not in df.columns]
        
        if missing_fields:
            print(f"⚠️ {level.value} 数据缺少字段: {missing_fields}")
            return pd.DataFrame()
        
        # 数据类型转换 - 根据级别处理时间字段
        if level in [TrendLevel.MIN5, TrendLevel.MIN30]:
            # 分钟级别：trade_time字段保持原始格式"YYYY-MM-DD HH:MM:SS"
            df['datetime_index'] = pd.to_datetime(df[time_field], errors='coerce')
            print(f"ℹ️ {level.value}级别时间字段示例: {df[time_field].iloc[0] if len(df) > 0 else 'N/A'}")
        else:
            # 日级：trade_date字段转换为日期格式
            print(f"ℹ️ {level.value}级别原始时间字段示例: {df[time_field].iloc[0] if len(df) > 0 else 'N/A'}")
            df['datetime_index'] = pd.to_datetime(df[time_field], format='%Y%m%d', errors='coerce')
            
            # 检查转换后的时间字段
            nan_count = df['datetime_index'].isna().sum()
            print(f"ℹ️ {level.value}级别时间转换结果: {len(df) - nan_count}/{len(df)} 条成功")
            if nan_count > 0:
                print(f"⚠️ {level.value}级别时间转换失败的前5个值:")
                failed_values = df[df['datetime_index'].isna()][time_field].head(5).tolist()
                print(f"   {failed_values}")
        
        # 价格字段转换为float
        price_fields = ['open', 'high', 'low', 'close']
        for field in price_fields:
            original_count = len(df)
            df[field] = pd.to_numeric(df[field], errors='coerce')
            nan_count = df[field].isna().sum()
            if nan_count > 0:
                print(f"⚠️ {level.value}级别 {field} 字段转换失败: {nan_count}/{original_count} 条")
        
        # 成交量转换
        df['volume'] = pd.to_numeric(df['vol'], errors='coerce')
        
        # 检查每个字段的NaN情况
        check_fields = price_fields + ['datetime_index', 'volume']
        print(f"ℹ️ {level.value}级别清洗前字段完整性检查:")
        for field in check_fields:
            nan_count = df[field].isna().sum()
            if nan_count > 0:
                print(f"   {field}: {nan_count}/{len(df)} 条NaN")
        
        # 删除无效数据 - 只删除关键字段为空的数据
        critical_fields = price_fields + ['datetime_index']
        df_before = len(df)
        df = df.dropna(subset=critical_fields)
        df_after = len(df)
        
        if df_before != df_after:
            print(f"⚠️ {level.value}级别删除无效数据: {df_before} -> {df_after} 条 (删除了 {df_before - df_after} 条)")
        
        # 设置索引
        df.set_index('datetime_index', inplace=True)
        df.sort_index(inplace=True)
        
        # 数据验证
        df = df[(df['high'] >= df['low']) & (df['high'] >= df['open']) & 
                (df['high'] >= df['close']) & (df['low'] <= df['open']) & 
                (df['low'] <= df['close'])]
        
        # 保留原始时间字段供参考
        if time_field in df.columns:
            df['original_time_field'] = df[time_field]
        
        print(f"✅ {level.value} 数据清洗完成，共 {len(df)} 条记录")
        
        return df
    
    def _clean_factor_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗技术因子数据"""
        if df.empty:
            return df
        
        # 日期转换
        df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        
        # 布林带字段检查和转换
        bollinger_fields = ['boll_upper_qfq', 'boll_mid_qfq', 'boll_lower_qfq']
        available_bollinger = [field for field in bollinger_fields if field in df.columns]
        
        if available_bollinger:
            for field in available_bollinger:
                df[field] = pd.to_numeric(df[field], errors='coerce')
            print(f"✅ 发现布林带字段: {available_bollinger}")
        else:
            print("⚠️ 未发现布林带字段，将使用价格计算")
        
        # 其他技术指标字段转换
        technical_fields = [col for col in df.columns if any(indicator in col.lower() 
                           for indicator in ['macd', 'rsi', 'ma', 'ema', 'kdj'])]
        
        for field in technical_fields:
            df[field] = pd.to_numeric(df[field], errors='coerce')
        
        # 设置索引
        df.set_index('trade_date', inplace=True)
        df.sort_index(inplace=True)
        
        return df
    
    def calculate_bollinger_bands(self, price_data: pd.Series, period: int = 20, 
                                 std_multiplier: float = 2.0) -> Dict[str, pd.Series]:
        """
        计算布林带（当数据库中没有时使用）
        
        Args:
            price_data: 价格序列（通常是收盘价）
            period: 计算周期
            std_multiplier: 标准差倍数
            
        Returns:
            布林带数据字典
        """
        # 计算中轨（移动平均）
        middle = price_data.rolling(window=period).mean()
        
        # 计算标准差
        std = price_data.rolling(window=period).std()
        
        # 计算上轨和下轨
        upper = middle + (std * std_multiplier)
        lower = middle - (std * std_multiplier)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    def _assign_minute_timestamps(self, df: pd.DataFrame, level: TrendLevel) -> pd.DataFrame:
        """
        为分钟级数据分配具体的时间戳
        每个交易日的数据按A股交易时间分配到不同时间点
        
        Args:
            df: 原始分钟级数据DataFrame (只包含日期)
            level: 时间级别
            
        Returns:
            带有具体时间戳的DataFrame
        """
        if df.empty:
            return df
        
        # 日周月级别不需要分钟时间戳处理
        return df
    
    def _generate_trading_timepoints(self, trade_date: pd.Timestamp, interval_minutes: int) -> list:
        """
        为交易日生成A股交易时间点
        
        Args:
            trade_date: 交易日期
            interval_minutes: 时间间隔(分钟)
            
        Returns:
            时间点列表
        """
        timepoints = []
        
        # 上午时段: 09:30-11:30 (2小时)
        morning_start = trade_date.replace(hour=9, minute=30, second=0)
        morning_end = trade_date.replace(hour=11, minute=30, second=0)
        
        # 下午时段: 13:00-15:00 (2小时)
        afternoon_start = trade_date.replace(hour=13, minute=0, second=0)
        afternoon_end = trade_date.replace(hour=15, minute=0, second=0)
        
        # 生成上午时间点
        current_time = morning_start
        while current_time <= morning_end:
            timepoints.append(current_time)
            current_time += pd.Timedelta(minutes=interval_minutes)
        
        # 生成下午时间点
        current_time = afternoon_start
        while current_time <= afternoon_end:
            timepoints.append(current_time)
            current_time += pd.Timedelta(minutes=interval_minutes)
        
        return timepoints
    
    def validate_data_quality(self, data: Dict[TrendLevel, pd.DataFrame]) -> Dict[TrendLevel, bool]:
        """
        验证数据质量
        
        Args:
            data: 多周期数据
            
        Returns:
            各周期数据质量验证结果
        """
        validation_results = {}
        
        for level, df in data.items():
            is_valid = True
            issues = []
            
            if df.empty:
                is_valid = False
                issues.append("数据为空")
            else:
                # 检查数据完整性
                if df.isnull().any().any():
                    issues.append("存在空值")
                
                # 检查价格逻辑
                invalid_price_logic = (df['high'] < df['low']) | \
                                    (df['high'] < df['open']) | \
                                    (df['high'] < df['close']) | \
                                    (df['low'] > df['open']) | \
                                    (df['low'] > df['close'])
                
                if invalid_price_logic.any():
                    issues.append("价格逻辑错误")
                
                # 检查数据量
                if len(df) < 30:
                    issues.append("数据量不足")
                    is_valid = False
            
            validation_results[level] = is_valid
            
            if issues:
                print(f"⚠️ {level.value} 数据质量问题: {', '.join(issues)}")
            else:
                print(f"✅ {level.value} 数据质量良好")
        
        return validation_results
    
    def _calculate_minute_technical_factors(self, df: pd.DataFrame, level: TrendLevel) -> pd.DataFrame:
        """
        为分钟级别计算技术因子（包括布林带、移动平均等）
        
        Args:
            df: K线数据
            level: 时间级别
            
        Returns:
            带有技术因子的DataFrame
        """
        if df.empty:
            return df
        
        try:
            print(f"📏 为 {level.value} 级别计算技术因子...")
            
            # 复制数据避免修改原始数据
            df_with_factors = df.copy()
            
            # 1. 计算布林带（模拟缠论三线）
            close_price = df_with_factors['close']
            
            # 根据不同级别调整布林带参数
            if level == TrendLevel.MIN5:
                period = 20  # 5分钟级别使甲20周期（约100分钟）
                std_multiplier = 2.0
            elif level == TrendLevel.MIN30:
                period = 14  # 30分钟级别使甲14周期（约7小时）
                std_multiplier = 2.0
            else:  # 日级
                period = 20  # 日级使用20天
                std_multiplier = 2.0
            
            bollinger_bands = self.calculate_bollinger_bands(
                close_price, period=period, std_multiplier=std_multiplier
            )
            
            df_with_factors['boll_upper'] = bollinger_bands['upper']
            df_with_factors['boll_mid'] = bollinger_bands['middle']
            df_with_factors['boll_lower'] = bollinger_bands['lower']
            
            # 2. 计算移动平均线
            if level == TrendLevel.MIN5:
                ma_periods = [5, 10, 20]  # 5、10、20周期
            elif level == TrendLevel.MIN30:
                ma_periods = [5, 10, 14]  # 5、10、14周期
            else:  # 日级
                ma_periods = [5, 10, 20, 60]  # 5、10、20、60天
            
            for period in ma_periods:
                df_with_factors[f'ma{period}'] = close_price.rolling(window=period).mean()
            
            # 3. 计算RSI指标
            rsi_period = 14 if level != TrendLevel.MIN5 else 10
            df_with_factors['rsi'] = self._calculate_rsi(close_price, period=rsi_period)
            
            # 4. 计算MACD指标
            if level == TrendLevel.MIN5:
                fast_period, slow_period, signal_period = 12, 26, 9
            elif level == TrendLevel.MIN30:
                fast_period, slow_period, signal_period = 8, 17, 6
            else:
                fast_period, slow_period, signal_period = 12, 26, 9
            
            macd_data = self._calculate_macd(
                close_price, fast_period=fast_period, 
                slow_period=slow_period, signal_period=signal_period
            )
            
            df_with_factors['macd'] = macd_data['macd']
            df_with_factors['macd_signal'] = macd_data['signal']
            df_with_factors['macd_hist'] = macd_data['histogram']
            
            # 5. 计算成交量指标
            volume_ma_period = 10 if level == TrendLevel.MIN5 else 14
            df_with_factors['vol_ma'] = df_with_factors['volume'].rolling(window=volume_ma_period).mean()
            df_with_factors['vol_ratio'] = df_with_factors['volume'] / df_with_factors['vol_ma']
            
            # 6. 计算价格位置指标（在布林带中的位置）
            upper = df_with_factors['boll_upper']
            lower = df_with_factors['boll_lower']
            df_with_factors['boll_position'] = (close_price - lower) / (upper - lower)
            
            # 7. 计算波动率
            volatility_period = 10 if level == TrendLevel.MIN5 else 14
            df_with_factors['volatility'] = close_price.pct_change().rolling(window=volatility_period).std()
            
            print(f"✅ {level.value} 级别技术因子计算完成")
            return df_with_factors
            
        except Exception as e:
            print(f"❌ {level.value} 级别技术因子计算失败: {e}")
            return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        计算RSI指标
        
        Args:
            prices: 价格序列
            period: 计算周期
            
        Returns:
            RSI数据
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast_period: int = 12, 
                       slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
        """
        计算MACD指标
        
        Args:
            prices: 价格序列
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            MACD数据字典
        """
        # 计算指数移动平均
        ema_fast = prices.ewm(span=fast_period).mean()
        ema_slow = prices.ewm(span=slow_period).mean()
        
        # MACD线 = 快线 - 慢线
        macd_line = ema_fast - ema_slow
        
        # 信号线 = MACD的指数移动平均
        signal_line = macd_line.ewm(span=signal_period).mean()
        
        # 柱状图 = MACD线 - 信号线
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }