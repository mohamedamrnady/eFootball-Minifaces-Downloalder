# Debug Mode Usage Guide

## Overview

The optimized script now includes comprehensive logging and debug capabilities. You can control the verbosity of output to suit your needs.

## Usage Examples

### 1. Normal Mode (Default)
```bash
python script_optimized.py
```
- Shows basic progress information
- Shows final summary
- Shows errors if they occur
- **Recommended for regular use**

### 2. Debug Mode (Verbose)
```bash
python script_optimized.py --debug
# or
python script_optimized.py -d
```
- Shows detailed progress for every player
- Shows timing information
- Shows configuration details
- Shows network requests and responses
- **Recommended for troubleshooting**

### 3. Quiet Mode (Minimal Output)
```bash
python script_optimized.py --quiet
# or
python script_optimized.py -q
```
- Only shows errors and final summary
- No progress information
- **Recommended for automated runs/GitHub Actions**

### 4. Debug + Quiet Mode
```bash
python script_optimized.py --debug --quiet
```
- Debug logging for troubleshooting
- Minimal non-debug output
- **Recommended for detailed logs without noise**

## Command Line Options

### Performance Overrides
```bash
# Override number of concurrent teams
python script_optimized.py --workers-teams 2

# Override number of concurrent players per team  
python script_optimized.py --workers-players 4

# Override request delay (in seconds)
python script_optimized.py --delay 0.2

# Combine multiple options
python script_optimized.py --debug --workers-teams 2 --delay 0.3
```

### Help
```bash
python script_optimized.py --help
```

## Log Levels

### Always Shown
- **Errors**: Network failures, parsing errors, file I/O issues
- **Final Summary**: Total players processed, execution time, success rate

### Debug Mode Only
- **[DEBUG]**: Detailed progress, configuration, timing
- **[INFO]**: Team and league processing status  
- **[SUCCESS]**: Individual player completions

### Example Output

**Normal Mode:**
```
Loading Info...
Loaded!
Starting optimized download with 4 team workers, 8 player workers
Total leagues to process: 45

Started League (1/45): Premier League
✓ Completed League Premier League in 45.23s (18/20 teams successful)

🎉 All done! Processed 15847 unique players in 1247.89s
Leagues processed: 44/45
Average time per player: 0.08s
```

**Debug Mode:**
```
[DEBUG] Configuration loaded from config.py
Loading Info...
[DEBUG] Configuration: Teams=4, Players=8, Delay=0.1s
[DEBUG] Found 45 leagues to process
Loaded!
Starting optimized download with 4 team workers, 8 player workers
Total leagues to process: 45

[DEBUG] Processing league: Premier League at https://...
Started League (1/45): Premier League
[DEBUG] Found 20 teams in Premier League
[INFO] Processing team 1/20 in Premier League
[DEBUG] Found 25 players in team 1
[DEBUG] Processing player 123456 from team_1
[SUCCESS] Processed player 123456 from team_1
...
[INFO] Completed team 1/20 in Premier League (23/25 players successful)
✓ Completed League Premier League in 45.23s (18/20 teams successful)

🎉 All done! Processed 15847 unique players in 1247.89s
Leagues processed: 44/45
Average time per player: 0.08s

[DEBUG] Final Statistics:
[DEBUG] - Total execution time: 1247.89s
[DEBUG] - Players per second: 12.70
[DEBUG] - Thread configuration used: Teams=4, Players=8
[DEBUG] - Request delay used: 0.1s
```

**Quiet Mode:**
```
🎉 All done! Processed 15847 unique players in 1247.89s
Leagues processed: 44/45
Average time per player: 0.08s
```

## Environment Variables

You can also control debug mode via environment variables:

```bash
# Enable debug mode
export DEBUG=1
python script_optimized.py

# Disable debug mode
unset DEBUG
python script_optimized.py
```

## GitHub Actions Integration

The optimized GitHub Actions workflow now uses quiet mode:

```yaml
- name: Run optimized script
  run: |
    python script_optimized.py --quiet
```

This ensures clean logs in automated environments while still showing errors and the final summary.

## Troubleshooting

### Getting Rate Limited?
```bash
# Use debug mode to see request timing
python script_optimized.py --debug --delay 0.3 --workers-teams 2
```

### Script Running Slowly?
```bash
# Debug mode shows timing per operation
python script_optimized.py --debug
```

### Want to See All Network Activity?
```bash
# Enable debug in all modules
export DEBUG=1
python script_optimized.py --debug
```

### Silent Run for Cron Jobs?
```bash
# Only errors and summary will be shown
python script_optimized.py --quiet 2>/dev/null
```

## Tips

1. **Start with normal mode** to see if everything works
2. **Use debug mode** when things aren't working as expected
3. **Use quiet mode** for automated scripts and cron jobs
4. **Combine debug + quiet** for detailed logs without progress spam
5. **Override workers** if you're getting rate limited or timeouts
