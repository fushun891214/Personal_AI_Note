from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from services import parser, llm, notion

app = FastAPI()

from typing import List

# 1. API Endpoints
@app.post("/api/upload")
async def upload_document(files: List[UploadFile] = File(...)):
    combined_text = ""
    file_names = []
    file_processing_results = []  # Track processing status for each file

    for file in files:
        filename = file.filename
        file_names.append(filename)
        content_bytes = await file.read()

        # Initialize file processing result
        result = {
            "filename": filename,
            "status": "success",
            "message": "",
            "method": "",
            "char_count": 0
        }

        extracted_text = ""
        try:
            if filename.lower().endswith(".pdf"):
                # Try pypdf first (fast, free)
                extracted_text = parser.extract_text_from_pdf(content_bytes)

                # Fallback to Gemini if pypdf fails or extracts too little
                if not extracted_text or len(extracted_text.strip()) < 50:
                    print(f"[FALLBACK] pypdf failed for {filename}, using Gemini...")
                    extracted_text = llm.extract_pdf_with_gemini(content_bytes, filename)
                    result["method"] = "gemini" if extracted_text else "failed"
                else:
                    result["method"] = "pypdf"

            elif filename.lower().endswith((".ppt", ".pptx")):
                extracted_text = parser.extract_text_from_ppt(content_bytes)
                result["method"] = "python-pptx"

            elif filename.lower().endswith((".mp3", ".wav", ".m4a", ".ogg")):
                # Audio uses Gemini
                await file.seek(0)
                extracted_text = llm.transcribe_audio(file)
                result["method"] = "gemini"

            else:
                result["status"] = "skipped"
                result["message"] = "不支援的檔案格式"
                print(f"[SKIP] Unsupported file: {filename}")
                file_processing_results.append(result)
                continue

            # Check if extraction succeeded
            if extracted_text:
                combined_text += f"\n\n--- Source: {filename} ---\n\n" + extracted_text
                result["char_count"] = len(extracted_text)
            else:
                result["status"] = "failed"
                result["message"] = "無法提取文字內容"

        except Exception as e:
            result["status"] = "failed"
            result["message"] = str(e)
            print(f"[ERROR] Processing {filename}: {e}")

        file_processing_results.append(result)

    # Count successful files
    successful_files = len([r for r in file_processing_results if r["status"] == "success"])

    # If all files failed, return error
    if not combined_text:
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": "所有文件提取失敗，無法生成摘要",
                "file_details": file_processing_results,
                "total_files": len(files),
                "successful_files": 0
            }
        )

    # 2. Summarize
    summary = llm.summarize_content(combined_text)

    # 3. Save to Notion (if summary is valid)
    notion_status = "Skipped (Summary failed)"
    title = f"Note: {', '.join(file_names)}"
    if len(title) > 100:
        title = title[:97] + "..."

    if "Error" not in summary:
        notion_status = notion.create_notion_page(title, summary)

    return {
        "summary": summary,
        "notion_status": notion_status,
        "file_details": file_processing_results,
        "total_files": len(files),
        "successful_files": successful_files
    }

# 2. Mount Static Files (Frontend) - Must be after API routes to avoid conflict
# This serves index.html at root "/"
app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")
