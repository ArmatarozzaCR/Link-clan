#!/usr/bin/env python3
"""
Clash Royale War Analysis Bot - MULTIPLE CLANS (FIXED PARSING)
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
import re

GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')
CLAN_TAGS = os.getenv('CLAN_TAGS', 'QC8LRJRP')

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

def get_clan_war_data(clan_tag):
    """
    Legge i dati del War Race di UN clan
    """
    driver = None
    try:
        tag = clan_tag.replace('#', '').upper()
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('user-agent=Mozilla/5.0')
        
        driver = webdriver.Chrome(options=chrome_options)
        url = f"https://royaleapi.com/clan/{tag}/war/race"
        driver.get(url)
        
        time.sleep(5)
        
        # Leggi il testo completo
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        war_data = {}
        
        # METODO 1: Parse dal testo raw (più robusto)
        lines = page_text.split('\n')
        
        for i, line in enumerate(lines):
            # Cerca linee con "Member", "Leader", "Co-leader"
            if any(role in line for role in ['Member', 'Leader', 'Co-leader']):
                # La linea ha il formato: NAME ROLE WINS LOSSES ...
                
                # Prova a estrarre i numeri
                numbers = re.findall(r'\d+', line)
                
                if len(numbers) >= 2:
                    try:
                        # Gli ultimi numeri sono tipicamente wins/losses
                        wins = int(numbers[-2]) if len(numbers) >= 2 else 0
                        losses = int(numbers[-1]) if len(numbers) >= 1 else 0
                        
                        # Estrai il nome (parte prima dei numeri)
                        # Rimuovi "Member", "Leader", "Co-leader"
                        clean_line = line
                        for role in ['Member', 'Leader', 'Co-leader']:
                            clean_line = clean_line.replace(role, '')
                        
                        # Rimuovi i numeri
                        for num in numbers:
                            clean_line = clean_line.replace(num, '')
                        
                        player_name = clean_line.strip()
                        
                        if player_name and len(player_name) > 2:
                            war_data[player_name] = (wins, losses)
                            print(f"         → {player_name}: {wins}W/{losses}L")
                    
                    except:
                        pass
        
        # METODO 2: Se il metodo 1 non ha trovato niente, prova con le celle HTML
        if not war_data:
            try:
                rows = driver.find_elements(By.XPATH, "//tr[td]")
                
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) >= 4:
                        try:
                            # cells[1] = nome, cells[2] = wins, cells[3] = losses
                            player_name = cells[1].text.strip()
                            wins_text = cells[2].text.strip()
                            losses_text = cells[3].text.strip()
                            
                            if player_name and player_name != "Participants:":
                                wins = int(wins_text) if wins_text.isdigit() else 0
                                losses = int(losses_text) if losses_text.isdigit() else 0
                                
                                war_data[player_name] = (wins, losses)
                                print(f"         → {player_name}: {wins}W/{losses}L")
                        
                        except:
                            pass
            except:
                pass
        
        return war_data
    
    except Exception as e:
        print(f"   ⚠️  Errore: {str(e)[:40]}")
        return {}
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    print("=" * 70)
    print("🤖 BOT CLASH ROYALE WAR - MULTIPLE CLANS")
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
        
        clan_tags = [tag.strip() for tag in CLAN_TAGS.split(',')]
        print(f"3️⃣ War Race ({len(clan_tags)} clan)...")
        print()
        
        all_war_data = {}
        
        for clan_tag in clan_tags:
            print(f"   📍 Clan {clan_tag}...")
            war_data = get_clan_war_data(clan_tag)
            
            if war_data:
                print(f"      ✅ {len(war_data)} giocatori")
                all_war_data.update(war_data)
            else:
                print(f"      ❌ Nessun dato")
        
        print()
        print(f"   📊 TOTALE: {len(all_war_data)} giocatori")
        print()
        
        if not all_war_data:
            print("❌ Nessun dato trovato")
            return False
        
        print("4️⃣ Aggiornamento...")
        print()
        
        updated = 0
        
        for row_idx, player_row in enumerate(players, start=2):
            if len(player_row) < 2 or not player_row[1]:
                continue
            
            name = player_row[1]
            
            if name in all_war_data:
                wins, losses = all_war_data[name]
                total = wins + losses
                
                if total == 0:
                    result = 'No'
                    status = "No"
                elif losses >= total or wins == 0:
                    result = 'Sì'
                    status = "Sì"
                else:
                    result = 'Win'
                    status = "Win"
                
                print(f"   🎮 {name}... {status} ({wins}W/{losses}L)")
                
                try:
                    sheet.update_cell(row_idx, 3, result)
                    updated += 1
                except:
                    pass
            else:
                print(f"   🎮 {name}... ❌ Not found")
        
        print()
        print(f"✅ Aggiornati: {updated}/{len(players)}")
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
