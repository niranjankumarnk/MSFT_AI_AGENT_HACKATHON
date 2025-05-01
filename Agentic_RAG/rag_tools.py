# rag_tools.py

from RAG_modules.extract_pdf_content import extract_pdf_content
from RAG_modules.create_chunks import create_chunks_with_references
from RAG_modules.embed_chunks import embed_chunks
from RAG_modules.Azure_CosmoDB import store_manual_data, retrieve_manual_chunks
# from S3_store import upload_image_to_s3
from RAG_modules.azure_store import upload_image_to_azure
from RAG_modules.llm_response import generate_llm_response
from RAG_modules.query_engine import retrieve_relevant_chunks
from RAG_modules.Azure_CosmoDB import retrieve_manual_chunks
from botocore.exceptions import ClientError
from bson import ObjectId
import tempfile
import os
import json
import datetime
from dotenv import load_dotenv
import boto3
import base64
import openai
import re
import pyodbc
import pandas as pd


load_dotenv()

# AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
# AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
# S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# import boto3
# s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

# ----------- TOOL: Upload and process manual ------------

def upload_manual_tool(file_bytes, filename):
    if manual_exists(filename):
        print(f"🟡 Manual {filename} already exists in DB. Skipping processing.")
        return f"Manual '{filename}' already exists."

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_bytes)
        pdf_path = tmp_file.name

    blocks = extract_pdf_content(pdf_path)
    

    for block in blocks:
        for img in block.get("images", []):
            image_bytes = img["bytes"]
            img_filename = img["filename"]
            content_type = "image/jpeg" if img_filename.endswith(".jpeg") else "image/png"

            # Upload and store Azure URL
            azure_url = upload_image_to_azure(image_bytes, img_filename, content_type, manual_folder=filename)
            if azure_url:
                img["s3_url"] = azure_url  # store the URL for later chunk processing
                
    chunks = create_chunks_with_references(blocks, filename)
    for chunk in chunks:
        print("Chunk images:", chunk["metadata"].get("image_urls"))

    embeddings, filtered_chunks = embed_chunks(chunks)
    timestamp = datetime.datetime.now().isoformat()
    store_manual_data(filename, filtered_chunks, embeddings.tolist(), timestamp)
    
    return f"✅ Uploaded and processed manual: {filename}"
# ----------- TOOL: Retrieve context ------------

def retrieve_context_tool(query, manual_name, top_k=3):
    if not manual_name:
        return []  # Avoid crashing if filename is missing
    chunks = retrieve_manual_chunks(manual_name)
    retrieved_chunks = retrieve_relevant_chunks(query, chunks, model = None,  top_k=top_k)
    return retrieved_chunks

# ----------- TOOL: Generate answer ------------

def generate_response_tool(user_query, retrieved_chunks, dashboard_context=None):
    if not retrieved_chunks:
        return "⚠️ No relevant information found in the manual.", []

    chunk = retrieved_chunks[0]
    context = chunk["text"]

    prompt = f"""Using the following manual content, answer the question clearly.
    Manual Context:
    {context}

    Dashboard Data:
    {dashboard_context or 'No dashboard data'}

    Question: {user_query}
    """

    llm_answer = generate_llm_response(prompt, model_name="deepseek-chat")

    all_image_urls = []
    for chunk in retrieved_chunks:
        if "image_urls" in chunk:
            all_image_urls.extend(chunk["image_urls"])

    return llm_answer, all_image_urls


def manual_exists(manual_name):
    try:
        chunks = retrieve_manual_chunks(manual_name)
        return chunks is not None and len(chunks) > 0
    except:
        return False

    
    
    
    
    
# # Azure SQL Connection
# server = os.getenv("SQL_SERVER")
# database = os.getenv("SQL_DATABASE")
# username = os.getenv("SQL_USERNAME")
# password = os.getenv("PASSWORD")
# driver = os.getenv("DRIVER")
    
# def fetch_equipment_summary():
#     conn = pyodbc.connect(
#         f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
#     )
    
#     query = """
#     SELECT Status, COUNT(*) as Count FROM EquipmentInventory GROUP BY Status;
#     """
#     df = pd.read_sql(query, conn)
#     summary = df.to_string(index=False)
#     return f"Equipment Status Summary:\n{summary}"

    

