#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """应用设置"""
    
    # 基础配置
    APP_NAME: str = "KK缠论量化分析API"
    VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 跨域配置
    ALLOWED_ORIGINS: List[str] = ["*"] 
    
    
    # 数据库配置
    MONGO_URI: str = "mongodb://localhost:27017/quant_analysis"
    MONGO_URI_CLOUD: str = ""
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    """获取设置实例"""
    return Settings()