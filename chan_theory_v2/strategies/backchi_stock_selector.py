#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的MACD背驰选股策略
基于MACD红绿柱面积对比的实用背驰判断方法
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..', '..'))

from chan_theory_v2.models.simple_backchi import SimpleBackchiAnalyzer
from chan_theory_v2.models.dynamics import MacdCalculator
from chan_theory_v2.models.kline import KLineList
from chan_theory_v2.models.enums import TimeLevel
from chan_theory_v2.core.trading_calendar import get_nearest_trading_date
from database.db_handler import get_db_handler

logger = logging.getLogger(__name__)


class SignalStrength(Enum):
    """信号强度枚举"""
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"


@dataclass
class StockSignal:
    """股票信号数据结构"""
    symbol: str
    name: str
    
    # 信号类型和强度
    signal_type: str = "观望"  # "买入", "卖出", "观望"
    backchi_type: Optional[str] = None  # "bottom", "top"
    reliability: float = 0.0
    description: str = ""
    
    # MACD技术指标
    has_macd_golden_cross: bool = False
    has_macd_death_cross: bool = False
    
    # 综合评分
    overall_score: float = 0.0
    signal_strength: SignalStrength = SignalStrength.WEAK
    recommendation: str = "观望"
    
    # 关键价位
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # 时间戳
    analysis_time: datetime = None
    
    def __post_init__(self):
        if self.analysis_time is None:
            self.analysis_time = datetime.now()


