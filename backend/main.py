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