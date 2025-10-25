import os
from typing import Any, Callable, Dict, List

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None


def setup_rag_pipeline(pdf_path: str, persist_dir: str = "vector_db") -> Callable[[Dict[str, str]], Dict[str, Any]]:
    """
    建立一個可呼叫的 QA 管線。輸入格式：{"query": str}
    回傳格式：{"result": str, "source_documents": List[Document]}
    """

    load_dotenv()

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"找不到指定的 PDF 檔案：{pdf_path}")

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    print("正在載入 Embedding 模型...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("Embedding 模型載入完成。")

    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        print("從本地載入向量資料庫...")
        vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    else:
        print("正在建立向量資料庫並持久化...")
        vectordb = Chroma.from_documents(texts, embedding=embeddings, persist_directory=persist_dir)
        print("資料庫建立完成。")

    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("警告：未設定 GOOGLE_API_KEY（或 GEMINI_API_KEY）。若無法呼叫 Gemini，請先至 .env 設定。")

    if ChatGoogleGenerativeAI is None:
        raise ImportError(
            "缺少套件 langchain-google-genai，請先安裝（pip install langchain-google-genai google-generativeai）。"
        )
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=gemini_key,
            transport="rest",
            temperature=0,
            max_output_tokens=512,
        )
    except Exception as e:
        print(f"初始化 Gemini 模型失敗（{e}），改用備援模型 gemini-1.5-flash。")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=gemini_key,
            transport="rest",
            temperature=0,
            max_output_tokens=512,
        )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是細心的助教，根據提供的文件內容回答問題。若無法從內容找到答案，請誠實說明。請以繁體中文作答。"),
        ("human", "問題：{question}\n\n已知內容：\n{context}\n\n請根據已知內容作答。"),
    ])

    def _format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)

    rag_chain = {
        "context": retriever | _format_docs,
        "question": RunnablePassthrough(),
    } | prompt | llm | StrOutputParser()

    def _qa_runner(inputs: Dict[str, str]) -> Dict[str, Any]:
        question = inputs.get("query") if isinstance(inputs, dict) else str(inputs)
        source_docs = retriever.invoke(question)
        answer = rag_chain.invoke(question)
        return {"result": answer, "source_documents": source_docs}

    return _qa_runner

if __name__ == "__main__":
    pdf_file_path = "data/syllabus.pdf"
    qa_pipeline = setup_rag_pipeline(pdf_file_path)
    print("正在測試 RAG 管線...", qa_pipeline)
    question = "這門課的期中報告要求是什麼？"
    result = qa_pipeline({"query": question})
    print("\n--- 提問 ---")
    print(question)
    print("\n--- 回答 ---")
    print(result["result"])