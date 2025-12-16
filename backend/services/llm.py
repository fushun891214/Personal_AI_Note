import os
import tempfile
from fastapi import UploadFile
import google.generativeai as genai
from config import settings

# Initialize Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

def transcribe_audio(file: UploadFile) -> str:
    """Extract text from an audio file using Gemini."""
    try:
        if not settings.GEMINI_API_KEY:
            print("Error: Gemini API Key not found for audio transcription.")
            return ""

        # Save to temp file because genai.upload_file requires a path
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        try:
            # Upload to Gemini
            audio_file = genai.upload_file(path=tmp_path)

            # Generate transcript
            model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
            response = model.generate_content(
                ["Please generate a transcript of this audio file. Do not add any other text, just the transcript.", audio_file]
            )
            return response.text
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        print(f"Error processing audio: {e}")
        return ""

def extract_pdf_with_gemini(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from PDF using Gemini's vision capabilities.
    Works for both electronic PDFs and scanned PDFs.
    Cost: ~$0.0002 per page
    """
    try:
        if not settings.GEMINI_API_KEY:
            print("[GEMINI API] Error: API Key not found for PDF extraction.")
            return ""

        print(f"[GEMINI API] Processing PDF with vision: {filename}")

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            # Upload PDF to Gemini
            pdf_file = genai.upload_file(path=tmp_path)

            # Extract text using vision model
            model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
            response = model.generate_content([
                "請仔細閱讀這份 PDF 文件的所有內容，並提取完整的文字。"
                "包含標題、段落、列表、表格等所有文字內容。"
                "請直接輸出文字，不要添加任何解釋或說明。",
                pdf_file
            ])

            extracted_text = response.text
            print(f"[GEMINI API] Success: Extracted {len(extracted_text)} characters from {filename}")
            return extracted_text

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        print(f"[GEMINI API] Failed to extract PDF {filename}: {e}")
        return ""

def summarize_content(text: str) -> str:
    """Use Gemini to summarize the text into Notion-friendly Markdown."""
    if not settings.GEMINI_API_KEY:
        return "Error: Gemini API Key not found."
    
    if not text.strip():
        return "Error: No text could be extracted from the document."

    prompt = (
        "你是專業的會議筆記整理專家。請將以下文件內容整理成結構化的 Notion 格式摘要（Markdown）。\n\n"
        "格式要求：\n"
        "1. 使用**粗體文字**作為主要段落標題（如：**討論**、**重點**、**行動項目**等）\n"
        "2. 每個段落下使用項目符號（-）列出要點\n"
        "3. 如有子項目或詳細步驟，使用縮排的子項目符號\n"
        "4. 重要關鍵字使用粗體（**文字**）\n"
        "5. 內容要簡潔精煉，每個要點不超過一行\n"
        "6. 按主題分組內容（例如：討論主題、決策事項、行動計劃、表揚等）\n\n"
        "輸出範例：\n"
        "**討論**\n"
        "- 切換筆記和資料庫之間的連結問題\n"
        "- 用戶認證和評論的問題\n"
        "- 創建新的、更易管理的工程發布方法\n"
        "  - 創建一個新的資料庫來處理發布\n"
        "  - 解決關係和連線的問題\n\n"
        "文件內容：\n"
        f"{text}"
    )

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary: {e}"
