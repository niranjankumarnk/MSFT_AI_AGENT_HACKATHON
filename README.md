# 🧠 AI Agents Based Predictive Maintenance – Industry Equipment

This project provides an intelligent, agent-powered platform to manage, monitor, and maintain industrial equipment. Built using **LangGraph**, **Azure**, and **Streamlit**, it features:
- AI-based troubleshooting from manuals (RAG)
- Asset management and dashboard analytics
- CSV uploads to Azure SQL
- Equipment summary + report generation
- A generative blog agent for content creation

---

## 🚀 Features

### 1. 📄 Manual Assistant (RAG)
- Upload or search equipment manuals
- Extracts both images and text from PDFs
- Stores content in **MongoDB** and **Azure Blob Storage**
- Answers troubleshooting questions with visual support

### 2. 🛠️ Asset Manager (Azure SQL)
- Add, view, modify, and delete assets
- Interact with dashboards:
  - Equipment Status Distribution
  - Compliance Summary
  - Spare Part Availability

### 3. 📤 CSV Uploader
- Upload CSV files to any table
- Validates schema before ingestion
- Supports bulk upload to Azure SQL

### 4. 📊 Dashboard Summary & Report Generator
- **LLM routing** decides:
  - RAG for manual-based queries
  - Dashboard summary from SQL
  - Report generation for individual equipment

### 5. ✍️ Blog Creator Agent
- Powered by GPT-4o via LangGraph
- Generate blog titles & full-length content
- Simple UI for marketing/technical content generation

---

## 🧩 Tech Stack

| Layer       | Tools/Tech Used                            |
|-------------|---------------------------------------------|
| Backend     | Python, LangGraph, LangChain, OpenAI GPT-4o |
| Frontend    | Streamlit                                   |
| Storage     | MongoDB, Azure Blob Storage, Azure SQL      |
| DevOps      | Git, GitHub, dotenv                         |

---

## 📁 Project Structure

```bash
├── Agentic_RAG/                 # RAG graph logic
├── DataBase/                    # Azure SQL schema logic
├── Equipment_data/              # Data files (CSV)
├── RAG_modules/                 # PDF parsing and vector storage
├── manuals/                     # Processed manual storage
├── app.py                       # Streamlit main app
├── blog_generation.py           # LangGraph blog agent
├── asset_generation.py          # Asset SQL logic
├── csv_upload.py                # CSV uploader logic
├── manuals.py                   # Manual assistant logic
├── README.md
