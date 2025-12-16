import os
import tempfile
from fastapi import UploadFile


def save_upload_to_temp(file: UploadFile) -> str:
    """
    保存 UploadFile 到臨時文件

    Args:
        file: FastAPI UploadFile 對象

    Returns:
        臨時文件的絕對路徑
    """
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        return tmp.name

def cleanup_temp_file(path: str) -> None:
    """
    清理臨時文件

    Args:
        path: 文件路徑
    """
    if os.path.exists(path):
        os.remove(path)
