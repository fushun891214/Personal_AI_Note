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
    try:
        extracted_text = ""
        method = ""

        if lower_name.endswith(".pdf"):
            # 使用 Gemini Vision 提取 PDF（支援電子 PDF 和掃描 PDF）
            tmp_path = parser.save_upload_to_temp(file)
            try:
                extracted_text = llm.extract_pdf_from_path(tmp_path, filename)
                method = "gemini-vision"
            finally:
                parser.cleanup_temp_file(tmp_path)

        elif lower_name.endswith((".ppt", ".pptx")):
            content_bytes = await file.read()
            extracted_text = parser.extract_text_from_ppt(content_bytes)
            method = "python-pptx"

        else:  # audio
            # 保存到臨時文件（parser 會處理文件讀取）
            tmp_path = parser.save_upload_to_temp(file)
            try:
                extracted_text = llm.transcribe_audio_from_path(tmp_path)
                method = "gemini"
            finally:
                parser.cleanup_temp_file(tmp_path)

        # 設置結果
        if extracted_text:
            result["extracted_text"] = extracted_text
            result["char_count"] = len(extracted_text)
            result["method"] = method
        else:
            result["status"] = "failed"
            result["message"] = "無法提取文字內容"

    except Exception as e:
        result["status"] = "failed"
        result["message"] = str(e)
        print(f"[ERROR] Processing {filename}: {e}")

    return result
