import streamlit as st
import pandas as pd
from database import get_all_visits
from login_manager import require_auth, logout

st.set_page_config(page_title="Admin Dashboard", page_icon="🔒", layout="wide")

# --- Authentication ---
require_auth()
user = st.session_state.user

if user['role'] != 'ADMIN':
    st.error("🚫 Access Denied. Admin privileges required.")
    st.stop()

# Sidebar
with st.sidebar:
    st.write(f"👤 **{user['full_name']}**")
    if st.button("Logout"):
        logout()

st.title("📊 Admin Dashboard")
st.subheader("All Store Visits")

visits = get_all_visits()

if visits:
    # Convert SQLAlchemy objects to Dictionary for DataFrame
    data = []
    for v in visits:
        data.append({
            "ID": v.id,
            "Date": v.visit_date,
            "Time": v.visit_time,
            "SR Name": v.sr_name,
            "Store": v.store_name,
            "Type": v.visit_type,
            "Category": v.store_category,
            "Phone": v.phone_number,
            "Lead": v.lead_type,
            "Products": v.products,
            "Lat": v.latitude,
            "Lon": v.longitude,
            "Map": v.maps_url
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    # Export Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download CSV",
        csv,
        "store_visits_export.csv",
        "text/csv",
        key='download-csv'
    )
else:
    st.info("No records found in the database.")
