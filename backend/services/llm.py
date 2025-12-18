import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import json
import re
import os
import platform
from typing import List

from config import settings
from models.services import NOTION_BLOCKS_SCHEMA

# 初始化 Gemini
# Removed global init

# 定義 Notion Blocks 的 JSON Schema
# Moved to models.services.schemas.NOTION_BLOCKS_SCHEMA


def normalize_path(path: str) -> str:
    """
    將路徑統一轉換為當前系統可識別的格式

    處理情況：
    1. WSL 環境收到 Windows 路徑 (C:\\...) → 轉換為 /mnt/c/...
    2. Windows 環境收到 Unix 路徑 (/mnt/c/...) → 轉換為 C:\\...
    3. 已經是正確格式 → 直接返回

    Args:
        path: 任意格式的文件路徑

    Returns:
        當前系統可識別的標準路徑
    """
    # 檢測是否在 WSL 環境
    is_wsl = "microsoft" in platform.uname().release.lower()

    if is_wsl:
        # WSL 環境：將 Windows 路徑轉換為 Unix 路徑
        if path.startswith(("C:\\", "c:\\")):
            # C:\Users\... → /mnt/c/Users/...
            unix_path = path.replace("C:\\", "/mnt/c/").replace("c:\\", "/mnt/c/")
            unix_path = unix_path.replace("\\", "/")
            return unix_path
        elif path.startswith(("D:\\", "d:\\")):
            # D:\... → /mnt/d/...
            unix_path = path.replace("D:\\", "/mnt/d/").replace("d:\\", "/mnt/d/")
            unix_path = unix_path.replace("\\", "/")
            return unix_path
    else:
        # Windows 環境：將 Unix 路徑轉換為 Windows 路徑
        if path.startswith("/mnt/c/"):
            # /mnt/c/Users/... → C:\Users\...
            return path.replace("/mnt/c/", "C:\\").replace("/", "\\")
        elif path.startswith("/mnt/d/"):
            return path.replace("/mnt/d/", "D:\\").replace("/", "\\")

    # 已經是正確格式或其他情況
    return path




async def get_static_options_menu(
    file_paths: List[str], 
    filenames: List[str] = None,
    api_key: str = None
) -> dict:
    """
    不調用 LLM，直接返回靜態的選項選單
    用於初始上傳後，讓使用者選擇分析方向
    """
    # 這裡我們依然可以先將檔案上傳到 Gemini (如果 refine_summary 需要依賴已上傳的檔案)
    # 但考慮到 refine_summary 也可以自己處理上傳，這裡我們先跳過上傳，只返回靜態內容
    # 為了保持一致性，title 使用檔名
    
    title = filenames[0] if filenames else "論文筆記"
    
    # 建構靜態的 Notion Blocks (對應原本 Prompt 的選項)
    blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "請選擇分析方向"}}]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "請從下方「快速指令」或直接輸入需求來開始分析："}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "**選項 A - 快速摘要指令**：生成500字摘要，包含目的、方法、結果與結論。"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "**選項 B - 論文結構解析指令**：解析摘要、引言、方法、結果與討論。"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "**選項 C - 深入技術或理論解析指令**：詳細解釋技術概念與原理。"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "**選項 D - 批判性分析指令**：分析研究優缺點、資料合理性與潛在限制。"}}]
            }
        }
    ]

    return {
        "title": title,
        "blocks": blocks,
        "is_initial_menu": True
    }


