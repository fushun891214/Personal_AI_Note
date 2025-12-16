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

        流程：驗證格式 → 保存文件 → 生成摘要 → 同步 Notion → 清理
        錯誤處理：任何失敗都直接返回錯誤訊息
        """
        tmp_paths = []

        try:
            # 1. 保存所有文件（fail-fast：任何失敗都直接拋異常）
            tmp_paths = await upload.save_files_to_temp(files)
            filenames = [file.filename for file in files]

            # 2. 一次性生成標題和 Notion blocks（所有文件）
            result = await llm.summarize_documents_from_paths(tmp_paths, filenames)

            # 3. 同步到 Notion
            notion_status = notion.create_notion_page(result["title"], result["blocks"])

            # 4. 返回成功響應
            return {
                "title": result["title"],
                "notion_status": notion_status,
                "files": filenames  # 簡單的檔案名稱列表
            }

        except Exception as e:
            # 統一錯誤處理
            return {
                "error": True,
                "message": str(e)
            }

        finally:
            # 清理所有臨時文件
            for path in tmp_paths:
                parser.cleanup_temp_file(path)
