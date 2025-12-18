"""
文件上傳相關路由

職責：處理 HTTP 請求/響應，統一錯誤處理
"""
from fastapi import APIRouter, UploadFile, File, Header
from fastapi.responses import JSONResponse
from typing import List, Optional

from managers import UploadManager

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
async def upload_document(
    files: List[UploadFile] = File(...),
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key")
):
    """
    文件上傳 API
    返回預覽用的 PDF URL 和初始筆記 JSON
    """
    try:
        # 嚴格限制僅支援 PDF
        for file in files:
            if not file.filename.lower().endswith(".pdf"):
                return JSONResponse(
                    status_code=400, 
                    content={"error": f"不支援的檔案格式: {file.filename}。僅支援 .pdf 檔案。"}
                )

        manager = UploadManager()
        result = await manager.process_upload(files, gemini_api_key=x_gemini_api_key)
        return result
    except ValueError as e:
        return JSONResponse(status_code=401, content={"error": str(e)})
    except Exception as e:
        msg = str(e)
        # Simple heuristic to map downstream API errors to 403/429
        if "403" in msg or "429" in msg or "Quota" in msg or "API key" in msg or "permission" in msg.lower():
             return JSONResponse(status_code=403, content={"error": msg})
        return JSONResponse(status_code=500, content={"error": msg})
