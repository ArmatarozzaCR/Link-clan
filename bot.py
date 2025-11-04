#!/usr/bin/env python3
"""
Clash Royale War Analysis Bot - FINAL VERSION
Legge i dati del War Race del clan da RoyaleAPI
"""

import gspread
from google.oauth2.service_account import Credentials
import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime
import re

GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')
CLAN_TAGS = os.getenv('CLAN_TAGS', 'QC8LRJRP')

def get_google_sheet():
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
    """Legge i dati del War Race dal clan"""
    try:
        tag = clan_tag.replace('#', '').upper()
        url = f"https://royaleapi.com/clan/{tag}/war/race"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"      ❌ HTTP {response.status_code}")
            return {}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        war_data = {}
        
        # METODO 1: Trova tutte le righe con dati di guerra
        # Cerca i <tr> che contengono le info dei giocatori
        rows = soup.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            
            if len(cells) >= 4:
                try:
                    # Estrai il nome (seconda colonna)
                    name_cell = cells[1].get_text(strip=True)
                    wins_cell = cells[2].get_text(strip=True)
                    losses_cell = cells[3].get_text(strip=True)
                    
                    # Rimuovi prefissi (numeri di ranking)
                    name = re.sub(r'^\d+\s*', '', name_cell).strip()
                    
                    # Estrai i numeri
                    wins_match = re.search(r'\d+', wins_cell)
                    losses_match = re.search(r'\d+', losses_cell)
                    
                    if name and name not in ['Participants:', ''] and wins_match and losses_match:
                        wins = int(wins_match.group())
                        losses = int(losses_match.group())
                        war_data[name] = (wins, losses)
                
                except:
                    pass
        
        return war_data
    
    except Exception as e:
        print(f"      ⚠️  Error: {str(e)[:30]}")
        return {}

def main():
    print("=" * 70)
    print("🤖 BOT CLASH ROYALE WAR - FINAL")
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
            print(f"   📍 {clan_tag}...")
            war_data = get_clan_war_data(clan_tag)
            
            if war_data:
                print(f"      ✅ {len(war_data)} giocatori")
                for name, (wins, losses) in list(war_data.items())[:3]:
                    print(f"         • {name}: {wins}W/{losses}L")
                if len(war_data) > 3:
                    print(f"         ... e altri {len(war_data) - 3}")
                all_war_data.update(war_data)
            else:
                print(f"      ⚠️  Nessun dato")
            
            time.sleep(1)
        
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
                elif losses >= total or wins == 0:
                    result = 'Sì'
                else:
                    result = 'Win'
                
                print(f"   ✅ {name}: {result}")
                
                try:
                    sheet.update_cell(row_idx, 3, result)
                    updated += 1
                except:
                    pass
        
        print()
        print(f"✅ Aggiornati: {updated}")
        print("=" * 70)
        print("✅ BOT COMPLETATO!")
        print("=" * 70)
        return True
    
    except Exception as e:
        print(f"❌ {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