class SimpleBackchiStockSelector:
    """简化的MACD背驰选股器"""
    
    def __init__(self):
        """初始化选股器"""
        self.db_handler = get_db_handler()
        
        # 选股参数配置
        self.config = {
            'days_30min': 30,      # 30分钟分析天数
            'min_backchi_strength': 0.3,  # 最小背驰强度
            'require_macd_golden_cross': True,  # 买入要求MACD金叉
            'max_stocks_per_batch': 0,     # 0表示处理全市场所有股票
            'min_price': 2.0,      # 最低股价过滤
            'max_price': 1000.0,   # 最高股价过滤
            'min_volume_ratio': 0.5,  # 最小成交量比率
        }
        
        logger.info("🎯 简化MACD背驰选股器初始化完成")
    
    def get_stock_pool(self) -> List[Dict[str, str]]:
        """获取股票池（全市场筛选）"""
        try:
            # 获取股票基础信息
            basic_collection = self.db_handler.get_collection("infrastructure_stock_basic")
            
            # 基础筛选条件：排除ST股票、退市股票、B股等
            filter_condition = {
                "name": {"$not": {"$regex": "ST|退市|暂停|B$|N|C"}},
                "ts_code": {"$exists": True, "$ne": None},
            }
            
            cursor = basic_collection.find(filter_condition)
            all_stocks = [{"symbol": doc["ts_code"], "name": doc["name"]} for doc in cursor]
            
            # 进一步过滤：基于最新价格和成交量
            filtered_stocks = []
            daily_collection = self.db_handler.get_collection("stock_kline_daily")
            
            # 获取最近交易日
            current_date = datetime.now().date()
            latest_trading_date = get_nearest_trading_date(current_date, direction='backward')
            
            if not latest_trading_date:
                logger.error("❌ 无法获取最近交易日")
                return []
            
            logger.info(f"📅 使用最近交易日: {latest_trading_date}")
            
            for stock in all_stocks:
                try:
                    # 获取最近交易日的日线数据进行过滤
                    latest_date_str = latest_trading_date.strftime("%Y%m%d")
                    
                    latest_data = daily_collection.find({
                        "ts_code": stock["symbol"],
                        "trade_date": {"$lte": latest_date_str}
                    }).sort("trade_date", -1).limit(5)
                    
                    latest_list = list(latest_data)
                    if len(latest_list) >= 3:
                        latest = latest_list[0]
                        
                        # 价格过滤
                        current_price = float(latest.get("close", 0))
                        if (self.config["min_price"] <= current_price <= self.config["max_price"]):
                            
                            # 成交量过滤（检查是否有足够流动性）
                            avg_volume = sum(float(item.get("vol", 0)) for item in latest_list[:3]) / 3
                            if avg_volume > 1000:  # 至少1000手成交量
                                filtered_stocks.append(stock)
                                
                except Exception:
                    continue  # 跳过有问题的股票
            
            logger.info(f"📊 全市场股票池：{len(all_stocks)} → {len(filtered_stocks)} 只股票（经过流动性过滤）")
            return filtered_stocks
            
        except Exception as e:
            logger.error(f"❌ 获取股票池失败: {e}")
            return []
    
    def analyze_stock_backchi(self, symbol: str) -> Optional[StockSignal]:
        """分析单个股票的背驰情况"""
        try:
            # 获取30分钟K线数据
            data = self._fetch_stock_data(symbol, TimeLevel.MIN_30, self.config['days_30min'])
            if not data or len(data) < 30:
                logger.debug(f"📊 {symbol} 数据不足: {len(data) if data else 0}条")
                return None
            
            # 转换数据格式
            klines = KLineList.from_mongo_data(data, TimeLevel.MIN_30)
            
            # 计算MACD
            close_prices = [kline.close for kline in klines]
            macd_calculator = MacdCalculator()
            macd_data = macd_calculator.calculate(close_prices)
            
            if len(macd_data) < 20:
                logger.debug(f"📊 {symbol} MACD数据不足: {len(macd_data)}条")
                return None
            
            # 执行简化背驰分析
            analyzer = SimpleBackchiAnalyzer()
            backchi_type, reliability, description = analyzer.analyze_backchi(klines, macd_data)
            
            # 检查MACD金叉/死叉
            has_golden_cross, has_death_cross = self._check_macd_crosses(macd_data)
            
            # 判断信号类型
            signal_type = "观望"
            if backchi_type == "bottom" and reliability >= self.config['min_backchi_strength']:
                if not self.config['require_macd_golden_cross'] or has_golden_cross:
                    signal_type = "买入"
            elif backchi_type == "top" and reliability >= self.config['min_backchi_strength']:
                signal_type = "卖出"
            
            # 只有买入或卖出信号才创建记录
            if signal_type == "观望":
                return None
            
            # 获取股票名称
            stock_name = self._get_stock_name(symbol)
            
            # 创建信号对象
            signal = StockSignal(
                symbol=symbol,
                name=stock_name,
                signal_type=signal_type,
                backchi_type=backchi_type,
                reliability=reliability,
                description=description,
                has_macd_golden_cross=has_golden_cross,
                has_macd_death_cross=has_death_cross
            )
            
            # 计算评分和建议
            signal.overall_score = self._calculate_signal_score(signal)
            signal.signal_strength = self._determine_signal_strength(signal.overall_score)
            signal.recommendation = self._generate_recommendation(signal)
            
            # 计算关键价位
            self._calculate_key_prices(signal, klines)
            
            logger.info(f"✅ {symbol} {signal_type}信号评分: {signal.overall_score:.1f}, 强度: {signal.signal_strength.value}")
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ 分析股票 {symbol} 失败: {e}")
            return None
    
    def _check_macd_crosses(self, macd_data) -> Tuple[bool, bool]:
        """检查MACD金叉和死叉"""
        has_golden_cross = False
        has_death_cross = False
        
        if len(macd_data) >= 3:
            recent_macd = macd_data[-3:]
            for i in range(1, len(recent_macd)):
                prev_macd = recent_macd[i-1]
                curr_macd = recent_macd[i]
                
                # 检查金叉
                if (prev_macd.dif <= prev_macd.dea and 
                    curr_macd.dif > curr_macd.dea and
                    curr_macd.macd >= 0):
                    has_golden_cross = True
                
                # 检查死叉
                if (prev_macd.dif >= prev_macd.dea and 
                    curr_macd.dif < curr_macd.dea and
                    curr_macd.macd <= 0):
                    has_death_cross = True
        
        return has_golden_cross, has_death_cross
    
    def _get_stock_name(self, symbol: str) -> str:
        """获取股票名称"""
        try:
            basic_collection = self.db_handler.get_collection("infrastructure_stock_basic")
            doc = basic_collection.find_one({"ts_code": symbol})
            return doc.get("name", symbol) if doc else symbol
        except:
            return symbol
    
    def _calculate_signal_score(self, signal: StockSignal) -> float:
        """计算信号综合评分"""
        score = 0.0
        
        # 背驰可靠度得分 (60分)
        score += signal.reliability * 60
        
        # MACD金叉得分 (25分)
        if signal.has_macd_golden_cross and signal.signal_type == "买入":
            score += 25
        elif signal.has_macd_death_cross and signal.signal_type == "卖出":
            score += 25
        
        # 信号类型得分 (15分)
        if signal.signal_type in ["买入", "卖出"]:
            score += 15
        
        return min(score, 100.0)
    
    def _determine_signal_strength(self, score: float) -> SignalStrength:
        """确定信号强度"""
        if score >= 80:
            return SignalStrength.STRONG
        elif score >= 60:
            return SignalStrength.MEDIUM
        else:
            return SignalStrength.WEAK
    
    def _generate_recommendation(self, signal: StockSignal) -> str:
        """生成投资建议"""
        if signal.signal_type == "买入":
            if signal.signal_strength == SignalStrength.STRONG:
                return "强烈推荐买入"
            elif signal.signal_strength == SignalStrength.MEDIUM:
                return "建议买入"
            else:
                return "谨慎买入"
        elif signal.signal_type == "卖出":
            if signal.signal_strength == SignalStrength.STRONG:
                return "强烈推荐卖出"
            elif signal.signal_strength == SignalStrength.MEDIUM:
                return "建议卖出"
            else:
                return "谨慎卖出"
        else:
            return "观望"
    
    def _calculate_key_prices(self, signal: StockSignal, klines: KLineList):
        """计算关键价位"""
        if len(klines) == 0:
            return
        
        current_price = klines[-1].close
        signal.entry_price = current_price
        
        if signal.signal_type == "买入":
            # 止损价：入场价的95%
            signal.stop_loss = current_price * 0.95
            # 止盈价：根据背驰强度确定
            profit_ratio = 1 + signal.reliability * 0.15
            signal.take_profit = current_price * profit_ratio
            
        elif signal.signal_type == "卖出":
            # 止损价：入场价的105%
            signal.stop_loss = current_price * 1.05
            # 止盈价：根据背驰强度确定
            profit_ratio = 1 - signal.reliability * 0.15
            signal.take_profit = current_price * profit_ratio
    
    def run_stock_selection(self, max_results: int = 50) -> List[StockSignal]:
        """执行选股（基于简化MACD背驰算法）"""
        logger.info("🎯 开始执行简化MACD背驰选股")
        
        stock_pool = self.get_stock_pool()
        if not stock_pool:
            logger.warning("⚠️ 股票池为空")
            return []
        
        signals = []
        processed_count = 0
        
        # 如果max_stocks_per_batch为0，则处理所有股票，否则按配置限制
        stock_limit = len(stock_pool) if self.config['max_stocks_per_batch'] == 0 else self.config['max_stocks_per_batch']
        
        for stock in stock_pool[:stock_limit]:
            try:
                symbol = stock['symbol']
                name = stock['name']
                
                logger.debug(f"📊 分析股票: {symbol} - {name}")
                
                # 分析背驰信号
                signal = self.analyze_stock_backchi(symbol)
                
                if signal:
                    signals.append(signal)
                
                processed_count += 1
                
                # 每100只股票报告一次进度
                if processed_count % 100 == 0:
                    logger.info(f"📈 已处理 {processed_count}/{stock_limit} 只股票，发现 {len(signals)} 个信号")
                
            except Exception as e:
                logger.error(f"❌ 处理股票 {stock['symbol']} 失败: {e}")
                continue
        
        # 按评分排序
        signals.sort(key=lambda x: x.overall_score, reverse=True)
        
        # 返回前N个结果
        results = signals[:max_results]
        
        logger.info(f"🎯 选股完成: 处理了 {processed_count} 只股票，筛选出 {len(results)} 个信号")
        
        return results
    
    def _fetch_stock_data(self, symbol: str, time_level: TimeLevel, days: int):
        """获取股票数据（基于最近交易日）"""
        try:
            if time_level == TimeLevel.MIN_30:
                collection_name = "stock_kline_30min"
            elif time_level == TimeLevel.MIN_5:
                collection_name = "stock_kline_5min"
            else:
                collection_name = "stock_kline_daily"
            
            collection = self.db_handler.get_collection(collection_name)
            
            # 获取最近的交易日作为结束日期
            current_date = datetime.now().date()
            end_trading_date = get_nearest_trading_date(current_date, direction='backward')
            
            if not end_trading_date:
                logger.error(f"❌ 无法获取最近交易日")
                return None
            
            # 计算开始日期
            start_date = end_trading_date - timedelta(days=days)
            end_date = end_trading_date
            
            logger.debug(f"📅 查询数据范围: {start_date} 到 {end_date} (最近交易日)")
            
            if time_level == TimeLevel.DAILY:
                # 日线数据使用trade_date字段（YYYYMMDD格式）
                cursor = collection.find({
                    "ts_code": symbol,
                    "trade_date": {
                        "$gte": start_date.strftime("%Y%m%d"),
                        "$lte": end_date.strftime("%Y%m%d")
                    }
                }).sort("trade_date", 1)
            else:
                # 分钟数据使用trade_time字段（YYYY-MM-DD HH:MM:SS格式）
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())
                
                cursor = collection.find({
                    "ts_code": symbol,
                    "trade_time": {
                        "$gte": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        "$lte": end_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    }
                }).sort("trade_time", 1)
            
            # 转换为缠论引擎需要的格式
            data = []
            for doc in cursor:
                try:
                    # 根据时间级别处理不同的时间字段
                    if time_level == TimeLevel.DAILY:
                        timestamp = datetime.strptime(doc['trade_date'], '%Y%m%d')
                    else:
                        timestamp = datetime.strptime(doc['trade_time'], '%Y-%m-%d %H:%M:%S')
                    
                    kline_data = {
                        'timestamp': timestamp,
                        'open': float(doc['open']),
                        'high': float(doc['high']),
                        'low': float(doc['low']),
                        'close': float(doc['close']),
                        'volume': float(doc.get('vol', doc.get('volume', 0)))
                    }
                    data.append(kline_data)
                except (ValueError, KeyError) as e:
                    continue
            
            logger.debug(f"📊 {symbol} 获取到 {len(data)} 条{time_level.value}数据")
            return data
            
        except Exception as e:
            logger.error(f"❌ 获取股票数据失败 {symbol}: {e}")
            return None


# 向后兼容的类名
BackchiStockSelector = SimpleBackchiStockSelector


if __name__ == "__main__":
    # 测试选股器
    selector = SimpleBackchiStockSelector()
    results = selector.run_stock_selection(max_results=10)
    
    print("\n🎯 选股结果:")
    for i, signal in enumerate(results, 1):
        print(f"{i}. {signal.symbol} - {signal.name}")
        print(f"   信号: {signal.signal_type}, 评分: {signal.overall_score:.1f}, 强度: {signal.signal_strength.value}")
        print(f"   建议: {signal.recommendation}")
        print(f"   描述: {signal.description}")
        if signal.entry_price:
            print(f"   入场价: {signal.entry_price:.2f}, 止损: {signal.stop_loss:.2f}, 止盈: {signal.take_profit:.2f}")
        print()