from typing import List, Dict, Any
from fastapi import UploadFile
from services import upload, llm, notion

class UploadManager:
    """
    應用層 - 協調文件上傳的完整業務流程

    職責：
    1. 編排各個 service 的調用順序
    2. 處理業務邏輯（文件循環、文字合併、錯誤處理）
    3. 構建響應數據

    不包含：
    - HTTP 相關邏輯（屬於 Controller）
    - 具體的文件解析邏輯（屬於 Services）
    """

    async def process_upload(self, files: List[UploadFile]) -> Dict[str, Any]:
        """
        處理多個文件上傳的完整流程

        流程：處理文件 → 合併文字 → 生成摘要 → 同步 Notion
        """
        # 1. 處理所有文件，提取文字（調用 upload service）
        file_results = []
        combined_text = ""

        for file in files:
            result = await upload.process_file(file)
            file_results.append(result)

            # 合併成功提取的文字
            if result["status"] == "success" and result.get("extracted_text"):
                combined_text += f"\n\n--- Source: {result['filename']} ---\n\n"
                combined_text += result["extracted_text"]

        # 2. 檢查是否所有文件都失敗
        successful_count = sum(1 for r in file_results if r["status"] == "success")
        if not combined_text:
            # 所有文件失敗，返回錯誤響應
            return {
                "error": True,
                "message": "所有文件提取失敗，無法生成摘要",
                "file_details": [{
                    "filename": r["filename"],
                    "status": r["status"],
                    "message": r["message"],
                    "method": r["method"],
                    "char_count": r["char_count"]
                } for r in file_results],
                "total_files": len(files),
                "successful_files": 0
            }

        # 3. 生成摘要（調用 llm service）
        summary = llm.summarize_content(combined_text)

        # 4. 同步到 Notion（調用 notion service）
        file_names = [r["filename"] for r in file_results]
        title = f"Note: {', '.join(file_names)}"
        if len(title) > 100:
            title = title[:97] + "..."

        if "Error" not in summary:
            notion_status = notion.create_notion_page(title, summary)
        else:
            notion_status = "Skipped (Summary failed)"

        # 5. 返回成功響應
        return {
            "summary": summary,
            "notion_status": notion_status,
            "file_details": [{
                "filename": r["filename"],
                "status": r["status"],
                "message": r["message"],
                "method": r["method"],
                "char_count": r["char_count"]
            } for r in file_results],
            "total_files": len(files),
            "successful_files": successful_count
        }
