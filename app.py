import streamlit as st
st.set_page_config(page_title="Field Sales Reporting", page_icon="🚀", layout="wide")

import time
from datetime import datetime
import base64
from io import BytesIO
import os
from pathlib import Path
from PIL import Image
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
from streamlit_geolocation import streamlit_geolocation
from database import init_db, save_visit, get_all_store_names, get_last_visit_by_store, update_lead_status
from login_manager import require_auth, logout

# --- Authentication ---
require_auth()
user = st.session_state.user

# --- Initialization ---
# Create tables if they don't exist
init_db()

# --- Helper Functions ---
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

def get_ip_location():
    """Fetch location from multiple IP APIs for better reliability."""
    # 1. Try IP-API (Often more accurate for free tier)
    try:
        response = requests.get("http://ip-api.com/json/", timeout=3)
        data = response.json()
        if data.get('status') == 'success':
            return float(data['lat']), float(data['lon'])
    except Exception:
        pass
    
    # 2. Fallback to IPInfo
    try:
        response = requests.get("https://ipinfo.io/json", timeout=3)
        data = response.json()
        if 'loc' in data:
            lat, lon = data['loc'].split(',')
            return float(lat), float(lon)
    except Exception:
        pass
        
    return None, None

# --- Session State ---
if 'loc_lat' not in st.session_state: st.session_state.loc_lat = None
if 'loc_lon' not in st.session_state: st.session_state.loc_lon = None

# --- Pre-fill Callback ---
def load_store_data():
    """Callback to load data when a store is selected."""
    selected = st.session_state.get("search_store")
    
    # If user just typed something in store_name and clicked RE VISIT, we also want to trigger this.
    # But usually, this callback is for the selectbox.
    
    if selected and selected != "Create New / Search...":
        visit = get_last_visit_by_store(selected)
        if visit:
            st.session_state.store_name = visit.store_name
            st.session_state.sr_name = visit.sr_name
            st.session_state.phone = visit.phone_number
            st.session_state.visit_type = "RE VISIT"
            
            # Map category to match widget options
            cat_val = visit.store_category
            if cat_val and cat_val.upper() == "HORECA":
                st.session_state.category = "HoReCa"
            elif cat_val and cat_val.upper() == "MT":
                st.session_state.category = "MT"
            else:
                st.session_state.category = "MT"
            
            st.session_state.lead_type = visit.lead_type
            
            # Map products string back to booleans
            prods = visit.products if visit.products else ""
            st.session_state.p1 = "CIGARETTE" in prods
            st.session_state.p2 = "ROLLING PAPERS" in prods
            st.session_state.p3 = "CIGARS" in prods
            st.session_state.p4 = "HOOKAH" in prods
            st.session_state.p5 = "ZIPPO LIGHTERS" in prods
            st.session_state.p6 = "NONE" in prods
            
            # CLEAR visit-specific details for Re-visit
            st.session_state.order_details = ""
            st.session_state.follow_up_date = datetime.now().date()
            # Photo and Location are managed separately by their widgets
            
    elif selected == "Create New / Search...":
        # Clear fields for new entry
        st.session_state.store_name = ""
        st.session_state.phone = ""
        st.session_state.p1 = False
        st.session_state.p2 = False
        st.session_state.p3 = False
        st.session_state.p4 = False
        st.session_state.p5 = False
        st.session_state.p6 = False
        st.session_state.order_details = ""
        st.session_state.follow_up_date = datetime.now().date()


# --- UI ---
st.set_page_config(page_title="Daily Store Reports", page_icon="📝", layout="centered")

# Sidebar for User Info & Logout
with st.sidebar:
    st.write(f"👤 **Logged in as:** {user['full_name']}")
    st.write(f"Role: {user['role']}")
    if st.button("Logout"):
        logout()

st.title("DAILY REPORT")

