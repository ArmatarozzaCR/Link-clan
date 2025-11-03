import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime
import traceback

GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')

def main():
    try:
        print("=" * 60)
        print("🤖 BOT CLASH ROYALE WAR ANALYSIS")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
        
        # Verifica environment
        print("1️⃣ Verificando environment variables...")
        if not GOOGLE_SHEET_ID:
            print("❌ GOOGLE_SHEET_ID mancante!")
            return False
        if not GOOGLE_CREDENTIALS:
            print("❌ GOOGLE_CREDENTIALS mancante!")
            return False
        print("✅ Variables OK")
        print()
        
        # Parse JSON
        print("2️⃣ Parsando JSON...")
        try:
            creds_dict = json.loads(GOOGLE_CREDENTIALS)
            print("✅ JSON parsato correttamente")
        except json.JSONDecodeError as e:
            print(f"❌ Errore JSON: {e}")
            return False
        print()
        
        # Autenticazione
        print("3️⃣ Autenticando con Google...")
        try:
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            print("✅ Autenticazione OK")
        except Exception as e:
            print(f"❌ Errore autenticazione: {e}")
            return False
        print()
        
        # Connessione Google Sheets
        print("4️⃣ Connettendosi a Google Sheets...")
        try:
            client = gspread.authorize(creds)
            sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
            print("✅ Connessione Google Sheets OK")
        except Exception as e:
            print(f"❌ Errore connessione: {e}")
            return False
        print()
        
        # Lettura dati
        print("5️⃣ Leggendo dati dal foglio...")
        try:
            all_rows = sheet.get_all_values()
            print(f"✅ Foglio letto ({len(all_rows)} righe)")
        except Exception as e:
            print(f"❌ Errore lettura: {e}")
            return False
        print()
        
        # Scrittura dati
        print("6️⃣ Scrivendo dati nel foglio...")
        try:
            for idx, row in enumerate(all_rows[1:], start=2):
                if len(row) > 1 and row[1]:
                    sheet.update_cell(idx, 3, "✅ TEST")
                    print(f"   ✅ Riga {idx}: {row[1]}")
            print("✅ Dati scritti")
        except Exception as e:
            print(f"❌ Errore scrittura: {e}")
            return False
        print()
        
        print("✅ BOT COMPLETATO CON SUCCESSO!")
        return True
    
    except Exception as e:
        print()
        print("❌ ERRORE GENERICO:")
        print(f"   {e}")
        print()
        print("TRACEBACK:")
        trac
