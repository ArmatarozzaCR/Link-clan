import gspread
from google.oauth2.service_account import Credentials
import requests
from datetime import datetime, timedelta
import os
import json

ROYALE_API_KEY = os.getenv('ROYALE_API_KEY')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')

def get_google_sheet():
    try:
        creds_dict = json.loads(GOOGLE_CREDENTIALS)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
        return sheet
    except Exception as e:
        print(f"❌ Errore: {e}")
        return None

def main():
    print(f"🤖 Bot Clash Royale War Analysis - {datetime.now()}")
    sheet = get_google_sheet()
    if sheet:
        print("✅ Connessione Google Sheets riuscita!")
    else:
        print("❌ Errore connessione")

if __name__ == "__main__":
    main()
