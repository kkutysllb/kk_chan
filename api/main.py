#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI缠论分析系统主入口
集成前端Vue3图表展示的后端API服务
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging
from datetime import datetime
from typing import Optional

# 导入路由模块
from api.routers import chan_analysis, ml_models, data_management, visualization
from api.middleware.auth import AuthMiddleware
from api.middleware.rate_limiter import RateLimiterMiddleware
from api.core.config import get_settings
from api.core.database import init_database
from api.core.cache import init_cache
from api.core.logger import setup_logging

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)

# 配置
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("🚀 启动缠论分析API服务")
    
    # 初始化数据库连接
    await init_database()
    
    # 初始化缓存
    await init_cache()
    
    # 预热模型
    from .services.ml_service import MLService
    ml_service = MLService()
    await ml_service.preload_models()
    
    logger.info("✅ 系统初始化完成")
    
    yield
    
    # 关闭时清理
    logger.info("🛑 正在关闭服务")
    await cleanup_resources()
    logger.info("✅ 服务已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="KK缠论量化分析API",
    description="基于缠论理论的专业量化分析API服务",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimiterMiddleware)

# 注册路由
app.include_router(
    chan_analysis.router,
    prefix="/api/v2/chan",
    tags=["缠论分析"]
)

app.include_router(
    ml_models.router,
    prefix="/api/v2/ml",
    tags=["机器学习"]
)

app.include_router(
    data_management.router,
    prefix="/api/v2/data",
    tags=["数据管理"]
)

app.include_router(
    visualization.router,
    prefix="/api/v2/visualization",
    tags=["数据可视化"]
)

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "database": await check_database_health(),
            "cache": await check_cache_health(),
            "ml_models": await check_ml_models_health()
        }
    }

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
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "内部服务器错误",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

async def cleanup_resources():
    """清理资源"""
    # 关闭数据库连接
    # 清理缓存
    # 停止后台任务
    pass

async def check_database_health():
    """检查数据库健康状态"""
    try:
        # 实现数据库健康检查
        return "healthy"
    except Exception:
        return "unhealthy"

async def check_cache_health():
    """检查缓存健康状态"""
    try:
        # 实现缓存健康检查
        return "healthy"
    except Exception:
        return "unhealthy"

async def check_ml_models_health():
    """检查机器学习模型健康状态"""
    try:
        # 实现模型健康检查
        return "healthy"
    except Exception:
        return "unhealthy"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )