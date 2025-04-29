# app.py

import streamlit as st
from io import BytesIO
import os
from rag_agent import create_agentic_rag_graph
from utility import NamedFile
from manualupload import download_manual_from_archive

st.set_page_config(page_title="Equipment Manual Assistant", page_icon="🛠️")
st.title("🛠️ Equipment Manual Assistant - Agent Powered")

graph = create_agentic_rag_graph()

st.markdown("### Upload or Search Manual")
search_query = st.text_input("Equipment name or model:")

manual_file = None

if st.button("🔍 Search Archive.org"):
    if search_query:
        downloaded = download_manual_from_archive(search_query)
        if downloaded:
            manual_file = NamedFile(open(downloaded, "rb"), os.path.basename(downloaded))
            st.success(f"Downloaded: {os.path.basename(downloaded)}")
        else:
            st.warning("No matching manual found.")

uploaded_file = st.file_uploader("📄 Or Upload manual manually", type=["pdf"])

if uploaded_file:
    manual_file = uploaded_file

if manual_file:
    file_bytes = manual_file.read()
    filename = getattr(manual_file, "name", "uploaded_manual.pdf")

    st.session_state.filename = filename
    st.session_state.file_bytes = file_bytes

st.markdown("---")
st.markdown("### 🤖 Ask Questions About the Manual")

user_query = st.chat_input("Ask about the equipment manual...")

if user_query:
    initial_state = {
        "query": user_query,
        "file_bytes": st.session_state.get("file_bytes"),
        "filename": st.session_state.get("filename"),
        "retrieved_chunks": None,
        "answer": None,
        "image_urls": None
    }

    result = graph.invoke(initial_state)

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        st.markdown(result["answer"])

        if result.get("image_urls"):
            for url in result["image_urls"]:
                st.image(url, caption="Reference Image", use_column_width=True)
