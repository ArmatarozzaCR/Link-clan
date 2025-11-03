#!/usr/bin/env python3
"""
Clash Royale War Analysis Bot - WAR EMBLEM DETECTION
Cerco le battaglie con gli STEMMI specifici delle war
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
        print(f"❌ Errore Google Sheets: {e}")
        return None

def get_war_battles(player_tag):
    """
    Legge le battaglie con gli STEMMI specifici delle war
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
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0')
        
        print(f"🌐 Checking battles...", end=" ", flush=True)
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Vai alla pagina battles
        url = f"https://royaleapi.com/player/{tag}/battles"
        driver.get(url)
        
        # Aspetta il caricamento
        time.sleep(4)
        
        # Leggi il codice HTML per trovare le immagini degli stemmi
        page_html = driver.page_source
        
        # Cerca gli STEMMI delle war nel codice HTML
        # RoyaleAPI usa tag <img> con src che contengono l'id dello stemma
        
        # Conta le battaglie con stemmi di guerra
        war_wins = 0
        war_losses = 0
        
        # Trova tutti i container delle battaglie
        battles = driver.find_elements(By.XPATH, "//tr")
        
        for battle in battles:
            try:
                # Cerca l'immagine dello stemma nella riga
                # Gli stemmi delle war hanno classi/id specifiche
                
                # Prova a trovare img con attributi che indicano war
                imgs = battle.find_elements(By.TAG_NAME, "img")
                
                is_war_battle = False
                
                for img in imgs:
                    src = img.get_attribute('src') or ""
                    alt = img.get_attribute('alt') or ""
                    class_name = img.get_attribute('class') or ""
                    
                    # Cerca indicatori di war battle:
                    # - src contiene 'war', 'clan-war', 'river-race'
                    # - alt contiene war-related keywords
                    
                    if any(keyword in src.lower() for keyword in ['war', 'clan-war', 'river', 'boat']):
                        is_war_battle = True
                        break
                    if any(keyword in alt.lower() for keyword in ['war', 'clan', 'river', 'boat']):
                        is_war_battle = True
                        break
                
                if is_war_battle:
                    # Leggi se è Victory o Defeat
                    battle_text = battle.text.lower()
                    
                    if 'victory' in battle_text or '1 - 0' in battle_text:
                        war_wins += 1
                    elif 'defeat' in battle_text or '0 - 1' in battle_text:
                        war_losses += 1
            
            except:
                pass
        
        # Fallback: cerca nel codice HTML raw
        if war_wins + war_losses == 0:
            # Conta nel HTML direttamente
            # Cerca elementi che indicano war battles
            
            if 'river-race' in page_html.lower() or 'clan-war' in page_html.lower():
                # Estrai le vittorie e sconfitte
                victory_count = page_html.lower().count('victory')
                defeat_count = page_html.lower().count('defeat')
                
                war_wins = max(0, victory_count // 4)  # Approssima
                war_losses = max(0, defeat_count // 4)
        
        # Risultato finale
        total_wars = war_wins + war_losses
        
        if total_wars == 0:
            print("⚠️  0 war")
            return 'No'
        elif war_losses >= total_wars or war_wins == 0:
            print(f"Sì (0/{total_wars})")
            return 'Sì'
        else:
            print(f"Win ({war_wins}/{total_wars})")
            return 'Win'
    
    except Exception as e:
        print(f"⚠️  {str(e)[:30]}")
        return 'No'
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    print("=" * 70)
    print("🤖 BOT CLASH ROYALE WAR ANALYSIS - WAR EMBLEM DETECTION")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    try:
        # 1. Connessione
        print("1️⃣ Connessione Google Sheets...")
        sheet = get_google_sheet()
        if not sheet:
            print("❌ Errore connessione")
            return False
        print("✅ OK")
        print()
        
        # 2. Lettura giocatori
        print("2️⃣ Lettura giocatori...")
        all_rows = sheet.get_all_values()
        
        if len(all_rows) < 2:
            print("❌ Foglio vuoto")
            return False
        
        players = all_rows[1:]
        print(f"✅ {len(players)} giocatori trovati")
        print()
        
        # 3. Analisi
        print("3️⃣ Analisi battaglie war...")
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
            except Exception as e:
                print(f"❌ Write error")
            
            time.sleep(3)
        
        print()
        print(f"✅ {updated} aggiornati!")
        print("=" * 70)
        print("✅ BOT COMPLETATO!")
        print("=" * 70)
        return True
    
    except Exception as e:
        print(f"❌ {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
