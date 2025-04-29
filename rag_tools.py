# rag_tools.py

from extract_pdf_content import extract_pdf_content
from create_chunks import create_chunks_with_references
from embed_chunks import embed_chunks
from mongodb_store import store_manual_data, retrieve_manual_chunks
from S3_store import upload_image_to_s3
from llm_response import generate_llm_response
from query_engine import retrieve_relevant_chunks
from bson import ObjectId
import tempfile
import os
import json
import datetime
from dotenv import load_dotenv
import boto3
import base64
import openai

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

import boto3
s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

# ----------- TOOL: Upload and process manual ------------

def upload_manual_tool(file_bytes, filename):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_bytes)
        pdf_path = tmp_file.name

    blocks = extract_pdf_content(pdf_path)
    chunks = create_chunks_with_references(blocks, filename)

    # Upload images to S3
    for block in blocks:
        for img in block["images"]:
            image_bytes = img["bytes"]
            img_filename = img["filename"]
            s3_path = f"manuals/{filename}/images/{img_filename}"
            url = upload_image_to_s3(image_bytes, img_filename, S3_BUCKET_NAME, s3_path)
            img["s3_url"] = url

    # Embed chunks
    embeddings, filtered_chunks = embed_chunks(chunks)

    timestamp = datetime.datetime.now().isoformat()
    store_manual_data(filename, filtered_chunks, embeddings.tolist(), timestamp)

    return f"✅ Uploaded and processed manual: {filename}"

# ----------- TOOL: Retrieve context ------------

def retrieve_context_tool(query, manual_name, top_k=3):
    chunks = retrieve_manual_chunks(manual_name)
    retrieved_chunks = retrieve_relevant_chunks(query, chunks, model = None,  top_k=top_k)
    return retrieved_chunks

# ----------- TOOL: Generate answer ------------

def generate_response_tool(user_query, retrieved_chunks):
    context = retrieved_chunks[0]["text"] if retrieved_chunks else "No context found."

    prompt = f"""Using the following manual content, answer the question clearly.
Context:
{context}

Question: {user_query}
"""

    llm_answer= generate_llm_response(prompt, model_name="deepseek-chat")

    # Handle images if asked
    include_images = any(word in user_query.lower() for word in ["image", "diagram", "drawing", "picture", "figure"])
    image_urls = []

    if include_images:
        chunk = retrieved_chunks[0]
        all_urls = chunk.get("image_urls", [])
        image_urls.extend(all_urls)

    return llm_answer, image_urls
