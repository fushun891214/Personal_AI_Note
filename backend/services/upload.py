from typing import Dict, Any
from fastapi import UploadFile
from . import parser, llm

async def process_file(file: UploadFile) -> Dict[str, Any]:
    """
    處理單個文件的文字提取

    流程：檢查格式 → 調用對應 service → 返回結果

    Returns:
        包含 filename, status, message, method, char_count, extracted_text 的字典
    """
    filename = file.filename
    lower_name = filename.lower()

    result = {
        "filename": filename,
        "status": "success",
        "message": "",
        "method": "",
        "char_count": 0,
        "extracted_text": ""
    }

    # 檢查格式是否支援
    is_supported = (lower_name.endswith(".pdf") or
                   lower_name.endswith((".ppt", ".pptx")) or
                   lower_name.endswith((".mp3", ".wav", ".m4a", ".ogg")))

    if not is_supported:
        result["status"] = "skipped"
        result["message"] = "不支援的檔案格式"
        print(f"[SKIP] Unsupported file: {filename}")
        return result

    # 根據類型調用 service 提取文字
    tmp_path = None
    try:
        # 保存到臨時文件
        tmp_path = parser.save_upload_to_temp(file)

        # 根據類型調用 Gemini 提取
        if lower_name.endswith((".pdf", ".ppt", ".pptx")):
            extracted_text = await llm.extract_document_from_path(tmp_path, filename)
        else:  # audio
            extracted_text = await llm.transcribe_audio_from_path(tmp_path)

        # 設置結果
        result["extracted_text"] = extracted_text
        result["char_count"] = len(extracted_text)
        result["method"] = "gemini"

    except Exception as e:
        result["status"] = "failed"
        result["message"] = str(e)
        print(f"[ERROR] Processing {filename}: {e}")

    finally:
        # 統一清理臨時文件
        if tmp_path:
            parser.cleanup_temp_file(tmp_path)

    return result
