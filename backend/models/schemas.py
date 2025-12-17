"""
API 請求/回應模型定義
"""
from pydantic import BaseModel
from typing import List, Dict, Any


class RefineRequest(BaseModel):
    """摘要調整請求"""
    original_summary: Dict[str, Any]
    user_feedback: str


class SaveToNotionRequest(BaseModel):
    """儲存到 Notion 請求"""
    title: str
    blocks: List[Any]


class GeneratePdfRequest(BaseModel):
    """生成 PDF 請求"""
    title: str
    blocks: List[Any]
