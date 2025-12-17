import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import json
import re
from typing import List
from config import settings

# 初始化 Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


# 定義 Notion Blocks 的 JSON Schema
NOTION_BLOCKS_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "論文標題（精簡版，15字內）"
        },
        "blocks": {
            "type": "array",
            "description": "Notion blocks 陣列，包含論文導讀的所有內容",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["callout", "heading_2", "heading_3", "bulleted_list_item", "code", "quote", "toggle"]
                    },
                    "callout": {
                        "type": "object",
                        "properties": {
                            "icon": {
                                "type": "object",
                                "properties": {
                                    "emoji": {"type": "string"}
                                },
                                "required": ["emoji"]
                            },
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        },
                                        "annotations": {
                                            "type": "object",
                                            "properties": {
                                                "bold": {"type": "boolean"},
                                                "italic": {"type": "boolean"},
                                                "code": {"type": "boolean"}
                                            }
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["icon", "rich_text"]
                    },
                    "heading_2": {
                        "type": "object",
                        "properties": {
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["rich_text"]
                    },
                    "heading_3": {
                        "type": "object",
                        "properties": {
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["rich_text"]
                    },
                    "bulleted_list_item": {
                        "type": "object",
                        "properties": {
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        },
                                        "annotations": {
                                            "type": "object",
                                            "properties": {
                                                "bold": {"type": "boolean"}
                                            }
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["rich_text"]
                    },
                    "code": {
                        "type": "object",
                        "properties": {
                            "language": {
                                "type": "string",
                                "enum": ["python", "javascript", "typescript", "java", "c", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin", "bash", "shell", "powershell", "sql", "html", "css", "json", "yaml", "xml", "markdown", "plain text", "latex"]
                            },
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["language", "rich_text"]
                    },
                    "quote": {
                        "type": "object",
                        "properties": {
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["rich_text"]
                    },
                    "toggle": {
                        "type": "object",
                        "properties": {
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            },
                            "children": {
                                "type": "array",
                                "description": "Toggle 內的子 blocks（通常是 bulleted_list_item）",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["bulleted_list_item"]
                                        },
                                        "bulleted_list_item": {
                                            "type": "object",
                                            "properties": {
                                                "rich_text": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "type": {"type": "string", "enum": ["text"]},
                                                            "text": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "content": {"type": "string"}
                                                                },
                                                                "required": ["content"]
                                                            },
                                                            "annotations": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "bold": {"type": "boolean"}
                                                                }
                                                            }
                                                        },
                                                        "required": ["type", "text"]
                                                    }
                                                }
                                            },
                                            "required": ["rich_text"]
                                        }
                                    },
                                    "required": ["type", "bulleted_list_item"]
                                }
                            }
                        },
                        "required": ["rich_text", "children"]
                    }
                },
                "required": ["type"]
            }
        }
    },
    "required": ["title", "blocks"]
}

