
import streamlit as st
import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

def display_csv_upload():
    st.header("📦 Upload CSV Data to Azure SQL")

    table_columns = {
        "EquipmentInventory": ["NameType", "Manufacturer", "ModelNumber", "SerialNumber", "Location", "PurchaseDate", "WarrantyExpiryDate", "Status"],
        "MaintenanceSchedule": ["EquipmentID", "MaintenanceType", "ScheduledDate", "CompletionDate", "ServiceEngineerName", "MaintenanceStatus"],
        "ComplianceData": ["EquipmentID", "ComplianceType", "LastInspectionDate", "NextInspectionDueDate", "ComplianceStatus", "Documentation"],
        "SparePartsInventory": ["EquipmentType", "PartName", "QuantityAvailable", "LastReplenishedDate", "SupplierInformation"],
        "UserData": ["Name", "Role", "ContactInformation", "CertificationLevels"]
    }

    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("PASSWORD")
    driver = os.getenv("DRIVER")

    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    cursor = conn.cursor()

    table = st.selectbox("Select Table", list(table_columns.keys()))
    uploaded_file = st.file_uploader("Upload your CSV", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        expected_cols = table_columns[table]
        df.columns = [col.strip().replace(' ', '').replace('​', '') for col in df.columns]
        if list(df.columns) != expected_cols:
            st.error(f"❌ Column mismatch! Expected: {expected_cols} | Found: {list(df.columns)}")
        else:
            count = 0
            for _, row in df.iterrows():
                placeholders = ', '.join(['?'] * len(row))
                cursor.execute(f"INSERT INTO {table} ({', '.join(df.columns)}) VALUES ({placeholders})", tuple(row))
                count += 1
            conn.commit()
            st.success(f"✅ Inserted {count} rows into {table}")
