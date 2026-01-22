# Daily Store Visit Reports

## 1. Setup & Install
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 2. Google Sheet Schema
The app writes to Sheet ID: `1D5FQt26Up0XCbcTRvz911OLFDefBYWSsOubuYn_0Ods`
Ensure these columns exist in order:
1.  Timestamp
2.  SR Name
3.  Store Name & Contact Person
4.  Store Visit Type
5.  Store Category
6.  Phone Number
7.  Lead Type
8.  Follow Up Date
9.  Products Interested
10. Order Details
11. Latitude
12. Longitude
13. Google Maps URL
14. Location Recorded (Yes/No)
15. Photo URL / Image

## 3. Geolocation Note
The app uses `navigator.geolocation` via `streamlit-js-eval`. usage requires:
- **HTTPS** (or localhost).
- **Location Permission** allowed in the browser.

## 4. Deploy to Streamlit Cloud
1.  Push text to GitHub.
2.  Deploy.
3.  Add `[gcp_service_account]` secrets in the dashboard.
