#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KK缠论分析API - 应用入口
标准FastAPI应用结构
"""

from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 导入路由
from routers import router

# 创建FastAPI应用实例
app = FastAPI(
    title="KK缠论分析API",
    description="为Vue前端提供缠论分析数据的代理服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(router, prefix="", tags=["API"])

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
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
    """通用异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "服务器内部错误",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# 应用启动
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动KK缠论分析API服务...")
    print("📍 服务地址: http://localhost:8000")
    print("📋 API文档: http://localhost:8000/docs")
    print("🔧 健康检查: http://localhost:8000/health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )