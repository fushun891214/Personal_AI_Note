from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from managers import upload_manager

app = FastAPI()

@app.post("/api/upload")
async def upload_document(files: List[UploadFile] = File(...)):
    """
    文件上傳 API
    職責：HTTP 路由，參數接收，調用 Manager，返回響應
    """
    manager = upload_manager.UploadManager()
    result = await manager.process_upload(files)

    if result.get("error"):
        return JSONResponse(status_code=400, content=result)

    return result

app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")
