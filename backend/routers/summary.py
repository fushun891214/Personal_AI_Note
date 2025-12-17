"""
摘要、Notion、PDF 相關路由

職責：僅處理 HTTP 請求/響應，業務邏輯委託給 Manager
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
import time

from models.schemas import RefineRequest, SaveToNotionRequest, GeneratePdfRequest
from managers.summary_manager import SummaryManager

router = APIRouter(prefix="/api", tags=["summary"])


@router.post("/refine")
async def refine_summary(request: RefineRequest):
    """根據用戶反饋調整筆記"""
    try:
        manager = SummaryManager()
        result = await manager.refine_summary(
            request.original_summary, request.user_feedback
        )
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/save-to-notion")
async def save_to_notion(request: SaveToNotionRequest):
    """確認後儲存到 Notion"""
    manager = SummaryManager()
    result = manager.save_to_notion(request.title, request.blocks)
    
    if not result["success"]:
        return JSONResponse(status_code=500, content={"error": result["error"]})
    
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
