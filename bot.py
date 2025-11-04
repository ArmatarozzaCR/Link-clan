#!/usr/bin/env python3
"""
Clash Royale War Analysis Bot - RESTORING WORKING VERSION
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
        return client.open_by_key(GOOGLE_SHEET_ID).sheet1
    except Exception as e:
        print(f"❌ {e}")
        return None

def install_playwright():
    """Installa Playwright browsers"""
    try:
        subprocess.run(['python', '-m', 'playwright', 'install', 'chromium'], 
                      check=True, capture_output=True, timeout=60)
    except:
        pass

def get_clan_war_data(clan_tag):
    """Scraping con Selenium - la vera soluzione che funzionava ieri"""
    driver = None
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        
        tag = clan_tag.replace('#', '').upper()
        url = f"https://royaleapi.com/clan/{tag}/war/race"
        
        print(f"      🌐 Browser...", end=" ", flush=True)
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Aspetta il caricamento completo
        time.sleep(5)
        
        # Prendi il testo della pagina
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        war_data = {}
        lines = page_text.split('\n')
        
        for line in lines:
            if any(role in line for role in ['Member', 'Leader', 'Co-leader']):
                numbers = re.findall(r'\d+', line)
                
                if len(numbers) >= 2:
                    try:
                        clean_line = line
                        for num in numbers:
                            clean_line = clean_line.replace(num, ' ', 1)
                        for role in ['Member', 'Leader', 'Co-leader']:
                            clean_line = clean_line.replace(role, ' ')
                        
                        name = ' '.join(clean_line.split()).strip()
                        
                        if name and len(name) > 2:
                            wins = int(numbers[0])
                            losses = int(numbers[1])
                            war_data[name] = (wins, losses)
                    except:
                        pass
        
        if war_data:
            print(f"✅ {len(war_data)}")
        else:
            print(f"❌")
        
        return war_data
    
    except Exception as e:
        print(f"⚠️  {str(e)[:30]}")
        return {}
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    print("=" * 70)
    print("🤖 BOT CLASH ROYALE WAR - WORKING VERSION")
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
        print(f"3️⃣ War Race ({len(clan_tags)} clan)...")
        print()
        
        all_war_data = {}
        for clan_tag in clan_tags:
            print(f"   📍 {clan_tag}... ", end="", flush=True)
            war_data = get_clan_war_data(clan_tag)
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
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exit(0 if main() else 1)
