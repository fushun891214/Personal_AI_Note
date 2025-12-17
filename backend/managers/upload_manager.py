from typing import List, Dict, Any
from fastapi import UploadFile
from services import upload, llm, notion, parser


class UploadManager:
    """
    應用層 - 協調文件上傳的完整業務流程

    職責：
    1. 編排各個 service 的調用順序
    2. 處理業務邏輯（批次處理、錯誤處理）
    3. 構建響應數據

    不包含：
    - HTTP 相關邏輯（屬於 Controller）
    - 具體的文件解析邏輯（屬於 Services）
    """

    async def process_upload(self, files: List[UploadFile]) -> Dict[str, Any]:
        """
        處理多個文件上傳的完整流程（fail-fast 模式）

        流程：驗證格式 → 保存文件 → 生成摘要 → 返回預覽數據
        注意：不再自動同步到 Notion，也不立即清理臨時文件（供預覽用）
        """
        tmp_paths = []

        try:
            # 1. 保存所有文件（fail-fast：任何失敗都直接拋異常）
            # 這裡的 paths 是絕對路徑
            tmp_paths = await upload.save_files_to_temp(files)
            filenames = [file.filename for file in files]

            # 2. 一次性生成標題和 Notion blocks（所有文件）
            result = await llm.summarize_documents_from_paths(tmp_paths, filenames)

            # 3. 構建 PDF URL (假設只有一個 PDF，目前邏輯也是合併處理)
            # 將絕對路徑轉換為相對 URL
            pdf_urls = []
            import os
            for path in tmp_paths:
                # 取得檔名 (basename)
                basename = os.path.basename(path)
                # 構建靜態資源 URL: /uploads/temp/filename
                pdf_urls.append(f"/uploads/temp/{basename}")

            # 4. 返回成功響應（不存 Notion）
            return {
                "title": result["title"],
                "blocks": result["blocks"],
                "files": filenames,
                "pdf_urls": pdf_urls,  # 前端可用第一個
                "temp_paths": tmp_paths # 後端可選：傳回給前端稍微有點危險，但方便之後操作（或者靠 URL 反推）
            }

        except Exception as e:
            # 統一錯誤處理
            # 如果失敗，還是要清理文件
            for path in tmp_paths:
                parser.cleanup_temp_file(path)
                
            return {
                "error": True,
                "message": str(e)
            }
