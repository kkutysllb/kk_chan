#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端代理服务器
用于连接Vue前端和Python缠论分析后端
"""

import json
import asyncio
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 导入缠论分析模块
from chan_api_v2 import ChanDataAPIv2

app = FastAPI(
    title="KK缠论分析API",
    description="为Vue前端提供缠论分析数据的代理服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化缠论API
chan_api = ChanDataAPIv2()

# JSON序列化处理函数
def clean_nan_values(obj):
    """处理数据中的NaN值，将其转换为None"""
    if isinstance(obj, dict):
        return {key: clean_nan_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj

# 请求模型
class AnalysisRequest(BaseModel):
    symbol: str
    timeframe: str = "daily"
    days: int = 90
    min_bi_length: Optional[int] = 5
    min_xd_bi_count: Optional[int] = 3
    fenxing_threshold: Optional[float] = 0.001

class StockInfo(BaseModel):
    value: str
    label: str
    name: str

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "KK缠论分析API服务",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/stocks", response_model=List[StockInfo])
async def get_stocks(query: str = Query("", description="搜索关键字")):
    """获取股票列表"""
    try:
        stocks = chan_api.get_symbols_list(query)
        return stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票列表失败: {str(e)}")

@app.get("/analysis")
async def get_analysis(
    symbol: str = Query(..., description="股票代码"),
    timeframe: str = Query("daily", description="时间级别"),
    days: int = Query(90, description="分析天数")
):
    """获取缠论分析数据"""
    try:
        print(f"🔍 API请求: symbol={symbol}, timeframe={timeframe}, days={days}")
        
        # 调用缠论分析
        result = chan_api.analyze_symbol_complete(
            symbol=symbol,
            timeframe=timeframe,
            days=days,
            analysis_level="complete"
        )
        
        # 清理NaN值
        cleaned_result = clean_nan_values(result)
        
        print(f"✅ 分析完成，返回数据")
        return cleaned_result
    
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/analysis")
async def post_analysis(request: AnalysisRequest):
    """POST方式获取缠论分析数据"""
    try:
        print(f"🔍 POST分析请求: {request.dict()}")
        
        result = chan_api.analyze_symbol_complete(
            symbol=request.symbol,
            timeframe=request.timeframe,
            days=request.days,
            analysis_level="complete"
        )
        
        print(f"✅ POST分析完成")
        return result
    
    except Exception as e:
        print(f"❌ POST分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/analysis/save")
async def save_analysis(data: Dict[str, Any]):
    """保存分析结果"""
    try:
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        symbol = data.get('meta', {}).get('symbol', 'unknown')
        timeframe = data.get('meta', {}).get('timeframe', 'daily')
        
        filename = f"analysis_{symbol}_{timeframe}_{timestamp}.json"
        filepath = Path(filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        return {
            "success": True,
            "message": "分析结果保存成功",
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")

@app.get("/analysis/history")
async def get_analysis_history():
    """获取历史分析记录"""
    try:
        # 扫描当前目录下的分析文件
        analysis_files = list(Path('.').glob('analysis_*.json'))
        
        history = []
        for file in sorted(analysis_files, key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    meta = data.get('meta', {})
                    
                    history.append({
                        'filename': file.name,
                        'symbol': meta.get('symbol'),
                        'timeframe': meta.get('timeframe'),
                        'analysis_time': meta.get('analysis_time'),
                        'data_count': meta.get('data_count', 0),
                        'file_size': file.stat().st_size,
                        'created_time': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
            except Exception:
                continue
        
        return {
            "success": True,
            "count": len(history),
            "history": history[:20]  # 最多返回20条记录
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")

# 异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "服务器内部错误",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动KK缠论分析API服务...")
    print("📍 服务地址: http://localhost:8000")
    print("📋 API文档: http://localhost:8000/docs")
    print("🔧 健康检查: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )