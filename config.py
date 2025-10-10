# Configuration file for the optimized eFootball miniface downloader
# Python 3.14t Free-Threading Optimized

import sys

# Detect if GIL is disabled (free-threading mode)
if hasattr(sys, "_is_gil_enabled"):
    GIL_ENABLED = sys._is_gil_enabled()
else:
    GIL_ENABLED = True  # Assume GIL is enabled if we can't detect

# Debug and Logging Configuration
DEBUG_MODE = (
    False  # Enable debug logging by default (can be overridden by --debug flag)
)
QUIET_MODE = False  # Enable quiet mode by default (can be overridden by --quiet flag)

# Threading Configuration - Optimized for Free-Threading
# Adjust these based on your system and network capacity
# With free-threading (GIL disabled), we can use MORE workers for true parallelism
if not GIL_ENABLED:
    # Free-threading optimized: 2x more workers for true parallel execution
    MAX_WORKERS_TEAMS = 8  # Concurrent teams processing (2x increase)
    MAX_WORKERS_PLAYERS = 16  # Concurrent players per team (2x increase)
    MAX_WORKERS_IMAGES = 12  # Concurrent image downloads per player (2x increase)
else:
    # Conservative settings for GIL-bound Python
    MAX_WORKERS_TEAMS = 4  # Concurrent teams processing
    MAX_WORKERS_PLAYERS = 8  # Concurrent players per team
    MAX_WORKERS_IMAGES = 6  # Concurrent image downloads per player

# Request Rate Limiting
# These delays help avoid overwhelming the server
REQUEST_DELAY = 0.5  # Delay between main requests (seconds)
IMAGE_REQUEST_DELAY = 0.5  # Delay between image downloads (seconds)
REQUEST_TIMEOUT = 30  # Timeout for all HTTP requests (seconds)

# Retry Configuration
MAX_RETRIES = 3  # Number of retries for failed requests
RETRY_DELAY_BASE = 1  # Base delay for retries (exponential backoff)

# Performance Notes:
# - Increase worker counts if you have good bandwidth and CPU
# - Increase delays if you get rate limited or blocked
# - Decrease delays if the server can handle more load
# - Monitor CPU and memory usage when adjusting worker counts

# Conservative settings (slower but safer):
# MAX_WORKERS_TEAMS = 2
# MAX_WORKERS_PLAYERS = 4
# MAX_WORKERS_IMAGES = 3
# REQUEST_DELAY = 0.2

# Aggressive settings (faster but may get rate limited):
# MAX_WORKERS_TEAMS = 6
# MAX_WORKERS_PLAYERS = 12
# MAX_WORKERS_IMAGES = 10
# REQUEST_DELAY = 0.05
