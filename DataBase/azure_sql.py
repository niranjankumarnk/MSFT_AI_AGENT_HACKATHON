# Import necessary libraries
from dotenv import load_dotenv

import os
import streamlit as st
import pandas as pd
import pyodbc
import uuid

load_dotenv()
# Azure SQL Connection
server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
username = os.getenv("SQL_USERNAME")
password = os.getenv("PASSWORD")
driver = os.getenv("DRIVER")

conn = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
)
cursor = conn.cursor()

# === Table Columns Mapping ===
table_columns = {
    "EquipmentInventory": ["EquipmentID", "NameType", "Manufacturer", "ModelNumber", "SerialNumber", "Location", "PurchaseDate", "WarrantyExpiryDate", "Status"],
    "MaintenanceSchedule": ["ID", "EquipmentID", "MaintenanceType", "ScheduledDate", "CompletionDate", "ServiceEngineerName", "MaintenanceStatus"],
    # "RepairLogs": ["ID", "EquipmentID", "IssueDescription", "DateOfIssue", "RepairStartDate", "RepairCompletionDate", "FaultCodes", "RepairNotes", "PartsReplaced", "DowntimeDuration", "ServiceEngineerName"],
    "ComplianceData": ["ID", "EquipmentID", "ComplianceType", "LastInspectionDate", "NextInspectionDueDate", "ComplianceStatus", "Documentation"],
    "SparePartsInventory": ["PartID", "EquipmentType", "PartName", "QuantityAvailable", "LastReplenishedDate", "SupplierInformation"],
    "UserData": ["UserID", "Name", "Role", "ContactInformation", "CertificationLevels"]
}

st.title("📦 Upload CSV Data to Azure SQL")
csv_table = st.selectbox("Select Table for CSV Upload", list(table_columns.keys()))
uploaded_file = st.file_uploader("Upload your CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip().replace('\xa0', '').replace('\u200b', '') for col in df.columns]
    expected_cols = [col for col in table_columns[csv_table] if col not in ["ID", "EquipmentID" ,"PartID", "UserID"]]
    if set(df.columns) != set(expected_cols):
        st.error(f"❌ Column mismatch! Expected: {expected_cols}\n Found: {list(df.columns)}" )
    else:
        count = 0
        for _, row in df.iterrows():
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['?'] * len(df.columns))
            cursor.execute(f"INSERT INTO {csv_table} ({columns}) VALUES ({placeholders})", tuple(row))
            count += 1
        conn.commit()
        st.success(f"✅ Inserted {count} rows into {csv_table}")

# === Asset Management ===
st.title("🛠️ Equipment Asset Management")
table = st.selectbox("Select Table to Manage", list(table_columns.keys()))
action = st.radio("Choose Action", ["View All", "Add", "Modify", "Delete"])

def generate_input(col, default=""):
    if col.lower().endswith("id") and col not in ["ID"]:
        return str(uuid.uuid4())
    elif "Date" in col:
        return st.date_input(col)
    elif "Status" in col:
        return st.selectbox(col, ["Active", "In Repair", "Retired", "Completed", "Pending", "Overdue", "Compliant", "Non-Compliant"])
    elif "Quantity" in col:
        return st.number_input(col, min_value=0)
    else:
        return st.text_input(col, default)

columns = table_columns[table]

# === View All ===
if action == "View All":
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.dataframe(df)
    if table == "EquipmentInventory":
        st.bar_chart(df["Status"].value_counts())
    elif table == "SparePartsInventory":
        st.bar_chart(df.groupby("PartName")["QuantityAvailable"].sum())

# === Add ===
elif action == "Add":
    with st.form("add_form"):
        inputs = []
        for col in columns:
            if col == "ID":
                continue
            default = str(uuid.uuid4()) if col.lower().endswith("id") and col != "ID" else ""
            inputs.append(generate_input(col, default))
        if st.form_submit_button("Add Record"):
            col_names = ", ".join([c for c in columns if c != "ID"])
            placeholders = ", ".join(["?"] * len(inputs))
            cursor.execute(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})", inputs)
            conn.commit()
            st.success("✅ Record added.")

# === Modify ===
elif action == "Modify":
    pk = st.text_input(f"Enter {columns[0]} to Modify")
    if pk:
        df = pd.read_sql(f"SELECT * FROM {table} WHERE {columns[0]} = ?", conn, params=(pk,))
        if not df.empty:
            with st.form("mod_form"):
                updated = []
                for col in columns[1:]:
                    val = str(df.iloc[0][col]) if pd.notna(df.iloc[0][col]) else ""
                    updated.append(generate_input(col, val))
                if st.form_submit_button("Update"):
                    set_clause = ", ".join([f"{col}=?" for col in columns[1:]])
                    cursor.execute(f"UPDATE {table} SET {set_clause} WHERE {columns[0]} = ?", (*updated, pk))
                    conn.commit()
                    st.success("✅ Record updated.")
        else:
            st.warning("⚠️ Record not found.")

# === Delete ===
elif action == "Delete":
    pk = st.text_input(f"Enter {columns[0]} to Delete")
    if st.button("Delete Record"):
        cursor.execute(f"DELETE FROM {table} WHERE {columns[0]} = ?", pk)
        conn.commit()
        st.success("✅ Record deleted.")
