#!/usr/bin/env python3
"""
Benchmark script to compare original vs optimized performance
Run this to test the performance improvements
"""

import time
import subprocess
import sys
import os
from datetime import datetime


def run_benchmark():
    """Run a simple benchmark comparing both versions"""

    print("🏁 eFootball Minifaces Downloader - Performance Benchmark")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if all required files exist
    required_files = [
        "script.py",
        "script_optimized.py",
        "get_miniface.py",
        "get_miniface_optimized.py",
        "teams.py",
        "teams_optimized.py",
        "players_in_team.py",
        "players_in_team_optimized.py",
    ]

    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return

    print("✅ All required files found")
    print()

    # For safety, let's run a limited test (first league only)
    print("⚠️  This benchmark will process only a small subset for comparison")
    print("⚠️  Modify the scripts to limit to 1-2 leagues for testing")
    print()

    response = input("Continue with benchmark? (y/N): ")
    if response.lower() != "y":
        print("Benchmark cancelled")
        return

    results = {}

    # Test original version
    print("\n🐌 Testing Original Version...")
    print("-" * 40)

    start_time = time.time()
    try:
        # Run original script with timeout
        result = subprocess.run(
            [sys.executable, "script.py"],
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minute timeout
        )
        original_time = time.time() - start_time
        results["original"] = {
            "time": original_time,
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
        }
        print(f"✅ Original completed in {original_time:.2f} seconds")
    except subprocess.TimeoutExpired:
        original_time = 1800
        results["original"] = {
            "time": original_time,
            "success": False,
            "output": "",
            "error": "Timeout after 30 minutes",
        }
        print("⏰ Original version timed out after 30 minutes")
    except Exception as e:
        results["original"] = {
            "time": 0,
            "success": False,
            "output": "",
            "error": str(e),
        }
        print(f"❌ Original version failed: {e}")

    # Test optimized version
    print("\n🚀 Testing Optimized Version...")
    print("-" * 40)

    start_time = time.time()
    try:
        # Run optimized script with timeout
        result = subprocess.run(
            [sys.executable, "script_optimized.py"],
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minute timeout
        )
        optimized_time = time.time() - start_time
        results["optimized"] = {
            "time": optimized_time,
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
        }
        print(f"✅ Optimized completed in {optimized_time:.2f} seconds")
    except subprocess.TimeoutExpired:
        optimized_time = 1800
        results["optimized"] = {
            "time": optimized_time,
            "success": False,
            "output": "",
            "error": "Timeout after 30 minutes",
        }
        print("⏰ Optimized version timed out after 30 minutes")
    except Exception as e:
        results["optimized"] = {
            "time": 0,
            "success": False,
            "output": "",
            "error": str(e),
        }
        print(f"❌ Optimized version failed: {e}")

    # Print results
    print("\n📊 Benchmark Results")
    print("=" * 60)

    if results["original"]["success"] and results["optimized"]["success"]:
        original_time = results["original"]["time"]
        optimized_time = results["optimized"]["time"]
        speedup = original_time / optimized_time if optimized_time > 0 else float("inf")

        print(f"Original time:     {original_time:.2f} seconds")
        print(f"Optimized time:    {optimized_time:.2f} seconds")
        print(f"Speed improvement: {speedup:.2f}x faster")
        print(f"Time saved:        {original_time - optimized_time:.2f} seconds")

        if speedup > 2:
            print("🎉 Excellent performance improvement!")
        elif speedup > 1.5:
            print("✅ Good performance improvement!")
        elif speedup > 1.1:
            print("👍 Moderate performance improvement")
        else:
            print("⚠️  Limited performance improvement")
    else:
        print("❌ Benchmark incomplete due to errors:")
        if not results["original"]["success"]:
            print(f"   Original: {results['original']['error']}")
        if not results["optimized"]["success"]:
            print(f"   Optimized: {results['optimized']['error']}")

    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Tips:")
    print("   - For full testing, process a complete league")
    print("   - Adjust config.py for your system")
    print("   - Monitor CPU and memory usage during runs")
    print("   - Check output directories for completeness")


if __name__ == "__main__":
    run_benchmark()
