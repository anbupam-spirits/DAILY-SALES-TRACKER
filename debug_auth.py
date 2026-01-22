import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys

SHEET_ID = "1D5FQt26Up0XCbcTRvz911OLFDefBYWSsOubuYn_0Ods"
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

print("--- Starting Auth Debug ---")
try:
    print("1. Loading Credentials...")
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
    print("   Credentials loaded successfully.")
except Exception as e:
    print(f"FAILED to load credentials: {e}")
    sys.exit(1)

try:
    print("2. Authorizing Client...")
    client = gspread.authorize(creds)
    print("   Client authorized.")
except Exception as e:
    print(f"FAILED to authorize client: {e}")
    sys.exit(1)

try:
    print(f"3. Opening Sheet ID: {SHEET_ID}")
    sheet = client.open_by_key(SHEET_ID).sheet1
    print("   Sheet opened successfully.")
except Exception as e:
    print(f"FAILED to open sheet: {e}")
    print("POSSIBLE CAUSES:")
    print(" - The Sheet ID is wrong.")
    print(" - The Service Account email has not been added as an 'Editor' to the Google Sheet.")
    print(" - The Google Sheets API is not enabled on the Cloud Project.")
    sys.exit(1)

print("--- Debug Complete: Connection works! ---")
