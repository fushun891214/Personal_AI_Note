"""
Personal AI Note - Backend 應用入口

職責：
1. 初始化 FastAPI 應用
2. 掛載靜態檔案服務
3. 註冊路由模組
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from routers import upload, summary

app = FastAPI(title="Personal AI Note", version="1.0.0")

# 確保 uploads 目錄存在
os.makedirs("uploads", exist_ok=True)

# 掛載靜態檔案（用於 PDF 預覽）
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 註冊路由
app.include_router(upload.router)
app.include_router(summary.router)

# ==========================================
# Serve Frontend (SPA)
# ==========================================
from fastapi.responses import HTMLResponse

# In Docker: /app/backend is WORKDIR
# Frontend dist is at /app/frontend/dist (so ../frontend/dist)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    # Mount assets (JS, CSS, Images)
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
    
    # Catch-all route for SPA (Vue Router)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Skip API and Uploads (handled above)
        if full_path.startswith("api") or full_path.startswith("uploads"):
             from fastapi import HTTPException
             raise HTTPException(status_code=404)
        
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            with open(index_file, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="Frontend not found", status_code=404)
