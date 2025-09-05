# GitHub Actions Workflow Guide

## Overview

The `new-release.yml` workflow now intelligently handles different trigger types with conditional logging and enhanced manual control.

## Trigger Types

### 🕒 Scheduled Release (Automatic)
**When:** Every Thursday at midnight UTC  
**Behavior:** 
- ✅ Runs in **quiet mode** (minimal output)
- ✅ Uses **optimized default settings**
- ✅ Focused on reliability and speed
- ✅ Clean logs for automated processing

**Command executed:**
```bash
python script_optimized.py --quiet
```

### 🎛️ Manual Release (workflow_dispatch)
**When:** Triggered manually from GitHub Actions tab  
**Behavior:**
- ✅ Runs in **debug mode by default** (detailed logging)
- ✅ Shows **comprehensive troubleshooting info**
- ✅ **Configurable options** via inputs
- ✅ Enhanced verification and statistics

**Command executed:**
```bash
python script_optimized.py --debug  # (with optional overrides)
```

## Manual Trigger Options

When triggering manually, you can configure:

### 🐛 Debug Mode
- **Default:** `true` (enabled)
- **Options:** `true` / `false`
- **Purpose:** Enable detailed logging for troubleshooting

### ⚙️ Worker Override
- **Format:** `teams,players` (e.g., `"2,4"`)
- **Example:** `"2,4"` = 2 concurrent teams, 4 players per team
- **Purpose:** Reduce load if getting rate limited

### ⏱️ Delay Override
- **Format:** Number in seconds (e.g., `"0.3"`)
- **Purpose:** Increase delays if getting rate limited

## Usage Examples

### 1. Standard Manual Run (Default)
Just click "Run workflow" with default options:
- Debug logging: ✅ Enabled
- Workers: Default from config.py
- Delay: Default from config.py

### 2. Conservative Manual Run (Rate Limit Safe)
Set inputs:
- Debug mode: `true`
- Worker override: `"2,4"`
- Delay override: `"0.3"`

Result: Slower but very safe execution with full logging

### 3. Silent Manual Run
Set inputs:
- Debug mode: `false`
- Worker override: (leave empty)
- Delay override: (leave empty)

Result: Same as scheduled run but manually triggered

## Workflow Outputs

### 📊 Scheduled Release Logs
```
Starting eFootball miniface download...
Trigger: schedule
Scheduled trigger detected - running in optimized quiet mode
Executing: python script_optimized.py --quiet

🎉 All done! Processed 15847 unique players in 1247.89s
Leagues processed: 44/45
Average time per player: 0.08s

📊 Download Statistics:
  - Total miniface files: 15847
  - Total players: 15847
✅ Verification completed successfully
```

### 🔍 Manual Release Logs (Debug Mode)
```
Starting eFootball miniface download...
Trigger: workflow_dispatch
Manual trigger detected
Debug logging enabled
Executing: python script_optimized.py --debug

[DEBUG] Configuration loaded from config.py
Loading Info...
[DEBUG] Configuration: Teams=4, Players=8, Delay=0.1s
[DEBUG] Found 36 leagues to process
...detailed progress logs...

🎉 All done! Processed 15847 unique players in 1247.89s
Leagues processed: 44/45
Average time per player: 0.08s

🔍 Debug Information:
  - Directory structure:
  - Sample player directories:
  - Recent files:
✅ Verification completed successfully
```

## Benefits

### ✅ For Scheduled Runs
- **Clean logs** - No debug spam in automated runs
- **Optimal performance** - Uses tested default settings
- **Reliability focused** - Proven configuration

### ✅ For Manual Runs
- **Full visibility** - See exactly what's happening
- **Troubleshooting ready** - Debug logs help identify issues
- **Flexible control** - Adjust settings on the fly
- **Problem diagnosis** - Detailed verification output

## Troubleshooting

### Getting Rate Limited?
**Manual run with:**
- Worker override: `"2,4"`
- Delay override: `"0.3"`
- Debug mode: `true`

### Want to See What's Happening?
**Manual run with:**
- Debug mode: `true` (default)
- Keep other settings default

### Need Fastest Possible Run?
**Manual run with:**
- Debug mode: `false`
- Worker override: `"6,12"`
- Delay override: `"0.05"`

### Schedule Not Working?
Check the logs of recent scheduled runs - they'll show any errors in a clean format.

## Release Notes

Release notes now indicate trigger type:
- **Scheduled releases:** "Automatically triggered on schedule"
- **Manual releases:** "Manually triggered release"

This helps track which releases were automated vs manually created for testing/emergency updates.

---

**Perfect for both production automation and development troubleshooting!** 🎯
