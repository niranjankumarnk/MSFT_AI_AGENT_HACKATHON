
import streamlit as st

import manuals
import csv_upload
import assets
import blog


st.set_page_config(page_title="AI Maintenance System", layout="wide")
st.markdown("<h1 style='text-align:center;'>AI-powered Maintenance Platform</h1>", unsafe_allow_html=True)

# Sector dropdown
sector = st.selectbox("Choose Sector", ["Healthcare", "Oil & Gas", "Factory", "Custom"])

# Sidebar navigation
menu = st.sidebar.radio("Navigation", ["Home", "Asset Manager", "Upload CSV", "Manual Assistant", "Blog Generation"])

# Load modules based on sidebar choice
if menu == "Asset Manager":
    assets.display_asset_manager()
elif menu == "Upload CSV":
    csv_upload.display_csv_upload()
elif menu == "Manual Assistant":
    manuals.display_manual_assistant()
elif menu =="Blog Generation":
    blog.display_blog_creator()
else:
    st.write("Welcome to the unified platform. Use the sidebar to navigate.")
