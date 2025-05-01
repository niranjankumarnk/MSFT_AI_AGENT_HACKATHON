
import streamlit as st
import os
from Agentic_RAG.rag_agent import create_agentic_rag_graph
from Agentic_RAG.rag_tools import manual_exists
from utility import NamedFile
from RAG_modules.azure_cosmoDB import list_manual_collections, delete_manual_data
from RAG_modules.azure_store import delete_manual_images_from_azure
from RAG_modules.manual_search import download_manual_from_archive

def display_manual_assistant():
    st.header("📄 Equipment Manual Assistant")
    graph = create_agentic_rag_graph()

    search_query = st.text_input("Search Archive.org for a manual:")
    manual_file = None

    if st.button("🔍 Search"):
        if search_query:
            downloaded = download_manual_from_archive(search_query)
            if downloaded:
                manual_file = NamedFile(open(downloaded, "rb"), os.path.basename(downloaded))
                st.success(f"Downloaded: {os.path.basename(downloaded)}")
            else:
                st.warning("No matching manual found. Please upload manually.")

    uploaded_file = st.file_uploader("Upload Manual (PDF)", type=["pdf"])

    if uploaded_file or manual_file:
        file_bytes = (manual_file or uploaded_file).read()
        filename = getattr(manual_file or uploaded_file, "name", "manual.pdf")

        if manual_exists(filename):
            st.success("Manual already exists!")
        else:
            with st.spinner("Processing manual..."):
                result = graph.invoke({"query": "trigger", "file_bytes": file_bytes, "filename": filename})
            st.success("✅ Manual processed.")

    manuals = sorted(list_manual_collections())
    if manuals:
        selected = st.selectbox("Select Manual", manuals)
        if st.button("🗑️ Delete Manual"):
            delete_manual_data(selected)
            delete_manual_images_from_azure(selected)
            st.success("✅ Manual deleted.")
            st.rerun()

        user_query = st.chat_input("Ask about the manual...")
        if user_query:
            result = graph.invoke({"query": user_query, "file_bytes": None, "filename": selected})
            st.chat_message("assistant").markdown(result.get("answer", ""))
            for img in result.get("image_urls", []):
                st.image(img, use_container_width=True)
