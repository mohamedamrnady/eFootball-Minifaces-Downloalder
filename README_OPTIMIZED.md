# eFootball Minifaces Downloader - Optimized Version

## Overview

This is an optimized, multi-threaded version of the eFootball minifaces downloader that significantly improves performance through concurrent processing.

## Performance Improvements

### Original vs Optimized

| Feature | Original | Optimized |
|---------|----------|-----------|
| Processing | Sequential | Multi-threaded |
| Team Processing | One at a time | Up to 4 concurrent |
| Player Processing | One at a time | Up to 8 concurrent per team |
| Image Downloads | Sequential | Up to 6 concurrent per player |
| Error Handling | Basic | Robust with retries |
| Rate Limiting | None | Configurable delays |
| Progress Tracking | Minimal | Detailed with timing |

### Expected Speed Improvement

- **3-5x faster** for team and player discovery
- **5-10x faster** for image downloads  
- **Overall 4-8x faster** depending on network and server conditions

## Files Structure

### Original Files
- `script.py` - Original sequential script
- `get_miniface.py` - Original image downloader
- `teams.py` - Original team scraper
- `players_in_team.py` - Original player scraper

### Optimized Files
- `script_optimized.py` - **Main optimized script** ⭐
- `get_miniface_optimized.py` - Thread-safe image downloader
- `teams_optimized.py` - Improved team scraper
- `players_in_team_optimized.py` - Improved player scraper
- `config.py` - Performance configuration

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Optimized Version
```bash
python script_optimized.py
```

### 3. Run Original Version (for comparison)
```bash
python script.py
```

## Configuration

Edit `config.py` to tune performance for your system:

```python
# Conservative settings (slower but safer)
MAX_WORKERS_TEAMS = 2
MAX_WORKERS_PLAYERS = 4
MAX_WORKERS_IMAGES = 3
REQUEST_DELAY = 0.2

# Default settings (balanced)
MAX_WORKERS_TEAMS = 4
MAX_WORKERS_PLAYERS = 8
MAX_WORKERS_IMAGES = 6
REQUEST_DELAY = 0.1

# Aggressive settings (faster but may get rate limited)
MAX_WORKERS_TEAMS = 6
MAX_WORKERS_PLAYERS = 12
MAX_WORKERS_IMAGES = 10
REQUEST_DELAY = 0.05
```

## Optimization Techniques Used

### 1. Concurrent Processing
- **Team Level**: Process multiple teams simultaneously
- **Player Level**: Download multiple player data concurrently
- **Image Level**: Download and process images in parallel

### 2. Thread Safety
- Thread-safe player tracking to avoid duplicates
- Thread-safe directory creation
- Thread-safe event caching for background images

### 3. Resource Management
- ThreadPoolExecutor for proper thread management
- Configurable worker limits to prevent overwhelming servers
- Automatic cleanup of thread resources

### 4. Error Handling & Resilience
- Retry logic for failed requests
- Exponential backoff for retries
- Graceful handling of network timeouts
- Detailed error reporting with context

### 5. Rate Limiting
- Configurable delays between requests
- Respectful to server resources
- Prevents IP blocking/rate limiting

### 6. Performance Monitoring
- Progress tracking for teams and players
- Timing information for each phase
- Summary statistics at completion

## Memory Usage

The optimized version uses more memory due to threading but includes safeguards:
- Limited thread pools prevent memory explosion
- Proper resource cleanup
- Efficient image processing

## Troubleshooting

### Getting Rate Limited?
Increase delays in `config.py`:
```python
REQUEST_DELAY = 0.3
IMAGE_REQUEST_DELAY = 0.1
```

### Out of Memory?
Reduce worker counts:
```python
MAX_WORKERS_TEAMS = 2
MAX_WORKERS_PLAYERS = 4
MAX_WORKERS_IMAGES = 3
```

### Network Timeouts?
Increase timeout values:
```python
REQUEST_TIMEOUT = 60
```

## Monitoring Progress

The optimized script provides detailed progress information:
```
Loading Info...
Loaded!
Starting optimized download with 4 team workers, 8 player workers
Total leagues to process: 45

Started League (1/45): Premier League
  Processing team 1/20 in Premier League
    ✓ Processed player 123456 from team_1
    ✓ Processed player 789012 from team_1
  ✓ Completed team 1/20 in Premier League (25 players)
✓ Completed League Premier League in 45.23s (20 teams)

🎉 All done! Processed 15847 unique players in 1247.89s
Average time per player: 0.08s
```

## Best Practices

1. **Start Conservative**: Use default settings first
2. **Monitor Resources**: Watch CPU and memory usage
3. **Respect Servers**: Don't set delays too low
4. **Run Tests**: Compare with original to verify results
5. **Backup Data**: Keep copies of important downloads

## Technical Details

### Threading Architecture
```
Main Thread
├── League Processing (Sequential)
│   ├── Team Pool (4 workers)
│   │   ├── Player Pool (8 workers per team)
│   │   │   ├── Image Pool (6 workers per player)
│   │   │   └── Thread-safe file operations
│   │   └── Progress tracking
│   └── Error aggregation
└── Final statistics
```

### Thread Safety Measures
- Global locks for shared resources
- Atomic operations for counters
- Thread-local storage where appropriate
- Proper synchronization primitives

## License

Same as original project.

## Contributing

When contributing optimizations:
1. Maintain thread safety
2. Add appropriate error handling  
3. Update configuration options
4. Test with various worker counts
5. Measure performance improvements
