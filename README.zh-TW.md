# psd

以 LangChain (RAG)、Hugging Face Inference API 與 Chroma 建置的課程助教 Chatbot（Streamlit）。

[English](./README.md) | 繁體中文

## 快速開始

1. 準備環境

```bash
# 建議使用 virtualenv 或 conda（zsh）
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. 設定環境變數（在專案根目錄建立 .env）

在專案根目錄建立 `.env` 檔，依你要使用的供應商填入：

```bash
# Hugging Face（預設）
HUGGINGFACEHUB_API_TOKEN=你的HF存取權杖   # 或 HF_TOKEN

# 或使用 Gemini
GOOGLE_API_KEY=你的Google API Key        # 或 GEMINI_API_KEY
```

注意：

- 如未設定 `GOOGLE_API_KEY`（或 `GEMINI_API_KEY`）時，Gemini 無法呼叫。
- 若改用 Hugging Face，請改設 `HUGGINGFACEHUB_API_TOKEN`（或 `HF_TOKEN`）。

3. 準備資料

- 將你的課程 PDF 放在 `data/` 資料夾，檔名請命名為 `syllabus.pdf`。

4. 啟動應用

```bash
streamlit run src/app.py
```

開啟瀏覽器並依照介面提示開始提問。

重要：請勿使用 `python src/app.py` 執行，否則會出現 `missing ScriptRunContext` 與 `Session state does not function...` 等警告；Streamlit 必須用 `streamlit run` 啟動。

## 專案說明

- 文件載入：`PyPDFLoader`（langchain_community）
- 切分：`RecursiveCharacterTextSplitter`
- 向量：`HuggingFaceEmbeddings`（all-MiniLM-L6-v2）
- 向量庫：`Chroma`（持久化目錄 `vector_db/`）
- LLM：`HuggingFaceEndpoint`（預設 `google/flan-t5-large`，任務 `text2text-generation`）
- 介面：Streamlit Chat + 來源段落展開

## 常見問題

- 第一次執行會下載 Embeddings 模型，需稍候。
- 如未設定 `HUGGINGFACEHUB_API_TOKEN`（或 `HF_TOKEN`），呼叫雲端 LLM 可能失敗。
- 若想重建向量庫，可刪除 `vector_db/` 後重新啟動。

## 結構

```
data/
src/
	app.py        # Streamlit 前端
	rag_core.py   # RAG 核心邏輯（LCEL 寫法）
requirements.txt
```
