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
    # save to backend/uploads/temp
    upload_dir = os.path.join(os.getcwd(), "uploads", "temp")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    import uuid
    filename = f"{uuid.uuid4()}{suffix}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    return file_path

def cleanup_temp_file(path: str) -> None:
    """
    清理臨時文件

    Args:
        path: 文件路徑
    """
    if os.path.exists(path):
        os.remove(path)
