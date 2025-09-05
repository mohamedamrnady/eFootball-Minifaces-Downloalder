#!/usr/bin/env python3
"""
Simple test script to verify the optimized downloader works correctly
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all optimized modules can be imported"""
    print("🔍 Testing imports...")

    try:
        from teams_optimized import league_info_scrapper, teams_urls_scrapper

        print("  ✅ teams_optimized imported successfully")
    except Exception as e:
        print(f"  ❌ teams_optimized import failed: {e}")
        return False

    try:
        from players_in_team_optimized import players_in_team

        print("  ✅ players_in_team_optimized imported successfully")
    except Exception as e:
        print(f"  ❌ players_in_team_optimized import failed: {e}")
        return False

    try:
        from get_miniface_optimized import miniface_downloader, download_image

        print("  ✅ get_miniface_optimized imported successfully")
    except Exception as e:
        print(f"  ❌ get_miniface_optimized import failed: {e}")
        return False

    try:
        import config

        print("  ✅ config imported successfully")
        print(f"     - MAX_WORKERS_TEAMS: {config.MAX_WORKERS_TEAMS}")
        print(f"     - MAX_WORKERS_PLAYERS: {config.MAX_WORKERS_PLAYERS}")
        print(f"     - REQUEST_DELAY: {config.REQUEST_DELAY}")
    except Exception as e:
        print(f"  ⚠️  config import failed, using defaults: {e}")

    return True


def test_scraping():
    """Test basic scraping functionality"""
    print("\n🌐 Testing web scraping...")

    try:
        from teams_optimized import league_info_scrapper

        print("  Testing league info scrapping...")
        start_time = time.time()

        # Test getting league URLs (limited)
        leagues_urls = league_info_scrapper(
            "https://www.pesmaster.com/efootball-2022/", "url", 2022
        )

        elapsed = time.time() - start_time

        if leagues_urls and len(leagues_urls) > 0:
            print(f"  ✅ Found {len(leagues_urls)} leagues in {elapsed:.2f}s")
            print(f"     First league: {leagues_urls[0]}")
            return True
        else:
            print("  ❌ No leagues found")
            return False

    except Exception as e:
        print(f"  ❌ Scraping test failed: {e}")
        return False


def test_threading():
    """Test basic threading functionality"""
    print("\n🧵 Testing threading capabilities...")

    def dummy_task(n):
        time.sleep(0.1)
        return f"Task {n} completed"

    try:
        start_time = time.time()

        # Test with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(dummy_task, i) for i in range(8)]
            results = [f.result() for f in futures]

        elapsed = time.time() - start_time

        if len(results) == 8 and elapsed < 0.5:  # Should be much faster than 0.8s
            print(f"  ✅ Threading working correctly (8 tasks in {elapsed:.2f}s)")
            return True
        else:
            print(f"  ❌ Threading may not be working optimally ({elapsed:.2f}s)")
            return False

    except Exception as e:
        print(f"  ❌ Threading test failed: {e}")
        return False


def test_directory_setup():
    """Test directory creation"""
    print("\n📁 Testing directory setup...")

    try:
        cwdir = os.path.join("MinifaceServer", "content", "miniface-server")
        if not os.path.exists(cwdir):
            os.makedirs(cwdir)
            print(f"  ✅ Created directory: {cwdir}")
        else:
            print(f"  ✅ Directory already exists: {cwdir}")

        # Test write permissions
        test_file = os.path.join(cwdir, "test_write.txt")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("  ✅ Write permissions confirmed")

        return True

    except Exception as e:
        print(f"  ❌ Directory test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 eFootball Minifaces Downloader - Optimization Test")
    print("=" * 60)

    tests = [
        ("Import Test", test_imports),
        ("Directory Test", test_directory_setup),
        ("Threading Test", test_threading),
        ("Scraping Test", test_scraping),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("-" * 30)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 All tests passed! The optimized version should work correctly.")
        print("\n💡 Next steps:")
        print("   1. Run: python script_optimized.py")
        print("   2. Adjust config.py if needed")
        print("   3. Monitor performance during execution")
    else:
        print(
            f"\n⚠️  {len(results) - passed} test(s) failed. Please review the errors above."
        )
        print("\n🔧 Troubleshooting:")
        print("   1. Check that all dependencies are installed")
        print("   2. Verify internet connection")
        print("   3. Check file permissions")

    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
