"""
摘要、Notion、PDF 相關路由

職責：僅處理 HTTP 請求/響應，業務邏輯委託給 Manager
"""
from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse, Response
import time
from typing import Optional

from models.routers import RefineRequest, SaveToNotionRequest, GeneratePdfRequest
from managers import SummaryManager

router = APIRouter(prefix="/api", tags=["summary"])


@router.post("/refine")
async def refine_summary(
    request: RefineRequest,
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key")
):
    """根據用戶反饋調整筆記"""
    try:
        manager = SummaryManager()
        result = await manager.refine_summary(
            request.original_summary, 
            request.user_feedback,
            gemini_api_key=x_gemini_api_key
        )
        return result
    except ValueError as e:
        return JSONResponse(status_code=401, content={"error": str(e)})
    except Exception as e:
        msg = str(e)
        if "403" in msg or "429" in msg or "Quota" in msg or "API key" in msg:
             return JSONResponse(status_code=403, content={"error": msg})
        return JSONResponse(status_code=500, content={"error": msg})


@router.post("/save-to-notion")
async def save_to_notion(
    request: SaveToNotionRequest,
    x_notion_api_key: Optional[str] = Header(None, alias="X-Notion-API-Key"),
    x_notion_database_id: Optional[str] = Header(None, alias="X-Notion-Database-ID")
):
    """確認後儲存到 Notion"""
    manager = SummaryManager()
    result = manager.save_to_notion(
        request.title, 
        request.blocks,
        notion_api_key=x_notion_api_key,
        notion_database_id=x_notion_database_id
    )
    
    if not result["success"]:
        # Check if error message implies auth failure
        error_msg = str(result["error"])
        if "API Key" in error_msg or "401" in error_msg or "403" in error_msg:
             return JSONResponse(status_code=403, content={"error": error_msg})
        return JSONResponse(status_code=500, content={"error": error_msg})
    
    return {"status": "success", "message": result["message"]}


@router.post("/generate-pdf")
async def generate_pdf_endpoint(request: GeneratePdfRequest):
    """生成 PDF 檔案"""
    try:
        manager = SummaryManager()
        pdf_bytes = manager.generate_pdf(request.title, request.blocks)

        safe_filename = f"summary_{int(time.time())}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'},
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
