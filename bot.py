from datetime import datetime
import os

def main():
    print("=" * 60)
    print("🤖 BOT CLASH ROYALE WAR ANALYSIS")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    royale_key = os.getenv('ROYALE_API_KEY')
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    
    print("✅ SISTEMA ONLINE!")
    print()
    print(f"📊 Sheet ID: {sheet_id}")
    print(f"🔑 API Key: {'✅ Configurata' if royale_key else '❌ Mancante'}")
    print()
    print("⏰ Il bot raccoglierà i dati:")
    print("   - Ogni giorno alle 10:00 AM")
    print("   - Dal Google Sheet configurato")
    print("   - Dalla API di Clash Royale")
    print()
    print("✅ PRONTO PER DOMANI!")

if __name__ == "__main__":
    main()
