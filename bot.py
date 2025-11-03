import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime

GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')

def get_google_sheet():
    """Connessione a Google Sheets"""
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
    print("=" * 60)
    print("🤖 BOT CLASH ROYALE WAR ANALYSIS")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Connessione
    sheet = get_google_sheet()
    if not sheet:
        print("❌ Errore connessione")
        return False
    
    print("✅ Connessione riuscita!")
    print()
    
    try:
        # Leggi i dati
        all_rows = sheet.get_all_values()
        print(f"📊 Righe nel foglio: {len(all_rows)}")
        
        if len(all_rows) > 1:
            print(f"👥 Giocatori trovati: {len(all_rows) - 1}")
            print()
            
            # Scrivi dati di test nella colonna "Lunedì" (colonna C, indice 3)
            for idx, row in enumerate(all_rows[1:], start=2):
                if len(row) > 1 and row[1]:  # Se c'è un nome
                    # Scrivi "TEST" nella colonna Lunedì (colonna 3)
                    sheet.update_cell(idx, 3, "✅ TEST")
                    print(f"   ✅ {row[1]} - Dati scritti")
            
            print()
            print("✅ BOT COMPLETATO!")
            print("📊 Controlla il Google Sheet!")
            return True
        else:
            print("⚠️  Foglio vuoto")
            return False
    
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

if __name__ == "__main__":
    main
