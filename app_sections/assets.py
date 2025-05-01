
import streamlit as st
import pandas as pd
import pyodbc
import uuid
import os
# from plots import display_analytics_section
from dotenv import load_dotenv

# import plotly.express as px
from datetime import datetime

load_dotenv()




import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# def display_analytics_section(df):
#     tab1, tab2 = st.tabs(["📋 Table View", "📊 Interactive Analytics"])

#     # Tab 1: Raw Table
#     with tab1:
#         st.subheader("Equipment Inventory Table")
#         st.dataframe(df)

#     # Tab 2: Visual Analytics
#     with tab2:
#         st.subheader("📊 Equipment Distribution by Type")
#         fig1, ax1 = plt.subplots()
#         df["NameType"].value_counts().plot.pie(autopct="%1.1f%%", ax=ax1, startangle=90)
#         ax1.set_ylabel("")
#         st.pyplot(fig1)

#         st.subheader("📈 Equipment Status Overview")
#         st.bar_chart(df["Status"].value_counts())

#         st.subheader("📍 Equipment by Location")
#         fig2, ax2 = plt.subplots()
#         sns.barplot(x=df["Location"].value_counts().index,
#                     y=df["Location"].value_counts().values, ax=ax2)
#         ax2.set_xlabel("Location")
#         ax2.set_ylabel("Count")
#         plt.xticks(rotation=45)
#         st.pyplot(fig2)

#         st.subheader("🕒 Purchases Over the Years")
#         df["Year"] = pd.to_datetime(df["PurchaseDate"]).dt.year
#         st.line_chart(df["Year"].value_counts().sort_index())


def display_equipment_dashboard(df: pd.DataFrame):
    import streamlit as st

    st.subheader("📋 EquipmentInventory Dashboard")

    # === Filter Section ===
    with st.expander("🔍 Filter Data", expanded=True):
        col1, col2 = st.columns(2)
        selected_status = col1.multiselect("Filter by Status", df["Status"].unique(), default=list(df["Status"].unique()))
        selected_location = col2.multiselect("Filter by Location", df["Location"].unique(), default=list(df["Location"].unique()))
        df = df[df["Status"].isin(selected_status) & df["Location"].isin(selected_location)]

    # === KPI Section ===
    st.markdown("### 📊 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Equipments", len(df))
    col2.metric("Active", (df["Status"] == "Active").sum())
    col3.metric("Retired", (df["Status"] == "Retired").sum())

    # === Charts ===
    st.markdown("### 📈 Charts")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Status Distribution")
        st.bar_chart(df["Status"].value_counts())

    with col2:
        st.markdown("#### Purchase Trend by Year")
        df["Year"] = pd.to_datetime(df["PurchaseDate"]).dt.year
        year_summary = df["Year"].value_counts().sort_index()
        st.line_chart(year_summary)

    st.markdown("#### Equipment Count by Location")
    st.bar_chart(df["Location"].value_counts())

    # === Raw Table ===
    st.markdown("### 📄 Full Data")
    st.dataframe(df)
    
    return df

def display_maintenance_dashboard(df: pd.DataFrame):
    st.subheader("🛠️ Maintenance Schedule Dashboard")

    # === Filter Section ===
    with st.expander("🔍 Filter Data", expanded=True):
        col1, col2 = st.columns(2)
        selected_status = col1.multiselect("Filter by Status", df["MaintenanceStatus"].unique(), default=list(df["MaintenanceStatus"].unique()))
        selected_type = col2.multiselect("Filter by Type", df["MaintenanceType"].unique(), default=list(df["MaintenanceType"].unique()))
        df = df[df["MaintenanceStatus"].isin(selected_status) & df["MaintenanceType"].isin(selected_type)]

    # === KPI Section ===
    st.markdown("### 📊 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Maintenance Records", len(df))
    col2.metric("Completed", (df["MaintenanceStatus"] == "Completed").sum())
    col3.metric("Pending", (df["MaintenanceStatus"] == "Pending").sum())

    # === Charts ===
    st.markdown("### 📈 Charts")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Status Distribution")
        st.bar_chart(df["MaintenanceStatus"].value_counts())

    with col2:
        st.markdown("#### Maintenance Type Distribution")
        st.bar_chart(df["MaintenanceType"].value_counts())

    # === Raw Table ===
    st.markdown("### 📄 Full Data")
    st.dataframe(df)
    return df

def display_asset_manager():
    st.header("🛠️ Equipment Asset Management")
    
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

    table_columns = {
        "EquipmentInventory": ["EquipmentID", "NameType", "Manufacturer", "ModelNumber", "SerialNumber", "Location", "PurchaseDate", "WarrantyExpiryDate", "Status"],
        "MaintenanceSchedule": ["ID", "EquipmentID", "MaintenanceType", "ScheduledDate", "CompletionDate", "ServiceEngineerName", "MaintenanceStatus"],
        "ComplianceData": ["ID", "EquipmentID", "ComplianceType", "LastInspectionDate", "NextInspectionDueDate", "ComplianceStatus", "Documentation"],
        "SparePartsInventory": ["PartID", "EquipmentType", "PartName", "QuantityAvailable", "LastReplenishedDate", "SupplierInformation"],
        "UserData": ["UserID", "Name", "Role", "ContactInformation", "CertificationLevels"]
    }

    table = st.selectbox("Select Table", list(table_columns.keys()))
    action = st.radio("Choose Action", ["View All", "Add", "Modify", "Delete"])
    columns = table_columns[table]
    
    
    def fetch_dashboard_summary():
        tables = ["EquipmentInventory", "MaintenanceSchedule", "ComplianceData"]
        summary = {}

        for table in tables:
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
            summary[table] = df.to_dict(orient='records')

        return summary
        


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

    if action == "View All":
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        if table == "EquipmentInventory":
            display_equipment_dashboard(df)
        elif table == "MaintenanceSchedule":
            display_maintenance_dashboard(df)
        else:
        # df = pd.read_sql("SELECT * FROM EquipmentInventory", conn)
            st.subheader(f"Viewing {table}")
            st.dataframe(df)

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

    elif action == "Delete":
        pk = st.text_input(f"Enter {columns[0]} to Delete")
        if st.button("Delete Record"):
            cursor.execute(f"DELETE FROM {table} WHERE {columns[0]} = ?", pk)
            conn.commit()
            st.success("✅ Record deleted.")


