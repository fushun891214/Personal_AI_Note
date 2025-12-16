import google.generativeai as genai
from config import settings

# 初始化 Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


def transcribe_audio_from_path(audio_path: str) -> str:
    """
    從文件路徑轉錄音頻（使用 Gemini）

    Args:
        audio_path: 音頻文件的絕對路徑

    Returns:
        轉錄的文字
    """
    try:
        if not settings.GEMINI_API_KEY:
            print("[GEMINI API] Error: API Key not found for audio transcription.")
            return ""

        # Upload to Gemini
        audio_file = genai.upload_file(path=audio_path)

        # Generate transcript
        model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        response = model.generate_content([
            "請生成這份音頻文件的轉錄。請直接輸出文字，不要添加任何解釋或說明。",
            audio_file
        ])
        return response.text

    except Exception as e:
        print(f"[GEMINI API] Error transcribing audio: {e}")
        return ""


def extract_document_from_path(file_path: str, filename: str = "") -> str:
    """
    從文件路徑提取文件內容（使用 Gemini）

    支援格式：PDF, PPT, PPTX 等
    成本：約 $0.0002/頁

    Args:
        file_path: 文件的絕對路徑
        filename: 文件名（用於日誌）

    Returns:
        提取的文字
    """
    try:
        if not settings.GEMINI_API_KEY:
            print("[GEMINI API] Error: API Key not found.")
            return ""

        print(f"[GEMINI API] Processing document: {filename or file_path}")

        # Upload file to Gemini
        uploaded_file = genai.upload_file(path=file_path)

        # Extract text using Gemini
        model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        response = model.generate_content([
            "請仔細閱讀這份文件的所有內容，並提取完整的文字。"
            "包含標題、段落、列表、表格等所有文字內容。"
            "請直接輸出文字，不要添加任何解釋或說明。",
            uploaded_file
        ])

        extracted_text = response.text
        print(f"[GEMINI API] Success: Extracted {len(extracted_text)} characters")
        return extracted_text

    except Exception as e:
        print(f"[GEMINI API] Failed to extract document: {e}")
        return ""

def summarize_content(text: str) -> dict:
    """
    使用 Gemini 生成標題和摘要

    Returns:
        {
            "title": "生成的標題",
            "summary": "結構化摘要"
        }
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API Key not found")

    if not text.strip():
        raise ValueError("No text to summarize")

    prompt = (
        "你是專業的會議筆記整理專家。請分析以下文件內容，生成標題和結構化摘要。\n\n"
        "輸出格式（JSON）：\n"
        "{\n"
        '  "title": "簡潔的標題（10-50字，概括文件主題）",\n'
        '  "summary": "結構化的 Markdown 摘要"\n'
        "}\n\n"
        "摘要格式要求：\n"
        "1. 使用**粗體文字**作為主要段落標題（如：**討論**、**重點**、**行動項目**等）\n"
        "2. 每個段落下使用項目符號（-）列出要點\n"
        "3. 如有子項目或詳細步驟，使用縮排的子項目符號\n"
        "4. 重要關鍵字使用粗體（**文字**）\n"
        "5. 內容要簡潔精煉，每個要點不超過一行\n"
        "6. 按主題分組內容（例如：討論主題、決策事項、行動計劃等）\n\n"
        "輸出範例：\n"
        "{\n"
        '  "title": "工程發布流程改進討論",\n'
        '  "summary": "**討論**\\n- 切換筆記和資料庫之間的連結問題\\n- 用戶認證和評論的問題\\n- 創建新的、更易管理的工程發布方法\\n  - 創建一個新的資料庫來處理發布\\n  - 解決關係和連線的問題"\n'
        "}\n\n"
        "文件內容：\n"
        f"{text}"
    )

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        response = model.generate_content(prompt)

        # 解析 JSON 響應
        import json
        result = json.loads(response.text)

        return {
            "title": result.get("title", "未命名筆記"),
            "summary": result.get("summary", "")
        }
    except json.JSONDecodeError:
        # 如果 LLM 沒返回正確的 JSON，使用默認值
        return {
            "title": "筆記摘要",
            "summary": response.text
        }
    except Exception as e:
        raise RuntimeError(f"Failed to generate summary: {e}")
