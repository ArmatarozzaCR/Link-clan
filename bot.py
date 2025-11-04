#!/usr/bin/env python3
"""
Clash Royale War Analysis Bot - REQUESTS (NO SELENIUM)
Usa requests per prendere i dati direttamente dall'HTML
"""

import gspread
from google.oauth2.service_account import Credentials
import requests
from bs4 import BeautifulSoup
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
    Usa requests + BeautifulSoup per scaricare la pagina
    """
    try:
        tag = clan_tag.replace('#', '').upper()
        
        url = f"https://royaleapi.com/clan/{tag}/war/race"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"      ❌ HTTP {response.status_code}")
            return {}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        war_data = {}
        
        # Cerca tutte le righe della tabella
        rows = soup.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            
            if len(cells) >= 4:
                try:
                    # cells[1] = nome player
                    # cells[2] = wins (primo numero)
                    # cells[3] = losses (secondo numero)
                    
                    player_name = cells[1].get_text().strip()
                    wins_text = cells[2].get_text().strip()
                    losses_text = cells[3].get_text().strip()
                    
                    if player_name and player_name != "Participants:":
                        # Estrai solo i numeri
                        wins = int(re.search(r'\d+', wins_text).group()) if re.search(r'\d+', wins_text) else 0
                        losses = int(re.search(r'\d+', losses_text).group()) if re.search(r'\d+', losses_text) else 0
                        
                        war_data[player_name] = (wins, losses)
                        print(f"         → {player_name}: {wins}W/{losses}L")
                
                except Exception as e:
                    pass
        
        # Fallback: parse dal testo raw
        if not war_data:
            text = soup.get_text()
            lines = text.split('\n')
            
            for line in lines:
                if any(role in line for role in ['Member', 'Leader', 'Co-leader']):
                    numbers = re.findall(r'\d+', line)
                    
                    if len(numbers) >= 2:
                        try:
                            wins = int(numbers[-4]) if len(numbers) >= 4 else 0
                            losses = int(numbers[-3]) if len(numbers) >= 3 else 0
                            
                            clean_line = line
                            for role in ['Member', 'Leader', 'Co-leader']:
                                clean_line = clean_line.replace(role, '')
                            
                            for num in numbers:
                                clean_line = clean_line.replace(num, '')
                            
                            player_name = clean_line.strip()
                            
                            if player_name and len(player_name) > 2:
                                war_data[player_name] = (wins, losses)
                                print(f"         → {player_name}: {wins}W/{losses}L")
                        
                        except:
                            pass
        
        return war_data
    
    except Exception as e:
        print(f"      ⚠️  {str(e)[:40]}")
        return {}

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
            
            time.sleep(1)
        
        print()
        print(f"   📊 TOTALE: {len(all_war_data)} giocatori")
        print()
        
        if not all_war_data:
            print("❌ Nessun dato trovato")
            print()
            print("   💡 DEBUG: Forse RoyaleAPI ha cambiato struttura")
            print("   💡 Prova a verificare manualmente:")
            print(f"   💡 <https://royaleapi.com/clan/{clan_tags>[0]}/war/race")
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
