#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心工具函数
"""

from typing import Any, Dict, List, Union
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


def remove_object_ids(data: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
    """
    递归移除数据中的MongoDB ObjectId字段
    
    Args:
        data: 要处理的数据，可以是字典、列表或其他类型
        
    Returns:
        处理后的数据，移除了所有_id ObjectId字段
    """
    if isinstance(data, dict):
        # 处理字典类型
        cleaned_data = {}
        for key, value in data.items():
            if key == '_id' and isinstance(value, ObjectId):
                # 跳过ObjectId类型的_id字段
                continue
            else:
                # 递归处理其他字段
                cleaned_data[key] = remove_object_ids(value)
        return cleaned_data
    
    elif isinstance(data, list):
        # 处理列表类型
        return [remove_object_ids(item) for item in data]
    
    else:
        # 其他类型直接返回
        return data


def safe_serialize_response(data: Any) -> Any:
    """
    安全序列化响应数据，确保没有不可序列化的类型
    
    Args:
        data: 要序列化的数据
        
    Returns:
        可安全序列化的数据
    """
    try:
        # 首先移除ObjectId
        cleaned_data = remove_object_ids(data)
        
        # 如果需要，还可以处理其他不可序列化的类型
        # 例如datetime对象转换为ISO格式字符串等
        
        return cleaned_data
    except Exception as e:
        logger.error(f"数据序列化失败: {e}")
        return {"error": "数据序列化失败", "message": str(e)}


def clean_db_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    清理单个数据库文档，移除ObjectId
    
    Args:
        doc: 数据库文档
        
    Returns:
        清理后的文档
    """
    if doc is None:
        return None
    
    # 创建副本避免修改原始数据
    cleaned_doc = doc.copy()
    
    # 移除ObjectId类型的_id字段
    if '_id' in cleaned_doc and isinstance(cleaned_doc['_id'], ObjectId):
        del cleaned_doc['_id']
    
    return cleaned_doc


def clean_db_documents(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    清理数据库文档列表，移除ObjectId
    
    Args:
        docs: 数据库文档列表
        
    Returns:
        清理后的文档列表
    """
    if not docs:
        return []
    
    return [clean_db_document(doc) for doc in docs if doc is not None]