#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
限流中间件（简化版）
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import functools

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """限流中间件（暂无实际限流逻辑）"""
    
    async def dispatch(self, request: Request, call_next):
        # 暂时跳过限流，直接处理请求
        response = await call_next(request)
        return response

def rate_limit(calls: int, period: int):
    """限流装饰器（暂无实际限流逻辑）"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 暂时跳过限流检查
            return await func(*args, **kwargs)
        return wrapper
    return decorator