# def llm_router_tool(query):
#     prompt = f"""
#     Decide the correct action based on the user's question.

#     Options:
#     - RAG: If asking about manuals, step-by-step instructions, images, or troubleshooting.
#     - SUMMARY: If asking for equipment counts, status summaries, inventory levels, etc.
#     - REPORT: If asking for a detailed analysis or report about a specific equipment.

#     Query: {query}
#     Response (choose one: RAG, SUMMARY, REPORT):
#     """
#     response = generate_llm_response(prompt)
#     return response.strip().upper()



# def fetch_dashboard_summary_tool(conn) -> str:
#     summary = ""

#     # Equipment status summary
#     equipment_df = pd.read_sql("SELECT Status FROM EquipmentInventory", conn)
#     status_counts = equipment_df["Status"].value_counts()
#     summary += "### Equipment Status Summary\n"
#     for status, count in status_counts.items():
#         summary += f"- {status}: {count}\n"

#     # Spare parts inventory
#     parts_df = pd.read_sql("SELECT PartName, SUM(QuantityAvailable) as Total FROM SparePartsInventory GROUP BY PartName", conn)
#     summary += "\n### Spare Parts Inventory\n"
#     for _, row in parts_df.iterrows():
#         summary += f"- {row['PartName']}: {row['Total']} units\n"

#     # Compliance status
#     compliance_df = pd.read_sql("SELECT ComplianceStatus FROM ComplianceData", conn)
#     comp_counts = compliance_df["ComplianceStatus"].value_counts()
#     summary += "\n### Compliance Overview\n"
#     for status, count in comp_counts.items():
#         summary += f"- {status}: {count}\n"

#     return summary

# def generate_equipment_report_tool(equipment_name: str, conn) -> str:
#     report = f"# Equipment Report for Name: {equipment_name}\n"

#     # Try partial match using LIKE
#     equip_df = pd.read_sql(
#         "SELECT * FROM EquipmentInventory WHERE NameType LIKE ?",
#         conn,
#         params=(f"%{equipment_name}%",)
#     )

#     if equip_df.empty:
#         fallback_names = pd.read_sql("SELECT DISTINCT NameType FROM EquipmentInventory", conn)
#         name_list = "\n- " + "\n- ".join(fallback_names["NameType"].tolist())
#         return f"⚠️ No equipment found matching '{equipment_name}'. Available equipment types:\n{name_list}"

#     for idx, eq in equip_df.iterrows():
#         equipment_id = eq["EquipmentID"]
#         report += f"\n## Equipment {idx+1}: {equipment_id}\n"
#         report += f"- Location: {eq['Location']}\n- Status: {eq['Status']}\n"

#         # Maintenance
#         maint = pd.read_sql("SELECT * FROM MaintenanceSchedule WHERE EquipmentID = ?", conn, params=(equipment_id,))
#         report += "\n### Maintenance Records\n"
#         report += "- No records.\n" if maint.empty else "\n".join([
#             f"- {row['MaintenanceType']} on {row['ScheduledDate']} (Status: {row['MaintenanceStatus']})"
#             for _, row in maint.iterrows()
#         ])

#         # Compliance
#         compliance = pd.read_sql("SELECT * FROM ComplianceData WHERE EquipmentID = ?", conn, params=(equipment_id,))
#         report += "\n\n### Compliance Records\n"
#         report += "- No records.\n" if compliance.empty else "\n".join([
#             f"- {row['ComplianceType']} (Last: {row['LastInspectionDate']}, Status: {row['ComplianceStatus']})"
#             for _, row in compliance.iterrows()
#         ])

#         report += "\n"

#     return report


# import re

# def extract_equipment_name(query: str, valid_names: list[str]) -> str:
#     query_lower = query.lower()
#     for name in valid_names:
#         if name.lower() in query_lower:
#             return name
#     # fallback: try extracting the last noun phrase (naive)
#     match = re.search(r"for ([\w\s\-]+)\??", query_lower)
#     return match.group(1).strip().title() if match else query
