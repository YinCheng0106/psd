# psd

A course TA Chatbot built with LangChain (RAG), Hugging Face Inference API, and Chroma, powered by Streamlit.

English | [繁體中文](./README.zh-TW.md)

## Quick Start

1. Set up environment

```bash
# recommended: use virtualenv or conda (zsh)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables (create a .env file at the project root)

Put the following into a file named `.env` in the repository root, depending on which provider you use.

```bash
# Hugging Face (default)
HUGGINGFACEHUB_API_TOKEN=your_hf_access_token   # or HF_TOKEN

# Or use Gemini
GOOGLE_API_KEY=your_google_api_key               # or GEMINI_API_KEY
```

Notes:

- If `GOOGLE_API_KEY` (or `GEMINI_API_KEY`) is not set, Gemini cannot be used.
- If you switch to Hugging Face, set `HUGGINGFACEHUB_API_TOKEN` (or `HF_TOKEN`).

3. Prepare data

- Put your course PDF in the `data/` folder and name it `syllabus.pdf`.

4. Run the app

```bash
streamlit run src/app.py
```

Open your browser and start asking questions via the UI.

Important: Do NOT run `python src/app.py`, otherwise you will see warnings like `missing ScriptRunContext` and `Session state does not function...`. Streamlit apps must be launched with `streamlit run`.

## Project Details

- Document loader: `PyPDFLoader` (langchain_community)
- Splitter: `RecursiveCharacterTextSplitter`
- Embeddings: `HuggingFaceEmbeddings` (all-MiniLM-L6-v2)
- Vector store: `Chroma` (persisted under `vector_db/`)
- LLM: `HuggingFaceEndpoint` (default `google/flan-t5-large`, task `text2text-generation`)
- UI: Streamlit Chat + expandable source passages

## FAQ

- The first run will download the embeddings model; please wait a bit.
- If `HUGGINGFACEHUB_API_TOKEN` (or `HF_TOKEN`) is not configured, cloud LLM calls may fail.
- To rebuild the vector store, delete the `vector_db/` folder and restart the app.

## Structure

```
data/
src/
	app.py        # Streamlit front-end
	rag_core.py   # RAG core logic (LCEL style)
requirements.txt
```