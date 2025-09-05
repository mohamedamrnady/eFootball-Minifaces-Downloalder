#!/usr/bin/env python3
"""Quick verification that the modules work"""

print("Testing modules...")

try:
    print("✅ Importing modules...")
    from teams import league_info_scrapper, teams_urls_scrapper
    from players_in_team import players_in_team
    from get_miniface import miniface_downloader
    import config

    print("✅ All imports successful!")

    print(f"✅ Configuration loaded:")
    print(f"   - Teams workers: {config.MAX_WORKERS_TEAMS}")
    print(f"   - Players workers: {config.MAX_WORKERS_PLAYERS}")
    print(f"   - Request delay: {config.REQUEST_DELAY}s")

    print("✅ Ready to run script!")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🚀 To run the script:")
print("   python script.py")
print("\n📊 To compare performance:")
print("   python benchmark.py")
