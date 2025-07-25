#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置
"""

import logging
import sys
from datetime import datetime

def setup_logging():
    """设置日志配置"""
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 文件处理器（可选）
    try:
        file_handler = logging.FileHandler(f'logs/api_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
    except:
        file_handler = None
    
    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    if file_handler:
        root_logger.addHandler(file_handler)
    
    # 禁用一些第三方库的日志
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)