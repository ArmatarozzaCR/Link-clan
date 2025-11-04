#!/usr/bin/env python3
"""
Clash Royale War Analysis Bot - RIVER RACE FILTER
Clicca sul dropdown Battle Types e seleziona River Race
"""

import gspread
from google.oauth2.service_account import Credentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    Clicca sul dropdown Battle Types
    Seleziona River Race
    Legge le vittorie e sconfitte
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
        
        time.sleep(4)
        
        print(f"🔍", end=" ", flush=True)
        
        try:
            # Trova il dropdown "Battle Types"
            # Cerca il pulsante select/dropdown
            dropdown = driver.find_element(By.XPATH, "//select | //button[contains(text(), 'Battle')] | //*[contains(text(), 'Battle Types')]")
            
            # Se è un select, usa select_by_value
            from selenium.webdriver.support.select import Select
            
            try:
                select = Select(dropdown)
                # Cerca un'opzione che contiene "River Race"
                options = select.options
                
                for option in options:
                    if 'River Race' in option.text:
                        select.select_by_value(option.get_attribute('value'))
                        time.sleep(2)
                        break
            except:
                # Se non è un select, clicca sul pulsante
                dropdown.click()
                time.sleep(2)
        except:
            pass
        
        # Leggi il testo della pagina DOPO il filtro
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        print(f"📊", end=" ", flush=True)
        
        # Conta Victory e Defeat nel testo
        victory_count = page_text.lower().count('victory') + page_text.lower().count('won') + page_text.lower().count('1 - 0')
        defeat_count = page_text.lower().count('defeat') + page_text.lower().count('lost') + page_text.lower().count('0 - 1') + page_text.lower().count('0 - 3')
        
        # Approssima: se ci sono "River Race 1v1: 10" significa 10 battaglie
        # Estrai il numero dal testo
        import re
        
        war_wins = 0
        war_losses = 0
        
        # Cerca pattern come "River Race 1v1: X" o "River Race Duel: X"
        patterns = [
            r'River Race 1v1.*?:\s*(\d+)',
            r'River Race Duel.*?:\s*(\d+)',
            r'River Race.*?:\s*(\d+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                # Prendi il primo match
                total = int(matches[0])
                
                # Conta vittorie e sconfitte nel testo della pagina
                snippet = page_text.lower()
                
                # Conta "Victory" e "Defeat" nelle righe di battaglia
                victories = snippet.count('victory')
                defeats = snippet.count('defeat')
                
                war_wins = max(0, victories)
                war_losses = max(0, defeats)
                
                break
        
        # Se non ha trovato niente, prova un approccio diverso
        if war_wins + war_losses == 0:
            # Conta solo le occorrenze nel testo
            war_wins = page_text.count('Victory')
            war_losses = page_text.count('Defeat')
        
        total = war_wins + war_losses
        
        print(f"W:{war_wins} L:{war_losses}", end=" ", flush=True)
        
        if total == 0:
            print(f"❌")
            return 'No'
        elif war_losses >= total or war_wins == 0:
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
    print("🤖 BOT CLASH ROYALE WAR - RIVER RACE DETECTION")
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
        
        print("2️⃣ Giocatori...")
        all_rows = sheet.get_all_values()
        
        if len(all_rows) < 2:
            print("❌ Vuoto")
            return False
        
        players = all_rows[1:]
        print(f"✅ {len(players)}")
        print()
        
        print("3️⃣ River Race Analysis...")
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
        print("✅ COMPLETATO!")
        print("=" * 70)
        return True
    
    except Exception as e:
        print(f"❌ {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
