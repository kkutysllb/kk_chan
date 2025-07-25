#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证中间件（简化版）
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件（暂无实际认证逻辑）"""
    
    async def dispatch(self, request: Request, call_next):
        # 暂时跳过认证，直接处理请求
        response = await call_next(request)
        return response