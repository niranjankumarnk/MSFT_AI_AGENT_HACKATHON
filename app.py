
import streamlit as st
from app_sections import assets, upload, manuals

st.set_page_config(page_title="AI Maintenance System", layout="wide")
st.markdown("<h1 style='text-align:center;'>AI-powered Maintenance Platform</h1>", unsafe_allow_html=True)

# Sector dropdown
sector = st.selectbox("Choose Sector", ["Healthcare", "Oil & Gas", "Factory", "Custom"])

# Sidebar navigation
menu = st.sidebar.radio("Navigation", ["Home", "Asset Manager", "Upload CSV", "Manual Assistant"])

# Load modules based on sidebar choice
if menu == "Asset Manager":
    assets.display_asset_manager()
elif menu == "Upload CSV":
    upload.display_csv_upload()
elif menu == "Manual Assistant":
    manuals.display_manual_assistant()
else:
    st.write("Welcome to the unified platform. Use the sidebar to navigate.")
