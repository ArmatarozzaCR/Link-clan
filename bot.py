#!/usr/bin/env python3
"""
Clash Royale War Analysis Bot - MULTIPLE CLANS WAR RACE ANALYSIS
Legge il War Race di MULTIPLI clan
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
CLAN_TAGS = os.getenv('CLAN_TAGS', 'QC8LRJRP')  # Separati da virgola

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
    Ritorna un dizionario con player_name -> (wins, losses)
    """
    driver = None
    try:
        tag = clan_tag.replace('#', '').upper()
        
        # Configura Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('user-agent=Mozilla/5.0')
        
        driver = webdriver.Chrome(options=chrome_options)
        url = f"https://royaleapi.com/clan/{tag}/war/race"
        driver.get(url)
        
        time.sleep(4)
        
        # Leggi il testo della pagina
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Dizionario per i risultati
        war_data = {}
        
        # Leggi le righe
        rows = driver.find_elements(By.TAG_NAME, "tr")
        
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 4:
                    player_name = cells[1].text.strip()
                    
                    if player_name and player_name != "Participants:":
                        try:
                            wins = int(cells[2].text.strip())
                            losses = int(cells[3].text.strip())
                            war_data[player_name] = (wins, losses)
                        except:
                            pass
            except:
                pass
        
        # Fallback: parsing dal testo
        if not war_data:
            lines = page_text.split('\n')
            
            for line in lines:
                if 'Member' in line or 'Leader' in line or 'Co-leader' in line:
                    parts = line.split()
                    
                    if len(parts) >= 4:
                        try:
                            for i in range(len(parts) - 4, -1, -1):
                                if parts[i].isdigit():
                                    wins = int(parts[i])
                                    losses = int(parts[i + 1]) if i + 1 < len(parts) else 0
                                    
                                    name_parts = []
                                    for j in range(i):
                                        if 'Member' not in parts[j] and 'Leader' not in parts[j] and 'Co-' not in parts[j]:
                                            name_parts.append(parts[j])
                                    
                                    player_name = ' '.join(name_parts).strip()
                                    
                                    if player_name:
                                        war_data[player_name] = (wins, losses)
                                    break
                        except:
                            pass
        
        return war_data
    
    except Exception as e:
        print(f"   ⚠️  Errore clan {tag}: {str(e)[:30]}")
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
        
        # Parsing dei clan tags
        clan_tags = [tag.strip() for tag in CLAN_TAGS.split(',')]
        print(f"3️⃣ Lettura War Race ({len(clan_tags)} clan)...")
        print()
        
        # Raccogli dati da TUTTI i clan
        all_war_data = {}
        
        for clan_tag in clan_tags:
            print(f"   📍 Clan {clan_tag}...")
            war_data = get_clan_war_data(clan_tag)
            
            if war_data:
                print(f"      ✅ {len(war_data)} giocatori trovati")
                # Merge dei dati
                all_war_data.update(war_data)
            else:
                print(f"      ❌ Nessun dato")
        
        print()
        print(f"   📊 TOTALE: {len(all_war_data)} giocatori in tutti i clan")
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
            
            # Cerca il giocatore nei dati di TUTTI i clan
            if name in all_war_data:
                wins, losses = all_war_data[name]
                total = wins + losses
                
                if total == 0:
                    result = 'No'
                    print_result = "No"
                elif losses >= total or wins == 0:
                    result = 'Sì'
                    print_result = f"Sì"
                else:
                    result = 'Win'
                    print_result = f"Win"
                
                print(f"   🎮 {name}... {print_result} ({wins}W/{losses}L)")
                
                try:
                    sheet.update_cell(row_idx, 3, result)
                    updated += 1
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"   🎮 {name}... ❌ Not in any clan")
        
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
