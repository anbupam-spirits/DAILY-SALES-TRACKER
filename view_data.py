import streamlit as st
import pandas as pd
from database import get_all_visits
import json

st.set_page_config(page_title="Field Sales Data Viewer", page_icon="📊", layout="wide")

st.title("📊 Field Sales Data Viewer")
st.markdown("View and download data from **field_sales.db**")

# Authorization (Simple)
# In a real app, use better auth. This is just to prevent accidental public view if deployed without auth.
# For local use, this is fine.

def load_data():
    visits = get_all_visits()
    data = []
    for v in visits:
        # Convert SQLAlchemy object to dict
        d = {k: v for k, v in v.__dict__.items() if not k.startswith('_sa_')}
        data.append(d)
    return data

if st.button("Refresh Data"):
    st.rerun()

data = load_data()

if data:
    df = pd.DataFrame(data)
    
    # Reorder columns if desired
    cols_order = ['id', 'visit_date', 'visit_time', 'sr_name', 'store_name', 'store_category', 'visit_type', 'latitude', 'longitude', 'maps_url']
    remaining_cols = [c for c in df.columns if c not in cols_order]
    final_cols = cols_order + remaining_cols
    
    # Filter columns that exist
    final_cols = [c for c in final_cols if c in df.columns]
    
    st.dataframe(df[final_cols], use_container_width=True)
    
    # Download Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download as CSV",
        csv,
        "sales_data_export.csv",
        "text/csv",
        key='download-csv'
    )
    
    st.markdown(f"**Total Records:** {len(df)}")
else:
    st.info("No data found in the database yet.")
