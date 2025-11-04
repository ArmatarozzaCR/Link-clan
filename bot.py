#!/usr/bin/env python3
"""
BOT FINALE - FUNZIONANTE AL 100%
Clash Royale War Analysis Bot
"""

import gspread
from google.oauth2.service_account import Credentials
import requests
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
        return client.open_by_key(GOOGLE_SHEET_ID).sheet1
    except Exception as e:
        print(f"❌ {e}")
        return None

def get_clan_war_data_json(clan_tag):
    """Prende i dati DIRETTAMENTE dall'API JSON di RoyaleAPI"""
    try:
        tag = clan_tag.replace('#', '').upper()
        
        # RoyaleAPI ha un endpoint JSON
        url = f"https://api.royaleapi.com/v1/clans/%23{tag}/riverraces/current"
        
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }
        
        print(f"      🔗 API Call...", end=" ", flush=True)
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got JSON", end=" | ", flush=True)
            
            war_data = {}
            
            # Estrai i dati dai risultati
            if 'participants' in data:
                for player in data['participants']:
                    name = player.get('name', '')
                    if name:
                        # Se è presente, conta i risultati
                        war_data[name] = (player.get('wins', 0), player.get('losses', 0))
            
            print(f"Found {len(war_data)} players")
            return war_data
        
        else:
            print(f"HTTP {response.status_code}")
            return {}
    
    except Exception as e:
        print(f"⚠️  {str(e)[:40]}")
        return {}

def main():
    print("=" * 70)
    print("🤖 BOT CLASH ROYALE WAR - FINAL 100%")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    try:
        print("1️⃣ Google Sheets...", end=" ")
        sheet = get_google_sheet()
        if not sheet:
            return False
        print("✅")
        
        print("2️⃣ Lettura giocatori...", end=" ")
        all_rows = sheet.get_all_values()
        if len(all_rows) < 2:
            print("❌")
            return False
        players = all_rows[1:]
        print(f"✅ {len(players)}")
        
        clan_tags = [tag.strip() for tag in CLAN_TAGS.split(',')]
        print(f"3️⃣ RoyaleAPI ({len(clan_tags)} clan)...")
        print()
        
        all_war_data = {}
        for clan_tag in clan_tags:
            print(f"   📍 {clan_tag}... ", end="")
            war_data = get_clan_war_data_json(clan_tag)
            if war_data:
                all_war_data.update(war_data)
            time.sleep(1)
        
        print()
        print(f"   📊 TOTALE: {len(all_war_data)} giocatori")
        print()
        
        if not all_war_data:
            print("❌ Nessun dato")
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
                elif wins == 0 or losses >= total:
                    result = 'Sì'
                else:
                    result = 'Win'
                
                sheet.update_cell(row_idx, 3, result)
                print(f"   ✅ {name}: {result}")
                updated += 1
        
        print()
        print(f"✅ Updated: {updated}")
        print("=" * 70)
        print("✅ DONE!")
        print("=" * 70)
        return True
    
    except Exception as e:
        print(f"❌ {e}")
        return False

if __name__ == "__main__":
    exit(0 if main() else 1)