# --- Main Form Container ---
with st.container():
    # Fetch existing stores for the dropdown
    existing_stores = get_all_store_names()
    
    # Search Box with Callback
    st.selectbox(
        "🔎 SEARCH EXISTING STORE (Auto-fill)", 
        ["Create New / Search..."] + existing_stores, 
        key="search_store",
        on_change=load_store_data
    )

    # sr_name = st.selectbox("SR NAME *", ["SHUBRAM KAR", "RAJU DAS"], key="sr_name")
    # Defaulting to the logged in user's full name
    sr_name = st.text_input("SR NAME *", value=user['full_name'], key="sr_name_input", disabled=True)
    # Using the value for the database
    sr_name_val = sr_name
    store_name_person = st.text_input("STORE NAME AND CONTACT PERSON *", key="store_name")
    
    # ... rest of fields
    # Logic for auto-populating when RE VISIT is clicked
    def handle_visit_type_change():
        if st.session_state.visit_type == "RE VISIT" and st.session_state.store_name:
            # Check if this name exists in DB
            visit = get_last_visit_by_store(st.session_state.store_name)
            if visit:
                st.session_state.sr_name = visit.sr_name
                st.session_state.phone = visit.phone_number
                
                # Map category to match widget options
                cat_val = visit.store_category
                if cat_val and cat_val.upper() == "HORECA":
                    st.session_state.category = "HoReCa"
                elif cat_val and cat_val.upper() == "MT":
                    st.session_state.category = "MT"
                else:
                    st.session_state.category = "MT"
                    
                st.session_state.lead_type = visit.lead_type
                
                prods = visit.products if visit.products else ""
                st.session_state.p1 = "CIGARETTE" in prods
                st.session_state.p2 = "ROLLING PAPERS" in prods
                st.session_state.p3 = "CIGARS" in prods
                st.session_state.p4 = "HOOKAH" in prods
                st.session_state.p5 = "ZIPPO LIGHTERS" in prods
                st.session_state.p6 = "NONE" in prods
                
                # Clear visit-specific details
                st.session_state.order_details = ""
                st.session_state.follow_up_date = datetime.now().date()
            else:
                st.warning("No previous data found for this store name.")

    visit_type = st.radio("STORE VISIT TYPE *", ["NEW VISIT", "RE VISIT"], horizontal=True, key="visit_type", on_change=handle_visit_type_change)
    store_category = st.radio("STORE CATEGORY *", ["MT", "HoReCa"], horizontal=True, key="category")
    phone = st.text_input("PHONE NUMBER *", key="phone")
    lead_type = st.radio("LEAD TYPE *", ["HOT", "WARM", "COLD", "DEAD"], horizontal=True, key="lead_type")
    follow_up_date = st.date_input("FOLLOW UP DATE", key="follow_up_date")
    
    st.write("TOBACCO PRODUCTS INTERESTED IN / THEY DEAL IN *")
    c1, c2, c3 = st.columns(3)
    p1 = c1.checkbox("CIGARETTE", key="p1")
    p2 = c2.checkbox("ROLLING PAPERS", key="p2")
    p3 = c3.checkbox("CIGARS", key="p3")
    p4 = c1.checkbox("HOOKAH", key="p4")
    p5 = c2.checkbox("ZIPPO LIGHTERS", key="p5")
    p6 = c3.checkbox("NONE", key="p6")

    order_details = st.text_area("ORDER DETAILS IF CONVERTED (Optional)", key="order_details")
    
    st.markdown("### 📸 PHOTOGRAPH *")
    cam_val = st.camera_input("Take Photo", key="camera")
    upl_val = st.file_uploader("Or Upload", type=['jpg','png','jpeg'], key="upload")
    final_photo = cam_val if cam_val else upl_val

    st.markdown("---")
    st.markdown("### 📍 LOCATION CAPTURE")
    
    # --- ULTIMATE GPS LOGIC (Using dedicated streamlit-geolocation) ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("🛰️ **Precision GPS**")
        # Direct hardware access component
        location = streamlit_geolocation()
        
        if location and location.get('latitude'):
            # Only update if different to avoid refresh loops
            if st.session_state.loc_lat != location['latitude']:
                st.session_state.loc_lat = location['latitude']
                st.session_state.loc_lon = location['longitude']
                st.session_state.loc_acc = location.get('accuracy', 0)
                st.rerun()

    with col2:
        st.write("🌐 **Fallbacks**")
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            if st.button("Network", key="btn_net", use_container_width=True):
                with st.spinner("Wait..."):
                    lat, lon = get_ip_location()
                    if lat:
                        st.session_state.loc_lat = lat
                        st.session_state.loc_lon = lon
                        st.session_state.loc_acc = 500
                        st.rerun()
        with col_sub2:
            if st.button("Reset", key="btn_reset", use_container_width=True):
                st.session_state.loc_lat = None
                st.session_state.loc_lon = None
                st.rerun()

    # Display Result
    if st.session_state.loc_lat:
        lat_disp = st.session_state.loc_lat
        lon_disp = st.session_state.loc_lon
        acc_disp = st.session_state.get('loc_acc', 0)
        map_link = f"https://www.google.com/maps?q={lat_disp},{lon_disp}"
        
        st.success(f"📍 Location Captured! (Accuracy: {acc_disp:.1f}m)")
        st.markdown(f"**Google Maps Link:** [{map_link}]({map_link})")
    else:
        st.info("👆 Click the GPS icon above to record location.")
    
    location_recorded_answer = st.radio("DID YOU RECORD THE LOCATION? *", ["YES", "NO"], horizontal=True, key="loc_recorded")

    # --- Visit Summary & Photos (Optional Display) ---
    # ... existing logic ...

