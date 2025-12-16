from typing import List
from fastapi import UploadFile
from . import parser

# 支援的文件格式
SUPPORTED_EXTENSIONS = (".pdf", ".ppt", ".pptx", ".mp3", ".wav", ".m4a", ".ogg")


async def save_files_to_temp(files: List[UploadFile]) -> List[str]:
    """
    保存上傳的文件到臨時目錄（fail-fast 模式）

    流程：
    1. 先驗證所有文件格式
    2. 格式都有效才開始保存
    3. 任何失敗都直接拋出異常

    Args:
        files: 上傳的文件列表

    Returns:
        臨時文件路徑列表

    Raises:
        ValueError: 不支援的檔案格式
        IOError: 檔案保存失敗
    """
    # 1. 先驗證所有文件格式
    for file in files:
        if not file.filename.lower().endswith(SUPPORTED_EXTENSIONS):
            raise ValueError(f"不支援的檔案格式: {file.filename}")

    # 2. 格式都有效，開始保存
    return [parser.save_upload_to_temp(file) for file in files]
