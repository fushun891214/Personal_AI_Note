from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel
from typing import List, Dict, Any

from managers import upload_manager
from services import llm, notion

app = FastAPI()

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)
# Mount static files for PDF preview
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

class RefineRequest(BaseModel):
    original_summary: Dict[str, Any]
    user_feedback: str

class SaveToNotionRequest(BaseModel):
    title: str
    blocks: List[Any]

@app.post("/api/upload")
async def upload_document(files: List[UploadFile] = File(...)):
    """
    文件上傳 API
    返回預覽用的 PDF URL 和初始筆記 JSON，不自動存 Notion
    """
    manager = upload_manager.UploadManager()
    result = await manager.process_upload(files)

    if result.get("error"):
        return JSONResponse(status_code=400, content=result)

    return result

@app.post("/api/refine")
async def refine_summary(request: RefineRequest):
    """
    根據用戶反饋調整筆記
    """
    try:
        refined_summary = await llm.refine_summary(request.original_summary, request.user_feedback)
        return refined_summary
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/save-to-notion")
async def save_to_notion(request: SaveToNotionRequest):
    """
    確認後儲存到 Notion
    """
    result = notion.create_notion_page(request.title, request.blocks)
    if "Error" in result:
        return JSONResponse(status_code=500, content={"error": result})
    return {"status": "success", "message": result}