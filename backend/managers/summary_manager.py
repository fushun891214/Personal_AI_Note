"""
摘要相關業務邏輯

職責：
1. 協調 services 的調用
2. 處理業務邏輯
3. 錯誤處理和數據轉換
"""
from typing import Dict, Any, List

from services import llm, notion, pdf


class SummaryManager:
    """摘要業務邏輯管理"""

    async def refine_summary(
        self, 
        original_summary: Dict[str, Any], 
        user_feedback: str,
        gemini_api_key: str = None
    ) -> Dict[str, Any]:
        """
        根據用戶反饋調整摘要
        
        Raises:
            Exception: 當 LLM 調用失敗時
        """
        return await llm.refine_summary(original_summary, user_feedback, api_key=gemini_api_key)

    def save_to_notion(
        self, 
        title: str, 
        blocks: List[Any],
        notion_api_key: str = None,
        notion_database_id: str = None
    ) -> Dict[str, Any]:
        """
        儲存到 Notion
        
        Returns:
            {"success": True, "message": ...} 或 {"success": False, "error": ...}
        """
        result = notion.create_notion_page(
            title, 
            blocks, 
            api_key=notion_api_key, 
            database_id=notion_database_id
        )
        
        if "Error" in result:
            return {"success": False, "error": result}
        
        return {"success": True, "message": result}

    def generate_pdf(self, title: str, blocks: List[Any]) -> bytes:
        """
        生成 PDF 檔案
        
        Returns:
            PDF 的 bytes
            
        Raises:
            Exception: 當 PDF 生成失敗時
        """
        return pdf.generate_pdf(title, blocks)
