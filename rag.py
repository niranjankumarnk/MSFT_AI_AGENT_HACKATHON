import os
import json
import openai
import numpy as np
from typing import List, Dict, Any
from query_engine import retrieve_relevant_chunks
from llm_response import generate_answer_from_context
from mongodb_store import store_manual_data, retrieve_manual_chunks
from S3_store import upload_image_to_s3
from extract_pdf_content import extract_pdf_content
from create_chunks import create_chunks_with_references
from embed_chunks import embed_chunks
import tempfile

class RAG:
    def __init__(self, manual_name: str):
        """
        Initialize RAG system for a given manual
        """
        self.manual_name = manual_name
        self.chunks = retrieve_manual_chunks(manual_name)
        if not self.chunks:
            raise ValueError(f"No chunks found for manual: {manual_name}")

    def process_and_store_manual(self, manual_file, filename: str):
        """
        1. Extract text, images from uploaded manual
        2. Upload images to S3
        3. Create chunks
        4. Embed chunks
        5. Store everything into MongoDB
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(manual_file.read())
            pdf_path = tmp_file.name

        # Extract text and images
        blocks = extract_pdf_content(pdf_path)

        # Upload images to S3 and update URLs
        for block in blocks:
            updated_images = []
            for img in block["images"]:
                s3_url = upload_image_to_s3(img["bytes"], img["filename"], "image/jpeg", manual_folder=filename)
                if s3_url:
                    updated_images.append(s3_url)
            block["images"] = updated_images

        # Chunking
        chunks = create_chunks_with_references(blocks)

        # Embedding
        embeddings, filtered_chunks = embed_chunks(chunks)

        if embeddings is None or len(embeddings) == 0 or len(embeddings.shape) < 2:
            raise ValueError("Embedding failed or returned invalid shape.")

        # Store into MongoDB
        store_manual_data(filename, filtered_chunks, embeddings.tolist(), timestamp=os.path.getmtime(pdf_path))

    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve top-k relevant chunks for the user query
        """
        return retrieve_relevant_chunks(query, self.chunks, model=None, top_k=top_k)

    def build_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Concatenate retrieved chunk texts into a single context
        """
        context_texts = [chunk["text"] for chunk in retrieved_chunks]
        return "\n\n".join(context_texts)

    def extract_images(self, retrieved_chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Get list of S3 image URLs from retrieved chunks
        """
        images = []
        for chunk in retrieved_chunks:
            images.extend(chunk.get("metadata", {}).get("images", []))
        return images

    def generate_response(self, user_query: str, model_name: str = "gpt-4o", top_k: int = 3):
        """
        End-to-end:
        - Retrieve relevant context
        - Generate LLM response
        - Return answer + images if needed
        """
        retrieved_chunks = self.retrieve_context(user_query, top_k)
        context = self.build_context(retrieved_chunks)

        # Generate LLM Answer
        answer = generate_answer_from_context(
            context=context,
            user_query=user_query,
            model_name=model_name
        )

        include_images = any(word in user_query.lower() for word in ["image", "diagram", "picture", "photo", "illustration"])
        images = self.extract_images(retrieved_chunks) if include_images else []

        return answer, images
