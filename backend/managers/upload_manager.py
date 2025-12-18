"""
文件上傳業務邏輯

職責：
1. 協調 services 的調用
2. 編排業務流程
3. 構建響應數據

錯誤處理：拋出異常，由 Router 層統一處理
"""
import os
from typing import List, Dict, Any
from fastapi import UploadFile

from services import upload, llm, parser


class UploadManager:
    """應用層 - 協調文件上傳的完整業務流程"""

    async def process_upload(
        self, 
        files: List[UploadFile], 
        gemini_api_key: str = None
    ) -> Dict[str, Any]:
        """
        處理多個文件上傳的完整流程

        流程：保存文件 → 生成摘要 → 返回預覽數據
        
        Raises:
            Exception: 當任何步驟失敗時，會清理已保存的臨時文件後再拋出
        """
        tmp_paths = []

        try:
            # 1. 保存所有文件
            tmp_paths = await upload.save_files_to_temp(files)
            filenames = [file.filename for file in files]

            # 2. 生成標題和 Notion blocks (靜態選單，不調用 LLM)
            result = await llm.get_static_options_menu(
                tmp_paths, 
                filenames,
                api_key=gemini_api_key
            )

            # 3. 構建 PDF URL
            pdf_urls = []
            for path in tmp_paths:
                basename = os.path.basename(path)
                pdf_urls.append(f"/uploads/temp/{basename}")

            # 4. 返回成功響應
            return {
                "title": result["title"],
                "blocks": result["blocks"],
                "files": filenames,
                "pdf_urls": pdf_urls,
                "temp_paths": tmp_paths,
            }

        except Exception:
            # 失敗時清理臨時文件，然後重新拋出異常
            for path in tmp_paths:
                parser.cleanup_temp_file(path)
            raise  # 讓 Router 處理
