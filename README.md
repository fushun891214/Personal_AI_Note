# AI Note Summary (AI 筆記摘要助手)

一個基於 Google Gemini 1.5 Flash 模型的智慧筆記摘要工具。
能夠自動解析 PDF 與 PowerPoint 投影片，生成結構化 Markdown 摘要，並自動同步到 Notion 資料庫。

## 核心功能

- **多格式支援**: 拖曳上傳 PDF (`.pdf`) 或 PowerPoint (`.ppt`, `.pptx`) 檔案。
- **AI 智慧摘要**: 使用 Google Gemini 1.5 Flash 快速生成精準的結構化重點摘要。
- **Notion 同步**: 自動將生成的摘要以 Page 形式寫入指定的 Notion Database。
- **現代化介面**: 乾淨、響應式的單頁應用 (SPA) 設計。

## 系統架構

本專案採用前後端分離的模組化架構：

```text
├── backend/                  # Python FastAPI 後端
│   ├── main.py               # API 入口
│   ├── config.py             # 設定檔管理
│   └── services/             # 核心服務層
│       ├── llm.py            # Gemini AI 整合
│       ├── parser.py         # 檔案解析邏輯 (PDF/PPT)
│       └── notion.py         # Notion API 整合
├── frontend/                 # Vue 3 + Vite 前端
│   ├── src/                  # Vue 組件源碼
│   │   ├── components/       # UI 組件 (FileUploader, FileList, SummaryResult)
│   │   ├── App.vue           # 主應用組件
│   │   └── main.js           # 應用入口
│   └── vite.config.js        # Vite 配置 (開發代理設定)
└── .env                      # 環境變數
```

## 快速開始

### 1. 環境準備 (Windows)

#### Python 後端
本專案使用 Python 3.10 的標準 `venv` 建立虛擬環境。

1. **建立虛擬環境**:
   ```powershell
   py -3.10 -m venv .venv
   ```

2. **啟用環境**:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. **安裝依賴**:
   ```powershell
   # 重要：請務必進入 backend 資料夾再執行
   cd backend
   pip install -r requirements.txt
   ```

#### Vue 前端
確保已安裝 Node.js (推薦 v18+)。

```powershell
cd frontend
npm install
```

### 2. 設定環境變數

在根目錄建立 `.env` 檔案（參考範例）：

```ini
GEMINI_API_KEY=AIza...              # Google Gemini API Key
NOTION_API_KEY=secret_...           # Notion Integration Token
NOTION_DATABASE_ID=...              # 目標 Notion Database ID
```

> **注意**: 您的 Notion Integration 必須已被邀請至該 Database，否則無法寫入。

### 3. 啟動服務

我們提供多種啟動方式，請選擇最適合您的：

#### 方式 A: 使用一鍵腳本 (最簡單)
在 Git Bash 或支援 bash 的終端機執行：
```bash
./start.sh
```
此腳本會同時啟動後端 API (8000) 與前端 Dev Server (5173)。

#### 方式 B: 分別手動啟動 (最靈活)

**Terminal 1: 後端**
```powershell
# 1. 啟用環境
.venv\Scripts\Activate.ps1

# 2. 進入後端目錄 (關鍵步驟)
cd backend

# 3. 啟動伺服器
uvicorn main:app --reload
```
API 地址: [http://127.0.0.1:8000](http://127.0.0.1:8000)

**Terminal 2: 前端**
```powershell
cd frontend
npm run dev
```
前端 UI: [http://localhost:5173](http://localhost:5173)

#### 方式 C: 生產模式預覽
將前端編譯為靜態檔案，由後端統一服務：

```powershell
# 1. 編譯前端
cd frontend
npm run build
cd ..

# 2. 啟動後端
cd backend
uvicorn main:app
```
單一入口: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 開發者筆記

### 後端開發
- 若要更換 AI 模型，請修改 `backend/services/llm.py` 中的 `GenerativeModel` 參數。
- API 端點位於 `backend/main.py`，使用 FastAPI 自動生成的文檔：`/docs`

### 前端開發
- 使用 Vue 3 Composition API (`<script setup>`)
- 開發時修改 `frontend/src/` 下的檔案，Vite HMR 會即時更新
- Vite proxy 配置位於 `frontend/vite.config.js`，開發環境自動將 `/api` 轉發至後端

### 架構說明
- **開發環境**: 前端 Vite dev server (5173) + 後端 FastAPI (8000)，透過 Vite proxy 避免 CORS
- **生產環境**: 前端建置為靜態檔案，由 FastAPI `StaticFiles` 掛載，單一服務統一對外
