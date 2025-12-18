import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import json
import re
from typing import List

from config import settings
from models.services import NOTION_BLOCKS_SCHEMA

# 初始化 Gemini
# Removed global init

# 定義 Notion Blocks 的 JSON Schema
# Moved to models.services.schemas.NOTION_BLOCKS_SCHEMA

async def summarize_documents_from_paths(
    file_paths: List[str], 
    filenames: List[str] = None,
    api_key: str = None
) -> dict:
    """
    一次處理多個文件，生成詳細的論文導讀筆記（僅支援 PDF）

    核心理念：不是壓縮摘要，而是完整展開並重新組織內容
    - 把艱澀的學術論文翻譯成通俗易讀的版本
    - 補充背景知識，讓無基礎的人能看懂
    - 保留所有重要細節（技術方法、公式、實驗數據）
    - 重新組織結構，讓邏輯更清晰

    Args:
        file_paths: 文件的絕對路徑列表
        filenames: 文件名列表（用於日誌）
        api_key: Gemini API Key

    Returns:
        {
            "title": "生成的標題",
            "blocks": "詳細的 Notion blocks 陣列"
        }
    """
    try:
        if not api_key:
            raise ValueError("Gemini API Key is required")
        
        genai.configure(api_key=api_key)

        if not file_paths:
            raise ValueError("No files to process")

        # 日誌輸出
        file_list = filenames or [f"File {i+1}" for i in range(len(file_paths))]
        print(f"[GEMINI API] Processing {len(file_paths)} files: {', '.join(file_list)}")

        # 上傳所有文件到 Gemini
        uploaded_files = [genai.upload_file(path=path) for path in file_paths]

        # 構建 Prompt（Gemini 會自動處理 JSON 格式，不需要手動提示）
        prompt = (
            "# Role Definition\n"
        "你是一位極度耐心的博士生導師，正在為基礎薄弱的學生整理論文閱讀筆記。\n"
        "你的目標是讓學生「只看筆記不需要看原文」就能完全理解，並輸出為符合 Notion 格式的 JSON。\n\n"

        "# Core Principles & Guidelines（核心原則與規範）\n"
        "1. **通俗易懂 (Accessibility)**：\n"
        "   - 假設讀者是聰明的高中生，用通俗語言解釋術語（如：Embedding = 文字的座標）。\n"
        "   - 善用「現實類比」解釋抽象概念。\n"
        "3. **🚫 嚴格禁用**：\n"
        "   - 「顯然」、「容易看出」、「眾所周知」等詞。\n"
        "   - **Markdown 語法**：text.content 中絕對不要包含 `**`、`*`、`` ` `` 等符號。若需粗體/斜體/程式碼，必須使用 `annotations` 屬性。\n"
        "   - **列表符號**：Text content 開頭絕對不要包含 `•`、`-`、`1.` 等列表符號，這些由 Block type 自動處理。\n"
        "2. **極度詳盡 (Completeness)**：\n"
        "2. **極度詳盡 (Completeness)**：\n"
        "   - 寧可多講，絕不少講。保留所有技術細節、公式推導和實驗數據。\n"
        "   - 遇到複雜公式/演算法，必須「逐項/逐行」解釋意義與邏輯（使用 bulleted_list）。\n"
        "   - 優先使用 `toggle` 區塊摺疊詳細推導與背景知識，以保持版面整潔但不丟失資訊。\n"
        "3. **數據精確 (Precision)**：\n"
        "   - 必須引用具體數字（如：準確率提升至 91%），避免模糊描述（如：效果變好）。\n\n"

        "# Technical Constraints（技術約束）\n"
        "1. **Notion Block Types**：\n"
        "   - `callout`: 一句話總結 (必須有 emoji)。\n"
        "   - `heading_2`: 章節標題。\n"
        "   - `bulleted_list_item`: 主要內容 (可用 bold 強調)。\n"
        "   - `code`: 程式碼/公式 (必須指定 language, 如 python, latex)。\n"
        "   - `quote`: 關鍵定義/公式。\n"
        "   - `toggle`: 用於「背景知識」與「複雜推導」，標題格式「▶ 點擊展開：...」。\n"
        "2. **Code Languages**: python, c++, java, latex, plain text 等。\n\n"

        "# Content Structure（筆記結構）\n"
        "請嚴格按照以下順序生成 block list：\n\n"

        "1. **💡 一句話總結 (Callout)**\n"
        "   - 格式：「提出 [方法]，解決 [問題]，效果 [數據]」。\n"
        "2. **🎯 為什麼要讀這篇論文 (Heading_2 + Bullets)**\n"
        "   - 現實痛點（具體場景）。\n"
        "   - 既有方法缺陷。\n"
        "   - 本文預期改進。\n"
        "3. **📚 背景知識補充 (Heading_2 + Toggle)**\n"
        "   - 主動識別並解釋論文中的專業術語（RAG, Transformer等）。\n"
        "   - 寧可多補，不要假設讀者有基礎。\n"
        "4. **🧠 核心方法拆解 (Heading_2 + Bullets/Code/Quote/Toggle)**\n"
        "   - 用流程圖語言描述技術方案 (首先...然後...)。\n"
        "   - 演算法：用 Code Block 展示，並逐行解釋。\n"
        "   - 數學公式：用 Quote 展示 LaTeX，並逐項解釋符號意義。\n"
        "5. **📊 實驗與結果 (Heading_2 + Bullets)**\n"
        "   - 數據集、Baseline 方法、評估指標。\n"
        "   - 詳細列出關鍵結果數據與提升幅度。\n"
        "6. **💭 批判性思考 (Heading_2 + Bullets)**\n"
        "   - 創新點 vs 局限性。\n"
        "7. **🔖 延伸學習 (Heading_2 + Bullets)**\n"
        "   - 前置知識、引用文獻、後續研究。\n\n"

            "# 輸出範例（論文導讀完整版）\n"
            "{\n"
            '  "title": "Attention 機制論文導讀",\n'
            '  "blocks": [\n'
            '    {"type": "callout", "callout": {"icon": {"emoji": "💡"}, "rich_text": [{"type": "text", "text": {"content": "這篇論文提出了 Attention 機制，解決了傳統 RNN 處理長文本時會遺忘前面內容的問題，使機器翻譯準確率從 78% 提升到 91%"}, "annotations": {"bold": true}}]}},\n'
            '    {"type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎯 為什麼要讀這篇論文"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "現實痛點：翻譯長句子時，傳統 RNN 會忘記句子開頭的內容，就像你背長串電話號碼會忘記前幾位"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "既有方法缺陷：RNN 把所有資訊壓縮成一個固定長度的向量，資訊會遺失"}}]}},\n'
            '    {"type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📚 背景知識補充"}}]}},\n'
            '    {"type": "toggle", "toggle": {"rich_text": [{"type": "text", "text": {"content": "▶ 點擊展開：理解這篇論文需要知道的基礎概念"}}], "children": [{"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "RNN（循環神經網路）：一種處理序列資料的神經網路，就像一個人逐字閱讀文章，每次都記住前面看過的內容"}}]}}, {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Encoder-Decoder：翻譯系統的架構，Encoder 理解原文，Decoder 生成譯文"}}]}}]}},\n'
            '    {"type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🧠 核心方法拆解"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "關鍵創新："}}, {"type": "text", "text": {"content": "Attention 機制"}, "annotations": {"bold": true}}, {"type": "text", "text": {"content": "，讓 Decoder 在生成每個詞時，可以回頭查看原文的所有位置，自動找出最相關的部分"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "為什麼需要 Attention：傳統 Encoder-Decoder 把整個句子壓縮成一個固定長度的向量 c，長句子會遺失資訊。Attention 讓每個輸出詞都能重新計算自己的 context vector"}}]}},\n'
            '    {"type": "quote", "quote": {"rich_text": [{"type": "text", "text": {"content": "注意力權重公式：α_ij = exp(score(h_i, s_j)) / Σ_k exp(score(h_i, s_k))"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "公式詳細解釋："}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "  • α_ij：翻譯第 i 個詞時，對原文第 j 個詞的關注程度（0到1之間，所有 j 的權重加起來等於1）"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "  • h_i：Encoder 在位置 i 的隱藏狀態（代表原文第 i 個詞的資訊）"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "  • s_j：Decoder 在位置 j 的隱藏狀態（代表目前正在生成的詞）"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "  • score(h_i, s_j)：計算兩個向量的相關性，常用方法是點積 h_i · s_j"}}]}},\n'
            '    {"type": "toggle", "toggle": {"rich_text": [{"type": "text", "text": {"content": "▶ 點擊展開：Attention 計算的完整流程"}}], "children": [{"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "步驟1：Encoder 處理原文，產生隱藏狀態序列 [h_1, h_2, ..., h_n]"}}]}}, {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "步驟2：Decoder 生成第 j 個詞時，計算 s_j 和所有 h_i 的 score"}}]}}, {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "步驟3：用 softmax 歸一化得到注意力權重 α"}}]}}, {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "步驟4：加權平均得到 context vector：c_j = Σ α_ij * h_i"}}]}}, {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "步驟5：用 c_j 和 s_j 一起生成第 j 個詞"}}]}}]}},\n'
            '    {"type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📊 實驗與結果"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "數據集："}}, {"type": "text", "text": {"content": "WMT 英德翻譯"}, "annotations": {"bold": true}}, {"type": "text", "text": {"content": "，包含 450 萬句對"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "結果：BLEU 分數從 baseline 的 27.3 提升到 34.8（提升 27%），長句子效果尤其明顯"}}]}},\n'
            '    {"type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "💭 批判性思考"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "創新點：首次讓模型能夠「回頭看」輸入，而非只依賴壓縮後的向量"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "局限性：計算複雜度 O(n²)，當句子很長時（如 1000 字）會很慢"}}]}},\n'
            '    {"type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🔖 延伸學習"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "下一步學習：Transformer 架構（完全基於 Attention，捨棄 RNN）"}}]}},\n'
            '    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "相關論文：《Attention Is All You Need》（2017）"}}]}}\n'
            '  ]\n'
            '}\n'
        )

        # 配置結構化輸出
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=NOTION_BLOCKS_SCHEMA
        )

        # 一次性生成論文筆記（所有文件）
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL_NAME,
            generation_config=generation_config
        )
        response = await model.generate_content_async([prompt, *uploaded_files])

        # 調試：顯示返回的 JSON（前 500 字元）
        print(f"[GEMINI API] Received JSON (first 500 chars): {response.text[:500]}")

        # 解析 JSON（Gemini 保證格式正確，不需要清理）
        result = json.loads(response.text)

        print(f"[GEMINI API] Success: Generated title and blocks from {len(file_paths)} files")
        return {
            "title": result.get("title", "未命名筆記"),
            "blocks": result.get("blocks", [])
        }

    except Exception as e:
        print(f"[GEMINI API] Failed to process documents: {e}")
        raise RuntimeError(f"Failed to generate summary: {e}")


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
            print(f"[GEMINI API] Found {len(temp_paths)} original files to reference.")
            # 驗證文件是否存在，並上傳
            import os
            valid_paths = [path for path in temp_paths if os.path.exists(path)]
            
            if len(valid_paths) != len(temp_paths):
                 print(f"[GEMINI API] Warning: Some temp files are missing. Found {len(valid_paths)}/{len(temp_paths)}")

            # 上傳文件給 Gemini (讓它能看到原文)
            uploaded_files = [genai.upload_file(path=path) for path in valid_paths]
        else:
            print("[GEMINI API] Warning: No temp_paths found in original_summary. Refinement will rely solely on previous summary.")
        
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
            "你是同一位耐心的博士生導師。你之前已經生成了一份論文導讀筆記，現在學生提出了一些修改建議。\n"
            "你的任務是：**參考原始論文(如果已提供)** 以及 **舊的筆記**，根據學生的反饋來修改並優化這份筆記。\n\n"
            
            "# User Feedback (學生反饋)\n"
            f"{user_feedback}\n\n"
            
            "# Original Summary (原始筆記)\n"
            f"{original_json}\n\n"
            
            "# Instructions\n"
            "1. **基於原文回答**：如果學生的問題涉及原始筆記中沒有的細節（例如「請補充實驗數據」），**請務必閱讀附帶的 PDF 文件** 來獲取正確資訊，絕對不要瞎編。\n"
            "2. **針對性修改**：只根據用戶的反饋進行必要的調整。如果用戶只要求修改某個部分，其他部分保持原樣。\n"
            "3. **維持格式**：必須嚴格遵守 Notion Block 格式（與原始筆記一致）。\n"
            "4. **完整性**：返回完整的筆記內容（包含未修改的部分），不要只返回修改的片段。\n"
            "5. **品質保持**：修改後的內容必須保持原有的詳細程度和通俗化風格。\n"
            "6. **格式規範**：\n"
            "   - Text content 中絕對不要使用 Markdown 語法（如 `**`），必須使用 annotations。\n"
            "   - Text content 開頭絕對不要包含 `•`、`-` 等列表符號。\n\n"
            
            "# Output Context\n"
            "請直接輸出修改後的完整 JSON，符合之前的 Notion Blocks Schema。"
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
            "temp_paths": temp_paths
        }
        
    except Exception as e:
        print(f"[GEMINI API] Failed to refine summary: {e}")
        raise RuntimeError(f"Failed to refine summary: {e}")
