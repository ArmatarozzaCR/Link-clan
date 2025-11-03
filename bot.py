#!/usr/bin/env python3
"""
Clash Royale War Analysis Bot - Scraping RoyaleAPI
Raccoglie i dati delle ultime 4 battaglie di guerra di ogni giocatore
dal sito RoyaleAPI.com usando web scraping (no API key needed!)
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

# Configuration
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
        print(f"❌ Errore connessione Google Sheets: {e}")
        return None

def get_war_results_scraping(player_tag):
    """
    Scraping da royaleapi.com per ottenere i risultati della guerra
    Legge il battlelog senza necessità di API Key
    """
    try:
        if not player_tag or player_tag == "":
            return 'No'
        
        # Formatta il tag
        tag = player_tag.replace('#', '').upper()
        
        # URL del profilo su RoyaleAPI
        url = f"https://royaleapi.com/player/{tag}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"🔍 Scraping {url}...", end=" ", flush=True)
        
        # Fai il request
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Cerca la sezione del battlelog nella pagina
            # RoyaleAPI mostra i battler nella struttura HTML
            
            # Cerca tutti gli elementi che contengono "Battle", "Win", "Loss"
            battles = soup.find_all('div', class_=['battle-log-item', 'battle', 'recent-battle'])
            
            if not battles:
                # Prova un approccio alternativo: cerca nel testo
                page_text = soup.get_text().lower()
                
                if 'battle' not in page_text and 'war' not in page_text:
                    print("⚠️  Nessun dato")
                    return 'No'
            
            # Conta wins e losses nei dati scritti
            wins = 0
            losses = 0
            
            # Analizza le righe della pagina
            for line in soup.find_all('tr'):
                text = line.get_text().lower()
                
                # Cerca negli ultimi 4 scontri
                if 'win' in text or 'victory' in text:
                    wins += 1
                elif 'loss' in text or 'defeat' in text:
                    losses += 1
                
                if wins + losses >= 4:
                    break
            
            # Se non ha trovato battaglie, torna 'No'
            if wins + losses == 0:
                print("⚠️  0 battaglie")
                return 'No'
            
            # Logica risultato
            if losses >= 4 or (wins == 0 and losses > 0):
                print(f"Sì (0 win, {losses} loss)")
                return 'Sì'
            else:
                print(f"Win ({wins} win, {losses} loss)")
                return 'Win'
        
        elif response.status_code == 404:
            print("❌ Tag non trovato")
            return 'No'
        else:
            print(f"⚠️  HTTP {response.status_code}")
            return 'No'
    
    except requests.exceptions.Timeout:
        print("⏱️  Timeout")
        return 'No'
    except requests.exceptions.ConnectionError:
        print("🚫 Connessione fallita")
        return 'No'
    except Exception as e:
        print(f"⚠️  {str(e)[:30]}")
        return 'No'

def main():
    print("=" * 70)
    print("🤖 BOT CLASH ROYALE WAR ANALYSIS - ROYALEAPI SCRAPING")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    try:
        # 1. Connessione
        print("1️⃣ Connettendosi a Google Sheets...")
        sheet = get_google_sheet()
        if not sheet:
            print("❌ Impossibile connettersi a Google Sheets")
            return False
        print("✅ Connessione OK")
        print()
        
        # 2. Lettura dati
        print("2️⃣ Leggendo dati dal foglio...")
        all_rows = sheet.get_all_values()
        
        if len(all_rows) < 2:
            print("❌ Foglio vuoto")
            return False
        
        players = all_rows[1:]
        
        print(f"✅ Trovati {len(players)} giocatori")
        print()
        
        # 3. Raccogli dati
        print("3️⃣ Raccogliendo dati da RoyaleAPI...")
        print()
        
        updated_count = 0
        
        for row_idx, player_row in enumerate(players, start=2):
            if len(player_row) < 2 or not player_row[1]:
                continue
            
            player_name = player_row[1]
            player_tag = player_row[0] if len(player_row) > 0 else None
            
            if not player_tag or player_tag == "":
                continue
            
            print(f"   🎮 {player_name} ({player_tag})... ", end="", flush=True)
            
            # Ottieni i risultati tramite scraping
            result = get_war_results_scraping(player_tag)
            
            # Scrivi nella colonna "Lunedì" (colonna 3)
            try:
                sheet.update_cell(row_idx, 3, result)
                updated_count += 1
            except Exception as e:
                print(f"❌ Errore scrittura: {e}")
            
            # Aspetta un po' tra le richieste
            time.sleep(2)
        
        print()
        print(f"✅ Aggiornati {updated_count} giocatori!")
        print()
        print("=" * 70)
        print("✅ BOT COMPLETATO CON SUCCESSO!")
        print("=" * 70)
        return True
    
    except Exception as e:
        print()
        print(f"❌ ERRORE: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
