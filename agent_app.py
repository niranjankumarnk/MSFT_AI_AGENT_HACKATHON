# app.py

# import streamlit as st
# import os
# from rag_agent import create_agentic_rag_graph
# from rag_tools import manual_exists
# from utility import NamedFile
# from mongodb_store import list_manual_collections, delete_manual_data
# # from S3_store import delete_manual_images_from_s3
# from azure_store import delete_manual_images_from_azure

# from manualupload import download_manual_from_archive
# import base64
# from io import BytesIO
# from dotenv import load_dotenv

# load_dotenv()

# st.set_page_config(page_title="Equipment Manual Assistant", page_icon="🛠️")
# st.title("🛠️ Equipment Manual Assistant - Agent Powered")

# graph = create_agentic_rag_graph()

# st.header("📄 Upload or Search Manual")
# search_query = st.text_input("Equipment name or model:")

# manual_file = None
# manual_uploaded = False

# if st.button("🔍 Search Archive.org"):
#     if search_query:
#         downloaded = download_manual_from_archive(search_query)
#         if downloaded:
#             manual_file = NamedFile(open(downloaded, "rb"), os.path.basename(downloaded))
#             st.success(f"Downloaded: {os.path.basename(downloaded)}")
#         else:
#             st.warning("No matching manual found online. Please upload it manually below.")

# uploaded_file = st.file_uploader("Upload Manual (PDF)", type=["pdf"])
    
# # --------- 2. Process Upload ---------
# if uploaded_file or manual_file:
#     if manual_file:
#         manual_filename = getattr(manual_file, "name", "uploaded_manual.pdf")
#         file_bytes = manual_file.read()
#     else:
#         manual_filename = getattr(uploaded_file, "name", "uploaded_manual.pdf")
#         file_bytes = uploaded_file.read()

#     # --- Check if manual already processed ---
#     exists_in_mongo = manual_exists(manual_filename)
#     # exists_in_s3 = image_exists_in_s3(S3_BUCKET_NAME, s3_key)

#     if exists_in_mongo:
#         st.success(f"✅ Manual '{manual_filename}' already uploaded and processed! Skipping upload.")
#     else:
#         with st.spinner(f"Processing {manual_filename}..."):
#             initial_state = {
#                 "query": "dummy-process-trigger",  # dummy query to trigger upload agent
#                 "file_bytes": file_bytes,
#                 "filename": manual_filename,
#             }
#             result = graph.invoke(initial_state)

#         st.success(f"✅ Manual '{manual_filename}' uploaded and processed!")

# st.header("📚 Available Manuals")
# available_manuals = sorted(list_manual_collections())

# if not available_manuals:
#     st.info("Please upload a manual first!")
#     st.stop()
    
# selected_manual = st.selectbox("Choose a manual to ask questions from:", available_manuals)

# if selected_manual:
#     st.write(f"📚 Selected manual: `{selected_manual}`")
    
#     # Add delete button
#     if st.button(f"🗑️ Delete Manual: {selected_manual}"):
#         delete_manual_data(selected_manual)
#         delete_manual_images_from_azure(selected_manual)
#         st.success(f"✅ Manual '{selected_manual}' deleted from database and S3!")
#         st.rerun()  # Refresh the page to update manual list


# st.markdown("---")
# st.markdown("### 🤖 Ask Questions About the Manual")

# user_query = st.chat_input("Ask about the equipment manual...")

# if user_query:
#     initial_state = {
#         "query": user_query,
#         "file_bytes": None,
#         "filename": selected_manual,
#     }
#     with st.spinner("🔎 Thinking..."):
#         result = graph.invoke(initial_state)

#     if result.get("answer"):
#         st.chat_message("assistant").markdown(result["answer"])

#     if result.get("image_urls"):
#         for image_url in result["image_urls"]:
#             st.image(image_url, use_container_width=True)


# app.py

import streamlit as st
from rag_agent import create_agentic_rag_graph
from utility import NamedFile
from manualupload import download_manual_from_archive
from mongodb_store import list_manual_collections, delete_manual_data
from azure_store import delete_manual_images_from_azure

st.set_page_config(page_title="Equipment Assistant", page_icon="🛠️")
st.title("🧠 AI-Powered Equipment Assistant")

graph = create_agentic_rag_graph()

# --- Query Input ---
user_query = st.chat_input("Ask a question about equipment, dashboard, or request a report...")

if user_query:
    st.session_state["query"] = user_query
    st.session_state["filename"] = None
    st.session_state["file_bytes"] = None

    # Ask LLM what to do
    st.write("🔍 Deciding best path using LLM...")
    decision = graph.invoke({"query": user_query, "file_bytes": None, "filename": None})
    route = decision.get("route", "").lower()

    st.write(f"LLM chose route: **{route}**")

    if route == "rag":
        # Ask for manual
        st.subheader("📄 Upload or Search for Manual")
        search_query = st.text_input("Search Archive.org:")
        manual_file = None

        if st.button("🔍 Search"):
            if search_query:
                downloaded = download_manual_from_archive(search_query)
                if downloaded:
                    manual_file = NamedFile(open(downloaded, "rb"), downloaded.name)
                    st.success(f"Downloaded: {manual_file.name}")
                else:
                    st.warning("Manual not found online. Try upload instead.")

        uploaded_file = st.file_uploader("Or upload a manual", type=["pdf"])

        if uploaded_file or manual_file:
            st.session_state["file_bytes"] = uploaded_file.read() if uploaded_file else None
            st.session_state["filename"] = manual_file or (uploaded_file.name if uploaded_file else None)

            with st.spinner("Processing manual and answering..."):
                result = graph.invoke({
                    "query": user_query,
                    "file_bytes": st.session_state["file_bytes"],
                    "filename": st.session_state["filename"]
                })

            st.chat_message("assistant").markdown(result.get("answer", "No answer found."))
            for img in result.get("image_urls", []):
                st.image(img, use_container_width=True)

    elif route == "summary":
        with st.spinner("Fetching dashboard summary..."):
            result = graph.invoke({"query": user_query})
        st.chat_message("assistant").markdown(result.get("answer", "No summary available."))

    elif route == "report":
        with st.spinner("Generating report..."):
            result = graph.invoke({"query": user_query})
        st.chat_message("assistant").markdown(result.get("answer", "No report found."))

    else:
        st.warning("❌ LLM could not determine a valid route.")
