# ============================================================
# PATH + STREAMLIT CONFIG (MUST BE FIRST)
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.set_page_config(
    page_title="Field Sales Reporting",
    page_icon="🚀",
    layout="wide"
)

# ============================================================
# STANDARD IMPORTS
# ============================================================

import time
from datetime import datetime
import base64
from io import BytesIO
from pathlib import Path
import requests

from PIL import Image
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
from streamlit_geolocation import streamlit_geolocation

# ============================================================
# LOCAL MODULE IMPORTS (NO DOTS, NO DUPLICATES)
# ============================================================

from database import (
    init_db,
    save_visit,
    get_all_store_names,
    get_last_visit_by_store,
    update_lead_status
)

from login_manager import require_auth, logout

# ============================================================
# AUTHENTICATION (NO UI BEFORE THIS)
# ============================================================

require_auth()
user = st.session_state.user

# ============================================================
# INITIALIZATION
# ============================================================

init_db()

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

def get_ip_location():
    try:
        response = requests.get("http://ip-api.com/json/", timeout=3)
        data = response.json()
        if data.get("status") == "success":
            return float(data["lat"]), float(data["lon"])
    except Exception:
        pass

    try:
        response = requests.get("https://ipinfo.io/json", timeout=3)
        data = response.json()
        if "loc" in data:
            lat, lon = data["loc"].split(",")
            return float(lat), float(lon)
    except Exception:
        pass

    return None, None

# ============================================================
# SESSION STATE DEFAULTS
# ============================================================

if "loc_lat" not in st.session_state:
    st.session_state.loc_lat = None
if "loc_lon" not in st.session_state:
    st.session_state.loc_lon = None
if "loc_acc" not in st.session_state:
    st.session_state.loc_acc = None

# ============================================================
# CALLBACKS
# ============================================================

def load_store_data():
    selected = st.session_state.get("search_store")

    if selected and selected != "Create New / Search...":
        visit = get_last_visit_by_store(selected)
        if visit:
            st.session_state.store_name = visit.store_name
            st.session_state.phone = visit.phone_number
            st.session_state.visit_type = "RE VISIT"
            st.session_state.category = "HoReCa" if visit.store_category.upper() == "HORECA" else "MT"
            st.session_state.lead_type = visit.lead_type

            prods = visit.products or ""
            st.session_state.p1 = "CIGARETTE" in prods
            st.session_state.p2 = "ROLLING PAPERS" in prods
            st.session_state.p3 = "CIGARS" in prods
            st.session_state.p4 = "HOOKAH" in prods
            st.session_state.p5 = "ZIPPO LIGHTERS" in prods
            st.session_state.p6 = "NONE" in prods

            st.session_state.order_details = ""
            st.session_state.follow_up_date = datetime.now().date()

    else:
        st.session_state.store_name = ""
        st.session_state.phone = ""
        st.session_state.order_details = ""

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.write(f"👤 **{user['full_name']}**")
    st.write(f"Role: {user['role']}")
    if st.button("Logout"):
        logout()

# ============================================================
# MAIN UI
# ============================================================

st.title("DAILY REPORT")

existing_stores = get_all_store_names()

st.selectbox(
    "🔎 SEARCH EXISTING STORE (Auto-fill)",
    ["Create New / Search..."] + existing_stores,
    key="search_store",
    on_change=load_store_data
)

st.text_input("SR NAME *", value=user["full_name"], disabled=True)

store_name_person = st.text_input("STORE NAME AND CONTACT PERSON *", key="store_name")

visit_type = st.radio("STORE VISIT TYPE *", ["NEW VISIT", "RE VISIT"], horizontal=True, key="visit_type")
store_category = st.radio("STORE CATEGORY *", ["MT", "HoReCa"], horizontal=True, key="category")
phone = st.text_input("PHONE NUMBER *", key="phone")
lead_type = st.radio("LEAD TYPE *", ["HOT", "WARM", "COLD", "DEAD"], horizontal=True, key="lead_type")
follow_up_date = st.date_input("FOLLOW UP DATE", key="follow_up_date")

st.markdown("### TOBACCO PRODUCTS")
c1, c2, c3 = st.columns(3)
p1 = c1.checkbox("CIGARETTE", key="p1")
p2 = c2.checkbox("ROLLING PAPERS", key="p2")
p3 = c3.checkbox("CIGARS", key="p3")
p4 = c1.checkbox("HOOKAH", key="p4")
p5 = c2.checkbox("ZIPPO LIGHTERS", key="p5")
p6 = c3.checkbox("NONE", key="p6")

order_details = st.text_area("ORDER DETAILS", key="order_details")

st.markdown("### 📸 PHOTOGRAPH")
cam = st.camera_input("Take Photo")
upl = st.file_uploader("Or Upload", type=["jpg", "jpeg", "png"])
final_photo = cam or upl

st.markdown("### 📍 LOCATION")
location = streamlit_geolocation()

if isinstance(location, dict) and location.get("latitude") is not None:
    st.session_state.loc_lat = location["latitude"]
    st.session_state.loc_lon = location["longitude"]
    st.session_state.loc_acc = location.get("accuracy", 0)
else:
    st.warning("📍 Location not available. Please allow GPS permission in your browser.")


if st.session_state.loc_lat:
    map_link = f"https://www.google.com/maps?q={st.session_state.loc_lat},{st.session_state.loc_lon}"
    st.success("Location Captured")
    st.markdown(f"[Open in Google Maps]({map_link})")

location_recorded_answer = st.radio(
    "DID YOU RECORD THE LOCATION?",
    ["YES", "NO"],
    horizontal=True
)

# ============================================================
# SUBMIT
# ============================================================

st.markdown("---")
submitted = st.button("SUBMIT REPORT", type="primary", use_container_width=True)

if submitted:
    if not final_photo:
        st.error("Photograph required")
    else:
        img = Image.open(final_photo)
        b64_img = image_to_base64(img)

        products = []
        for name, flag in [
            ("CIGARETTE", p1), ("ROLLING PAPERS", p2), ("CIGARS", p3),
            ("HOOKAH", p4), ("ZIPPO LIGHTERS", p5), ("NONE", p6)
        ]:
            if flag:
                products.append(name)

        now = datetime.now()

        visit_data = {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "sr_name": user["full_name"],
            "username": user["username"],
            "store_name": store_name_person,
            "visit_type": visit_type,
            "store_category": store_category,
            "phone": phone,
            "lead_type": lead_type,
            "follow_up_date": str(follow_up_date),
            "products": ", ".join(products),
            "order_details": order_details,
            "latitude": st.session_state.loc_lat,
            "longitude": st.session_state.loc_lon,
            "maps_url": "",
            "location_recorded_answer": location_recorded_answer,
            "image_data": b64_img
        }

        ok, msg = save_visit(visit_data)
        if ok:
            st.success("✅ Report Saved Successfully")
            st.balloons()
        else:
            st.error(msg)