async def summarize_documents_from_paths(file_paths: List[str], filenames: List[str] = None) -> dict:
    """
    一次處理多個文件，生成詳細的論文導讀筆記（支援 PDF + PPT + 音頻混合）

    核心理念：不是壓縮摘要，而是完整展開並重新組織內容
    - 把艱澀的學術論文翻譯成通俗易讀的版本
    - 補充背景知識，讓無基礎的人能看懂
    - 保留所有重要細節（技術方法、公式、實驗數據）
    - 重新組織結構，讓邏輯更清晰

    Args:
        file_paths: 文件的絕對路徑列表
        filenames: 文件名列表（用於日誌）

    Returns:
        {
            "title": "生成的標題",
            "blocks": "詳細的 Notion blocks 陣列"
        }
    """
    try:
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API Key not found")

        if not file_paths:
            raise ValueError("No files to process")

        # 日誌輸出
        file_list = filenames or [f"File {i+1}" for i in range(len(file_paths))]
        print(f"[GEMINI API] Processing {len(file_paths)} files: {', '.join(file_list)}")

        # 上傳所有文件到 Gemini
        uploaded_files = [genai.upload_file(path=path) for path in file_paths]

        # 構建 Prompt（Gemini 會自動處理 JSON 格式，不需要手動提示）
        prompt = (
            "# Role Definition（角色定位）\n"
            "你是一位極度耐心的博士生導師，正在為基礎薄弱的學生整理論文閱讀筆記。\n"
            "你的任務不是「摘要」論文，而是「完整展開並重新組織」論文內容。\n\n"

            "# Core Principles（核心原則）\n"
            "1. **完整性優先於簡潔性**\n"
            "   - 寧可多講，不要少講\n"
            "   - 保留所有重要的技術細節、公式推導、實驗數據\n"
            "   - 不要跳過任何關鍵步驟\n\n"

            "2. **通俗化優先於專業性**\n"
            "   - 用通俗語言解釋所有專業術語（假設讀者是聰明的高中生）\n"
            "   - 多用類比和現實案例，避免抽象描述\n"
            "   - 永遠不要使用「顯然」、「容易看出」、「眾所周知」等詞\n\n"

            "3. **展開式講解**\n"
            "   - 遇到複雜公式，逐項解釋每個符號的意義\n"
            "   - 遇到演算法，一步步說明執行過程和背後原理\n"
            "   - 遇到實驗結果，列出所有重要數據和圖表資訊\n\n"

            "4. **補充背景知識**\n"
            "   - 辨識論文中所有需要背景知識的地方\n"
            "   - 主動補充相關概念的解釋（用 Toggle 摺疊，不干擾主線）\n"
            "   - 如果某個概念很基礎但論文沒講，你也要補充\n\n"

            "# 目標效果\n"
            "讓學生可以「只看你整理的筆記」就能達到以下效果（不需要回去看原文）：\n"
            "1. 完全理解論文的研究動機和要解決的問題\n"
            "2. 理解核心技術方案的每個細節和設計決策\n"
            "3. 理解所有重要公式和演算法的推導過程\n"
            "4. 了解實驗設計和所有關鍵結果數據\n"
            "5. 能夠批判性思考這篇論文的貢獻和局限\n"
            "6. 知道下一步可以學習哪些相關知識\n\n"

            "# 論文導讀筆記結構（必須按此順序組織內容）\n"
            "以下是教學大綱，每個部分都要「詳細展開」，保留所有重要資訊：\n\n"

            "1. **💡 一句話總結（Callout）**\n"
            "   - 用最簡單的語言說明這篇論文的核心貢獻\n"
            "   - 格式：「這篇論文提出了 [方法]，解決了 [具體問題]，效果是 [具體數據對比]」\n\n"

            "2. **🎯 為什麼要讀這篇論文（Heading_2 + Bulleted List）**\n"
            "   - 現實世界遇到什麼痛點？用具體場景舉例（不要只說「效能不好」，要說明具體表現）\n"
            "   - 為什麼現有方法不夠好？詳細說明既有方案的缺陷\n"
            "   - 這篇論文承諾解決什麼問題？預期改進多少？\n"
            "   - 這個部分要寫得詳細，讓讀者完全理解研究動機\n\n"

            "3. **📚 背景知識補充（Heading_2 + Toggle 摺疊）**\n"
            "   - 用 Toggle 包裹，標題：「▶ 點擊展開：理解這篇論文需要知道的基礎概念」\n"
            "   - 列出並詳細解釋所有重要術語（如：RAG、向量檢索、Embedding、Transformer 等）\n"
            "   - 每個術語格式：「術語名稱：詳細的通俗解釋 + 現實類比 + 為什麼在這篇論文中重要」\n"
            "   - 如有公式或程式碼，使用 Code Block 展示並解釋\n"
            "   - 寧可多補充背景知識，不要假設讀者有任何基礎\n\n"

            "4. **🧠 核心方法拆解（Heading_2 + Bulleted List + Code/Quote + Toggle）**\n"
            "   - 這篇論文的技術方案是什麼？用流程圖式的語言詳細描述\n"
            "   - 每個步驟都要說明：(1) 做什麼 (2) 為什麼這樣做 (3) 和既有方法有何不同\n"
            "   - 遇到演算法必須用 Code Block 展示完整邏輯（標註 language），並在 bulleted_list 中逐行解釋\n"
            "   - 遇到關鍵公式，用 Quote Block 標示，然後用 bulleted_list 逐項解釋每個符號和推導步驟\n"
            "   - 複雜的數學推導用 Toggle 摺疊，但內容要完整保留（不要簡化）\n"
            "   - 這是最重要的部分，要非常詳細，保留所有技術細節\n\n"

            "5. **📊 實驗與結果（Heading_2 + Bulleted List）**\n"
            "   - 論文用什麼數據集驗證？數據集規模多大？為什麼選這些數據集？\n"
            "   - 和哪些 baseline 方法比較？每個方法的結果是多少？詳細列出數字\n"
            "   - 有哪些評估指標？每個指標的具體數值是多少？提升幅度多大？\n"
            "   - 有沒有消融實驗（Ablation Study）？驗證了什麼？\n"
            "   - 如果論文有多個實驗表格，把重要數據都列出來\n"
            "   - 為什麼這些結果有說服力？有沒有統計顯著性檢驗？\n\n"

            "6. **💭 批判性思考（Heading_2 + Bulleted List）**\n"
            "   - 這篇論文的核心創新點在哪裡？（技術創新 vs 應用創新）\n"
            "   - 有什麼局限性？什麼場景下可能不適用？\n"
            "   - 實驗設計有沒有可能的缺陷？（如：數據集太小、baseline 太弱）\n"
            "   - 未來可以如何改進？有哪些值得探索的方向？\n\n"

            "7. **🔖 延伸學習（Heading_2 + Bulleted List）**\n"
            "   - 如果想深入理解這篇論文，需要先學習哪些前置知識？\n"
            "   - 這篇論文引用了哪些重要的相關工作？\n"
            "   - 有哪些後續論文改進了這個方法？\n"
            "   - 列出 3-5 個關鍵主題或相關論文名稱\n\n"

            "# 支援的 Notion Block Types（技術約束）\n"
            "- **callout**：提示框（emoji icon 必須設定）\n"
            "- **heading_2 / heading_3**：段落標題\n"
            "- **bulleted_list_item**：列表項（可使用 annotations.bold 強調關鍵詞）\n"
            "- **code**：程式碼或公式區塊（必須指定 language）\n"
            "- **quote**：引用區塊（用於重要定義或公式）\n"
            "- **toggle**：摺疊區塊（children 是 block 陣列，用於背景知識和技術細節）\n\n"

            "# Code Block Language 白名單（必須精確使用）\n"
            "- python, javascript, java, c, c++, c#, go, rust, sql, bash, shell\n"
            "- 特別注意：\"c#\" 不是 \"csharp\"，\"c++\" 不是 \"cpp\"\n"
            "- 數學公式可用 \"plain text\" 或 \"latex\"\n\n"


            "# 語言風格與教學原則（嚴格遵守）\n"
            "1. **通俗化術語**：\n"
            "   - 遇到專業術語，格式：「術語（通俗解釋）」\n"
            "   - 例如：「Embedding（把文字轉成數字向量，就像給每個詞一個座標）」\n"
            "   - 例如：\"RAG（檢索增強生成，就像考試時可以翻書找答案）\"\n\n"

            "2. **多用類比**：\n"
            "   - 抽象概念必須用現實場景類比\n"
            "   - 例如：「向量檢索就像在圖書館用索引卡快速找書」\n"
            "   - 例如：「注意力機制就像考試時對不同題目分配不同時間」\n\n"

            "3. **拆解複雜邏輯**：\n"
            "   - 演算法要一步步說明，每步都解釋「為什麼」\n"
            "   - 公式要逐項解釋每個符號的意義\n"
            "   - 使用「首先...然後...最後...」的流程式語言\n\n"

            "4. **具體數據優於模糊描述**：\n"
            "   - ✅ 正確：「準確率從 78% 提升到 91%」\n"
            "   - ❌ 錯誤：「效果變好了」\n"
            "   - ✅ 正確：\"推理時間減少 65%，從 200ms 降到 70ms\"\n"
            "   - ❌ 錯誤：\"速度變快了\"\n\n"

            "5. **禁用詞彙**：\n"
            "   - 永遠不要使用：「顯然」、「容易看出」、「眾所周知」、「trivial」\n"
            "   - 如果某個步驟真的很簡單，也要簡要說明原因\n\n"

            "6. **rich_text 格式使用**：\n"
            "   - 使用 annotations.bold 標示關鍵術語、方法名稱、數據\n"
            "   - code block 必須標註正確的 language（python/c++/java 等）\n"
            "   - quote block 用於重要公式或定義，並在 bulleted_list 中逐項解釋\n\n"

            "7. **Toggle 使用原則**：\n"
            "   - 背景知識用 Toggle 摺疊，避免干擾主線\n"
            "   - 複雜數學推導用 Toggle 摺疊\n"
            "   - Toggle 標題格式：「▶ 點擊展開：[內容類別]」\n\n"

            "8. **內容完整性提醒**：\n"
            "   - 寧可內容太多（可以用 Toggle 摺疊），不要遺漏重要資訊\n"
            "   - 記住核心目標：讓讀者「不需要回去看原文」就能完全理解論文\n"
            "   - 如果某個部分內容特別多，優先使用 Toggle 摺疊而非省略\n\n"

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


async def refine_summary(original_summary: dict, user_feedback: str) -> dict:
    """
    根據用戶反饋調整筆記內容
    
    Args:
        original_summary: 原始筆記內容 (包含 title 和 blocks)
        user_feedback: 用戶的調整需求
        
    Returns:
        更新後的筆記內容
    """
    try:
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API Key not found")
            
        print(f"[GEMINI API] Refining summary with feedback: {user_feedback}")
        
        # 將原始 blocks 轉為 JSON 字串以便放入 Prompt
        original_json = json.dumps(original_summary, ensure_ascii=False, indent=2)
        
        prompt = (
            "# Role Definition\n"
            "你是同一位耐心的博士生導師。你之前已經生成了一份論文導讀筆記，現在學生提出了一些修改建議。\n"
            "你的任務是：根據學生的反饋，修改並優化這份筆記。\n\n"
            
            "# User Feedback (學生反饋)\n"
            f"{user_feedback}\n\n"
            
            "# Original Summary (原始筆記)\n"
            f"{original_json}\n\n"
            
            "# Instructions\n"
            "1. **針對性修改**：只根據用戶的反饋進行必要的調整。如果用戶只要求修改某個部分，其他部分保持原樣。\n"
            "2. **維持格式**：必須嚴格遵守 Notion Block 格式（與原始筆記一致）。\n"
            "3. **完整性**：返回完整的筆記內容（包含未修改的部分），不要只返回修改的片段。\n"
            "4. **品質保持**：修改後的內容必須保持原有的詳細程度和通俗化風格。\n\n"
            
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
        
        # 使用 generate_content (這是一個新的對話回合)
        response = await model.generate_content_async(prompt)
        
        # 解析結果
        result = json.loads(response.text)
        
        print(f"[GEMINI API] Success: Refined summary based on feedback.")
        return {
            "title": result.get("title", original_summary.get("title")),
            "blocks": result.get("blocks", [])
        }
        
    except Exception as e:
        print(f"[GEMINI API] Failed to refine summary: {e}")
        raise RuntimeError(f"Failed to refine summary: {e}")
