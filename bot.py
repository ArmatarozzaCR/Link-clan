#!/usr/bin/env python3
"""
Clash Royale War Analysis Bot - RIVER RACE BATTLES DETECTION
Legge le River Race Duel, 1v1, e Colosseum battles
"""

import gspread
from google.oauth2.service_account import Credentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import os
import time
from datetime import datetime
import traceback

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

def get_war_battles(player_tag):
    """
    Legge le River Race battles (Duel, 1v1, Colosseum)
    """
    driver = None
    try:
        if not player_tag or player_tag == "":
            return 'No'
        
        tag = player_tag.replace('#', '').upper()
        
        # Configura Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('user-agent=Mozilla/5.0')
        
        print(f"🌐", end=" ", flush=True)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"https://royaleapi.com/player/{tag}/battles")
        
        time.sleep(5)
        
        # Leggi il testo completo della pagina
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        print(f"📄", end=" ", flush=True)
        
        # Tipi di River Race battles che cerchiamo
        war_types = [
            'River Race Duel',
            'River Race 1v1',
            'River Race Duel Colosseum',
            'river race duel',
            'river race 1v1',
            'river race duel colosseum'
        ]
        
        # Conta le war battles
        war_wins = 0
        war_losses = 0
        
        # Dividi il testo per ogni tipo di war
        for war_type in war_types:
            if war_type in page_text:
                # Trova tutte le occorrenze di questo tipo di battaglia
                sections = page_text.split(war_type)
                
                # Per ogni occorrenza (tranne la prima che è testo prima)
                for section in sections[1:]:
                    # Guarda i prossimi 300 caratteri
                    snippet = section[:300].lower()
                    
                    # Cerca il risultato (Victory o Defeat)
                    if 'victory' in snippet or 'won' in snippet or '1 - 0' in snippet:
                        war_wins += 1
                    elif 'defeat' in snippet or 'lost' in snippet or '0 - 1' in snippet or '0 - 3' in snippet:
                        war_losses += 1
        
        total_wars = war_wins + war_losses
        
        print(f"W:{war_wins} L:{war_losses}", end=" ", flush=True)
        
        # Logica risultato
        if total_wars == 0:
            print(f"❌")
            return 'No'
        elif war_losses >= total_wars or war_wins == 0:
            print(f"✅ Sì")
            return 'Sì'
        else:
            print(f"✅ Win")
            return 'Win'
    
    except Exception as e:
        print(f"⚠️  {str(e)[:20]}")
        return 'No'
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    print("=" * 70)
    print("🤖 BOT CLASH ROYALE WAR - RIVER RACE BATTLES")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    try:
        print("1️⃣ Google Sheets...")
        sheet = get_google_sheet()
        if not sheet:
            return False
        print("✅")
        print()
        
        print("2️⃣ Lettura giocatori...")
        all_rows = sheet.get_all_values()
        
        if len(all_rows) < 2:
            print("❌ Foglio vuoto")
            return False
        
        players = all_rows[1:]
        print(f"✅ {len(players)} giocatori")
        print()
        
        print("3️⃣ Analisi River Race battles...")
        print()
        
        updated = 0
        
        for row_idx, player_row in enumerate(players, start=2):
            if len(player_row) < 2 or not player_row[1]:
                continue
            
            name = player_row[1]
            tag = player_row[0] if len(player_row) > 0 else None
            
            if not tag or tag == "":
                continue
            
            print(f"   🎮 {name} ({tag})... ", end="", flush=True)
            
            result = get_war_battles(tag)
            
            try:
                sheet.update_cell(row_idx, 3, result)
                updated += 1
            except:
                pass
            
            time.sleep(2)
        
        print()
        print()
        print(f"✅ Aggiornati: {updated}")
        print("=" * 70)
        print("✅ DONE!")
        print("=" * 70)
        return True
    
    except Exception as e:
        print(f"❌ {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