async def refine_summary(
    original_summary: dict, 
    user_feedback: str,
    api_key: str = None
) -> dict:
    """
    根據用戶反饋調整筆記內容
    
    Args:
        original_summary: 原始筆記內容 (包含 title, blocks, temp_paths)
        user_feedback: 用戶的調整需求
        api_key: Gemini API Key
        
    Returns:
        更新後的筆記內容
    """
    try:
        if not api_key:
            raise ValueError("Gemini API Key is required")
            
        genai.configure(api_key=api_key)
            
        print(f"[GEMINI API] Refining summary with feedback: {user_feedback}")

        # 1. 嘗試從原始摘要中獲取文件路徑
        temp_paths = original_summary.get("temp_paths", [])
        uploaded_files = []

        if temp_paths:
            # 規範化路徑（處理 Windows/Unix 格式差異）
            normalized_paths = [normalize_path(path) for path in temp_paths]

            # 過濾存在的文件並上傳
            valid_paths = [path for path in normalized_paths if os.path.exists(path)]

            if valid_paths:
                uploaded_files = [genai.upload_file(path=path) for path in valid_paths]
                print(f"[GEMINI API] Uploaded {len(uploaded_files)} file(s) to Gemini.")
            else:
                print(f"[GEMINI API] Warning: No valid files found from {len(temp_paths)} path(s).")
        else:
            print("[GEMINI API] Warning: No temp_paths in original_summary.")
        
        # 將原始 blocks 轉為 JSON 字串以便放入 Prompt
        # 為了節省 token，我們過濾掉技術性的欄位 (如 temp_paths, pdf_urls)，
        # 但保留 title, blocks (筆記本體) 和 files (檔名)，讓 LLM 知道內容與來源。
        context_summary = {
            "title": original_summary.get("title"),
            "blocks": original_summary.get("blocks"),
            "files": original_summary.get("files", [])
        }
        original_json = json.dumps(context_summary, ensure_ascii=False, indent=2)
        
        prompt = (
            "# Role Definition\n"
            "你是一位論文理解專家。學生之前上傳了論文，現在提出了新的需求或修改建議。\n"
            "你的任務是：**參考原始論文 PDF** 以及 **舊的筆記**，根據學生的反饋來處理。\n\n"

            "# User Feedback (學生反饋)\n"
            f"{user_feedback}\n\n"

            "# Original Summary (原始筆記)\n"
            f"{original_json}\n\n"

            "# Instructions\n"
            "**0. 關於「原始筆記」的處理原則（最重要！）**：\n"
            "   - **絕對保留**：除非學生明確要求「刪除」某部分，否則 **必須保留原始筆記中的所有內容**。\n"
            "   - **新增模式**：對於補充說明、深入解析等需求，請將新生成的內容 **附加** 到原始筆記的相關段落之後，或者是新增一個標題區塊來放置。\n"
            "   - **禁止覆蓋**：不要因為生成了新內容就丟棄了舊內容。你的輸出必須包含「舊的完整內容」+「新的補充內容」。\n\n"

            "**1. 選項執行優先**：\n"
            "   - 如果學生反饋包含「選項 A」~「選項 E」，這視為全新的分析請求。此時（也只有此時）可以忽略原始筆記，重新生成全新的完整結構。\n\n"

            "**2. 一般調整（非選項指令）**：\n"
            "   - 務必閱讀附帶的 PDF 文件來獲取正確資訊。\n"
            "   - 將新資訊整合進現有結構，保持筆記的完整性。\n\n"

            "**3. 格式規範**：\n"
            "   - Text content 中絕對不要使用 Markdown 語法（如 `**`），必須使用 annotations。\n"
            "   - Text content 開頭絕對不要包含 `•`、`-` 等列表符號。\n"
            "   - **嚴格禁止使用任何 Emoji 符號**（如 💡、📊、✅ 等），請用純文字替代。\n\n"

            "# Output Context\n"
            "請直接輸出修改後的 **完整** JSON（包含所有保留的舊區塊和新生成的區塊）。"
        )
        
        # 配置結構化輸出
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=NOTION_BLOCKS_SCHEMA
        )
        
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL_NAME,
            generation_config=generation_config
        )
        
        # 將 prompt 和 上傳的文件一起傳給 Gemini
        # request_content 順序: [Prompt, File1, File2, ...]
        request_content = [prompt]
        if uploaded_files:
            request_content.extend(uploaded_files)

        # 使用 generate_content
        response = await model.generate_content_async(request_content)
        
        # 解析結果
        result = json.loads(response.text)
        
        print(f"[GEMINI API] Success: Refined summary based on feedback.")
        return {
            "title": result.get("title", original_summary.get("title")),
            "blocks": result.get("blocks", []),
            # 保留 temp_paths 以便下次繼續修改
            "temp_paths": temp_paths,
            "is_initial_menu": False
        }
        
    except Exception as e:
        print(f"[GEMINI API] Failed to refine summary: {e}")
        raise RuntimeError(f"Failed to refine summary: {e}")
