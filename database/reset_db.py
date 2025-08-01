#!/usr/bin/env python3
"""
重置数据库连接脚本
用于清除缓存的数据库实例，确保使用最新的连接配置
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def main():
    try:
        from database.db_handler import reset_db_handler, get_db_handler
        
        print("🔄 重置数据库连接...")
        
        # 重置单例实例
        reset_db_handler()
        
        # 重新初始化
        db = get_db_handler()
        
        print("✅ 数据库连接重置完成")
        
        # 测试连接
        if hasattr(db, 'local_available') and db.local_available:
            print("📍 本地数据库连接正常")
        else:
            print("❌ 本地数据库连接异常")
            
        if hasattr(db, 'cloud_available') and db.cloud_available:
            print("🌐 云端数据库连接正常")
        else:
            print("💡 云端数据库连接已跳过（API接口分析模式）")
            
    except Exception as e:
        print(f"❌ 重置数据库连接失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()