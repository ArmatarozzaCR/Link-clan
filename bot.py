#!/usr/bin/env python3
print("🤖 BOT STARTED")
print("================")

import sys
print(f"Python: {sys.version}")

try:
    import gspread
    print("✅ gspread imported")
except Exception as e:
    print(f"❌ gspread error: {e}")
    sys.exit(1)

try:
    from google.oauth2.service_account import Credentials
    print("✅ google.oauth2 imported")
except Exception as e:
    print(f"❌ google.oauth2 error: {e}")
    sys.exit(1)

import json
import os
from datetime import datetime

print()
print("=" * 60)
print("🤖 BOT CLASH ROYALE WAR ANALYSIS")
print(f"⏰ {datetime.now()}")
print("=" * 60)
print()

GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')

print(f"✅ GOOGLE_SHEET_ID: {GOOGLE_SHEET_ID}")
print(f"✅ GOOGLE_CREDENTIALS: {'Set' if GOOGLE_CREDENTIALS else 'Not set'}")
print()

try:
    print("Parsing JSON...")
    creds_dict = json.loads(GOOGLE_CREDENTIALS)
    print("✅ JSON parsed OK")
    print()
    
    print("Authenticating with Google...")
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    print("✅ Auth OK")
    print()
    
    print("Connecting to Google Sheets...")
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
    print("✅ Connected!")
    print()
    
    print("Reading sheet...")
    all_rows = sheet.get_all_values()
    print(f"✅ Sheet read ({len(all_rows)} rows)")
    print()
    
    if len(all_rows) > 1:
        print(f"Found {len(all_rows) - 1} players")
        print()
        
        print("Writing test data...")
        count = 0
        for idx, row in enumerate(all_rows[1:], start=2):
            if len(row) > 1 and row[1]:
                try:
                    sheet.update_cell(idx, 3, "✅ TEST")
                    print(f"  ✅ Row {idx}: {row[1]}")
                    count += 1
                except Exception as e:
                    print(f"  ❌ Error row {idx}: {e}")
        
        print()
        print(f"✅ Written {count} cells!")
    
    print()
    print("✅ BOT COMPLETED SUCCESSFULLY!")
    
except Exception as e:
    import traceback
    print()
    print(f"❌ ERROR: {e}")
    print()
    traceback.print_exc()
    sys.exit(1)
