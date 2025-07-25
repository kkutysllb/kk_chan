#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理API路由
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from api.core.utils import clean_db_document, clean_db_documents

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/stocks")
async def get_stock_list(
    market: Optional[str] = Query(None, description="市场"),
    sector: Optional[str] = Query(None, description="行业"),
    limit: int = Query(100, description="数量限制"),
    offset: int = Query(0, description="偏移量")
):
    """获取股票列表"""
    try:
        from api.core.database import init_database, get_database
        
        # 初始化数据库连接
        await init_database()
        db = await get_database()
        
        if db is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        
        # 构建查询条件
        query = {}
        if market:
            if market == "深交所" or market == "SZ":
                query["ts_code"] = {"$regex": r"\.SZ$"}
            elif market == "上交所" or market == "SH":
                query["ts_code"] = {"$regex": r"\.SH$"}
        
        if sector:
            query["industry"] = {"$regex": sector, "$options": "i"}
        
        # 查询股票数据
        cursor = db.infrastructure_stock_basic.find(query).skip(offset).limit(limit)
        
        stocks = []
        async for doc in cursor:
            market_name = "深交所" if ".SZ" in doc.get("ts_code", "") else "上交所"
            
            stocks.append({
                "symbol": doc.get("ts_code", ""),
                "name": doc.get("name", ""),
                "market": market_name,
                "sector": doc.get("industry", ""),
                "area": doc.get("area", ""),
                "list_date": doc.get("list_date", ""),
                "market_type": doc.get("market", ""),
                "act_name": doc.get("act_name", ""),
                "cnspell": doc.get("cnspell", "")
            })
        
        # 获取总数
        total_count = await db.infrastructure_stock_basic.count_documents(query)
        
        return {
            "success": True,
            "data": stocks,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "message": f"成功获取 {len(stocks)} 条股票数据"
        }
    except Exception as e:
        logger.error(f"获取股票列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_stocks(q: str = Query(..., description="搜索关键词")):
    """搜索股票"""
    try:
        from api.core.database import init_database, get_database
        
        # 初始化数据库连接
        await init_database()
        db = await get_database()
        
        if db is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        
        # 构建搜索条件
        search_conditions = []
        
        # 搜索股票代码
        if q:
            search_conditions.append({"ts_code": {"$regex": q, "$options": "i"}})
            search_conditions.append({"name": {"$regex": q, "$options": "i"}})
            # 如果是纯数字，也搜索代码的数字部分
            if q.isdigit():
                search_conditions.append({"ts_code": {"$regex": f"^{q}", "$options": "i"}})
        
        if not search_conditions:
            return {
                "success": True,
                "data": [],
                "message": "请输入搜索关键词"
            }
        
        # 执行搜索
        query = {"$or": search_conditions}
        cursor = db.infrastructure_stock_basic.find(query).limit(20)
        
        results = []
        async for doc in cursor:
            # 计算匹配度
            match_score = 0.5  # 基础分
            if q.upper() in doc.get("ts_code", "").upper():
                match_score += 0.4
            if q in doc.get("name", ""):
                match_score += 0.3
            if doc.get("ts_code", "").startswith(q):
                match_score += 0.2
                
            market_name = "深交所" if ".SZ" in doc.get("ts_code", "") else "上交所"
            
            results.append({
                "symbol": doc.get("ts_code", ""),
                "name": doc.get("name", ""),
                "market": market_name,
                "industry": doc.get("industry", ""),
                "area": doc.get("area", ""),
                "list_date": doc.get("list_date", ""),
                "match_score": round(match_score, 2)
            })
        
        # 按匹配度排序
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "success": True,
            "data": results,
            "total": len(results),
            "message": f"找到 {len(results)} 个匹配结果"
        }
    except Exception as e:
        logger.error(f"搜索股票失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock_info/{symbol}")
async def get_stock_info(symbol: str):
    """获取股票基本信息"""
    try:
        from api.core.database import init_database, get_database
        
        # 初始化数据库连接
        await init_database()
        db = await get_database()
        
        if db is None:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        
        # 查询股票基本信息
        stock_info = await db.infrastructure_stock_basic.find_one({"ts_code": symbol})
        
        if not stock_info:
            raise HTTPException(status_code=404, detail=f"未找到股票 {symbol}")
        
        # 清理ObjectId
        stock_info = clean_db_document(stock_info)
        
        # 查询最新价格数据
        latest_price = await db.stock_kline_daily.find_one(
            {"ts_code": symbol},
            sort=[("trade_date", -1)]
        )
        
        # 清理ObjectId
        latest_price = clean_db_document(latest_price)
        
        market_name = "深交所" if ".SZ" in symbol else "上交所"
        
        result_data = {
            "ts_code": stock_info.get("ts_code", ""),
            "name": stock_info.get("name", ""),
            "market": market_name,
            "sector": stock_info.get("industry", ""),
            "area": stock_info.get("area", ""),
            "list_date": stock_info.get("list_date", ""),
            "act_name": stock_info.get("act_name", ""),
            "cnspell": stock_info.get("cnspell", "")
        }
        
        # 如果有价格数据，添加价格信息
        if latest_price:
            result_data.update({
                "current_price": latest_price.get("close", 0),
                "change": latest_price.get("change", 0),
                "pct_change": latest_price.get("pct_change", 0),
                "volume": latest_price.get("vol", 0),
                "amount": latest_price.get("amount", 0),
                "trade_date": latest_price.get("trade_date", "")
            })
        
        return {
            "success": True,
            "symbol": symbol,
            "data": result_data,
            "message": f"成功获取 {symbol} 的基本信息"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))