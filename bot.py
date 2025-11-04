#!/usr/bin/env python3
"""
Clash Royale War Analysis Bot - FINAL WORKING VERSION
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import os
import time
from datetime import datetime
import re
import subprocess
import sys

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
    """Scraping CON CURL - NO BROWSER NEEDED"""
    try:
        tag = clan_tag.replace('#', '').upper()
        url = f"https://royaleapi.com/clan/{tag}/war/race"
        
        print(f"      📡 Downloading...", end=" ", flush=True)
        
        # Usa curl per scaricare la pagina
        result = subprocess.run(
            ['curl', '-s', '-A', 'Mozilla/5.0', url],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0:
            print(f"❌")
            return {}
        
        html_content = result.stdout
        
        war_data = {}
        
        # Parse il contenuto HTML per trovare i dati
        # Cerca il pattern: "ＡＲ❤️Ｔｅｆａｎｏｓ Member 4 0 0 0"
        
        lines = html_content.split('\n')
        
        for line in lines:
            # Cerca linee con "Member", "Leader", "Co-leader"
            if any(role in line for role in ['Member', 'Leader', 'Co-leader']):
                # Estrai i numeri
                numbers = re.findall(r'\d+', line)
                
                if len(numbers) >= 2:
                    try:
                        # Pulisci la linea
                        clean_line = line
                        for num in numbers:
                            clean_line = clean_line.replace(num, ' ', 1)
                        for role in ['Member', 'Leader', 'Co-leader']:
                            clean_line = clean_line.replace(role, ' ')
                        
                        # Estrai il nome
                        name = ' '.join(clean_line.split()).strip()
                        
                        # Filtra nomi di sistema
                        if name and len(name) > 2 and name not in [
                            'Participants', 'Battle Types', 'All Battles', 
                            'Ladder', 'Ranked', 'Friendly', 'Boat Battle',
                            'River Race', 'War', 'Battles', '20 win'
                        ]:
                            # Prendi i primi 2 numeri
                            wins = int(numbers[0])
                            losses = int(numbers[1])
                            
                            war_data[name] = (wins, losses)
                    
                    except Exception as e:
                        pass
        
        if war_data:
            print(f"✅ {len(war_data)}")
        else:
            print(f"❌")
        
        return war_data
    
    except Exception as e:
        print(f"      ⚠️  {str(e)[:40]}")
        return {}

def main():
    print("=" * 70)
    print("🤖 BOT CLASH ROYALE WAR - FINAL WORKING")
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
            print(f"   📍 {clan_tag}")
            war_data = get_clan_war_data(clan_tag)
            
            if war_data:
                all_war_data.update(war_data)
            
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
                
                try:
                    sheet.update_cell(row_idx, 3, result)
                    print(f"   ✅ {name}: {result}")
                    updated += 1
                except:
                    print(f"   ⚠️  {name}")
            else:
                print(f"   ❌ {name}: Not found")
        
        print()
        print(f"✅ Aggiornati: {updated}")
        print("=" * 70)
        print("✅ COMPLETATO!")
        print("=" * 70)
        return True
    
    except Exception as e:
        print(f"❌ {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
