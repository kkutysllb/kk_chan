#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API服务启动脚本
"""

import uvicorn
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    # 启动API服务
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[current_dir],
        log_level="info"
    )