# --- SUBMIT BUTTON (OUTSIDE CONTAINER) ---
st.markdown("---")
# Use full width container for button area to separate it visually
with st.container():
    submitted = st.button("SUBMIT REPORT", type="primary", use_container_width=True)

if submitted:
    # Validation
    errors = []
    if not store_name_person: errors.append("Store Name is required.")
    if not phone: errors.append("Phone Number is required.")
    if not final_photo: errors.append("Photograph is required.")
    
    products = []
    if p1: products.append("CIGARETTE")
    if p2: products.append("ROLLING PAPERS")
    if p3: products.append("CIGARS")
    if p4: products.append("HOOKAH")
    if p5: products.append("ZIPPO LIGHTERS")
    if p6: products.append("NONE")
    if not products: errors.append("Select at least one Product.")
    
    final_lat = ""
    final_lon = ""
    if location_recorded_answer == "YES":
        if st.session_state.loc_lat is None:
             errors.append("You said YES to location, but none is recorded. Please check 'Record Location'.")
        else:
             final_lat = str(st.session_state.loc_lat)
             final_lon = str(st.session_state.loc_lon)

    if errors:
        for e in errors:
            st.error(f"❌ {e}")
    else:
        try:
            img = Image.open(final_photo)
            img.thumbnail((800,800))
            b64_img = image_to_base64(img)
            prod_str = ", ".join(products)
            maps_url = ""
            if final_lat and final_lon:
                maps_url = f"https://www.google.com/maps?q={final_lat},{final_lon}"
                
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")
            
            # Prepare Dictionary for Database
            visit_data = {
                "date": current_date,
                "time": current_time,
                "sr_name": user['full_name'],
                "username": user['username'],
                "store_name": store_name_person,
                "visit_type": visit_type,
                "store_category": store_category,
                "phone": phone,
                "lead_type": lead_type,
                "follow_up_date": str(follow_up_date),
                "products": prod_str,
                "order_details": order_details,
                "latitude": final_lat,
                "longitude": final_lon,
                "maps_url": maps_url,
                "location_recorded_answer": location_recorded_answer,
                "image_data": b64_img
            }
            
            with st.spinner("Saving to Secure Database..."):
                ok, msg = save_visit(visit_data)
                if ok:
                    st.success("✅ Report Saved Successfully to Database!")
                    st.balloons()
                    # Optional: reset fields
                else:
                    st.error(f"❌ Database Error: {msg}")
        except Exception as e:
            st.error(f"❌ Processing Error: {e}")
