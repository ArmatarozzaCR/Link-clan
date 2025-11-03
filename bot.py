#!/usr/bin/env python3
"""
Clash Royale War Analysis Bot
Raccoglie i dati delle ultime 4 battaglie di guerra di ogni giocatore
e li scrive nel Google Sheet
"""

import gspread
from google.oauth2.service_account import Credentials
import requests
import json
import os
from datetime import datetime
import traceback

# Configuration
ROYALE_API_KEY = os.getenv('ROYALE_API_KEY')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')

API_BASE_URL = "https://api.clashroyale.com/v1"

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
        print(f"❌ Errore connessione Google Sheets: {e}")
        return None

def get_war_results(player_tag):
    """Ottiene i risultati della guerra da RoyaleAPI"""
    try:
        if not player_tag or player_tag == "":
            return None
        
        # Formatta il tag
        tag = player_tag.replace('#', '').upper()
        
        headers = {
    'User-Agent': 'Armata-Rozza-Bot'
}
        
        # Ottieni il battlelog
        url = f"{API_BASE_URL}/players/%23{tag}/battlelog"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            battles = response.json()
            return battles
        else:
            print(f"   ⚠️  API Error per {player_tag}: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"   ⚠️  Errore RoyaleAPI: {e}")
        return None

def analyze_results(battles):
    """
    Analizza i risultati della guerra
    Ritorna: 
    - "Win" se ha vinto almeno 1 battaglia
    - "Sì" se ha perso tutto
    - "No" se non ha giocato
    """
    if not battles:
        return 'No'  # Non ha giocato
    
    # Filtra solo le battaglie di guerra
    war_battles = [b for b in battles if 'riverRaceWar' in b.get('type', '')][:4]
    
    if not war_battles:
        return 'No'  # Nessuna battaglia di guerra trovata
    
    # Conta le sconfitte
    losses = sum(1 for b in war_battles if not b.get('won', False))
    
    if losses == len(war_battles):
        return 'Sì'  # Perso tutto
    else:
        return 'Win'  # Vinto almeno 1

def get_column_index(header_row, column_name):
    """Trova l'indice della colonna dal nome"""
    try:
        return header_row.index(column_name) + 1
    except ValueError:
        return None

def main():
    print("=" * 70)
    print("🤖 BOT CLASH ROYALE WAR ANALYSIS")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    try:
        # 1. Connessione
        print("1️⃣ Connettendosi a Google Sheets...")
        sheet = get_google_sheet()
        if not sheet:
            print("❌ Impossibile connettersi a Google Sheets")
            return False
        print("✅ Connessione OK")
        print()
        
        # 2. Lettura dati
        print("2️⃣ Leggendo dati dal foglio...")
        all_rows = sheet.get_all_values()
        
        if len(all_rows) < 2:
            print("❌ Foglio vuoto o non inizializzato")
            return False
        
        headers = all_rows[0]
        players = all_rows[1:]
        
        print(f"✅ Trovati {len(players)} giocatori")
        print()
        
        # 3. Raccogli dati
        print("3️⃣ Raccogliendo dati dalla guerra...")
        print()
        
        updated_count = 0
        
        for row_idx, player_row in enumerate(players, start=2):
            if len(player_row) < 2 or not player_row[1]:
                continue
            
            player_name = player_row[1]
            player_tag = player_row[0] if len(player_row) > 0 else None
            
            if not player_tag or player_tag == "":
                continue
            
            print(f"   🎮 {player_name} ({player_tag})...", end=" ", flush=True)
            
            # Ottieni i risultati
            battles = get_war_results(player_tag)
            result = analyze_results(battles)
            
            # Scrivi nella colonna "Lunedì" (colonna C = indice 3)
            # Puoi cambiare il numero della colonna se serve
            try:
                sheet.update_cell(row_idx, 3, result)
                print(f"✅ {result}")
                updated_count += 1
            except Exception as e:
                print(f"❌ Errore: {e}")
        
        print()
        print(f"✅ Aggiornati {updated_count} giocatori!")
        print()
        print("=" * 70)
        print("✅ BOT COMPLETATO CON SUCCESSO!")
        print("=" * 70)
        return True
    
    except Exception as e:
        print()
        print("❌ ERRORE GENERICO:")
        print(f"   {e}")
        print()
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
