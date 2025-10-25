import os
import streamlit as st
from rag_core import setup_rag_pipeline

st.title("智慧課程助教 Chatbot")
st.caption("使用 LangChain (RAG) + Gemini API + Chroma 持久化向量庫")

@st.cache_resource(show_spinner=True)
def load_pipeline():
    pdf_file_path = "data/syllabus.pdf"
    if not os.path.exists(pdf_file_path):
        st.error("找不到資料檔案 data/syllabus.pdf，請將課程 PDF 放到 data/ 資料夾並命名為 syllabus.pdf。")
        st.stop()
    return setup_rag_pipeline(pdf_file_path)


qa_pipeline = load_pipeline()
st.success("知識庫與模型載入完成，開始提問吧！")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("請輸入關於這門課的問題..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("助教思考中..."):
            try:
                response = qa_pipeline({"query": prompt})
                answer = response.get("result", "抱歉，我暫時無法回答這個問題。")
                print("回答生成完成。")
                print("回答內容：", answer)
                st.markdown(answer)

                sources = response.get("source_documents", [])
                if sources:
                    with st.expander("參考來源段落"):
                        for i, doc in enumerate(sources[:4], start=1):
                            meta = doc.metadata or {}
                            page = meta.get("page", "?")
                            source = meta.get("source", "")
                            st.markdown(f"第 {i} 段（第 {page} 頁） - {source}")
                            st.write(doc.page_content)
                            st.divider()
            except Exception as e:
                st.error(f"產生回答時發生錯誤：{e}")

    st.session_state.messages.append({"role": "assistant", "content": answer})