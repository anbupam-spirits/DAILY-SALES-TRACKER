import streamlit as st
import pandas as pd
from database import get_visits_by_user, update_lead_status
from login_manager import require_auth, logout

st.set_page_config(page_title="User Dashboard", page_icon="📊", layout="wide")

# --- Authentication ---
require_auth()
user = st.session_state.user

# Sidebar
with st.sidebar:
    st.write(f"👤 **{user['full_name']}**")
    if st.button("Logout"):
        logout()

st.title("📊 My Lead Dashboard")

# Fetch Data
visits = get_visits_by_user(user['username'])

if visits:
    # Prepare Data
    data = []
    for v in visits:
        data.append({
            "ID": v.id,
            "Date": v.visit_date,
            "Store": v.store_name,
            "Phone": v.phone_number,
            "Lead Status": v.lead_type,
            "Category": v.store_category,
            "Follow-up": v.follow_up_date
        })
    df = pd.DataFrame(data)

    # --- Charts ---
    st.subheader("Lead Status Overview")
    status_counts = df['Lead Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(status_counts, hide_index=True)
    with col2:
        st.bar_chart(status_counts.set_index('Status'))

    # --- Lead Management ---
    st.markdown("---")
    st.subheader("🏷️ Manage Your Leads")
    st.info("💡 You can change the Lead Status in the table below and click 'Save Changes'.")

    # Use data_editor for interactive updates
    edited_df = st.data_editor(
        df,
        column_config={
            "Lead Status": st.column_config.SelectboxColumn(
                "Lead Status",
                options=["HOT", "WARM", "COLD", "DEAD"],
                required=True,
            )
        },
        disabled=["ID", "Date", "Store", "Phone", "Category", "Follow-up"],
        hide_index=True,
        use_container_width=True,
        key="lead_editor"
    )

    if st.button("💾 Save Changes"):
        updated_count = 0
        # Compare edited_df with df to find changes
        for i, row in edited_df.iterrows():
            original_status = df.iloc[i]['Lead Status']
            new_status = row['Lead Status']
            if original_status != new_status:
                ok, msg = update_lead_status(row['ID'], new_status)
                if ok:
                    updated_count += 1
        
        if updated_count > 0:
            st.success(f"✅ {updated_count} lead(s) updated successfully!")
            st.rerun()
        else:
            st.info("No changes to save.")

    # Details Table
    with st.expander("View Full Visit Details"):
        st.table(df)

else:
    st.info("You haven't entered any visit reports yet.")
