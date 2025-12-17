"""
文件上傳相關路由

職責：處理 HTTP 請求/響應，統一錯誤處理
"""
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List

from managers.upload_manager import UploadManager

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
async def upload_document(files: List[UploadFile] = File(...)):
    """
    文件上傳 API
    返回預覽用的 PDF URL 和初始筆記 JSON
    """
    try:
        manager = UploadManager()
        result = await manager.process_upload(files)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
