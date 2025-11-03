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
        # Verifica che il JSON non sia vuoto
        if not GOOGLE_CREDENTIALS or GOOGLE_CREDENTIALS.strip() == '':
            print("❌ GOOGLE_CREDENTIALS è vuoto!")
            return None
        
        print(f"📝 Parsando JSON...")
        creds_dict = json.loads(GOOGLE_CREDENTIALS)
        
        print(f"🔐 Autenticando con Google...")
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        print(f"📊 Connettendosi a Google Sheets...")
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
        return sheet
    except json.JSONDecodeError as e:
        print(f"❌ Errore JSON: {e}")
        print(f"   Valore ricevuto: {GOOGLE_CREDENTIALS[:50]}...")
        return None
    except Exception as e:
        print(f"❌ Errore: {e}")
        return None

def main():
    print(f"🤖 Bot Clash Royale War Analysis - {datetime.now()}")
    print()
    
    # Verifica environment variables
    print("📋 Verificando environment variables...")
    print(f"   ROYALE_API_KEY: {'✅ Set' if ROYALE_API_KEY else '❌ Non set'}")
    print(f"   GOOGLE_SHEET_ID: {'✅ Set' if GOOGLE_SHEET_ID else '❌ Non set'}")
    print(f"   GOOGLE_CREDENTIALS: {'✅ Set' if GOOGLE_CREDENTIALS else '❌ Non set'}")
    print()
    
    sheet = get_google_sheet()
    if sheet:
        print("✅ Connessione Google Sheets riuscita!")
        print("✅ Bot pronto per domani!")
    else:
        print("❌ Errore connessione")

if __name__ == "__main__":
    main()
