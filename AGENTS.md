# Agent Development Guide

## Testing & Execution
- Run tests: `python test.py`
- Run main script: `python script.py` 
- Install dependencies: `pip install -r requirements.txt`
- No specific lint/build commands - this is a Python scraping project

## Code Style & Conventions
- **Imports**: Standard library first, then third-party (`requests`, `bs4`, `pandas`, `wand`), then local modules
- **Functions**: Use snake_case naming, include docstrings for public functions
- **Variables**: Use snake_case, descriptive names (e.g., `leagues_urls`, `done_players`)
- **Constants**: Use UPPER_CASE for configuration values in `config.py`
- **Threading**: Use `ThreadPoolExecutor`, thread-safe locks for shared resources (`threading.Lock()`)
- **Error handling**: Use `log_error()` and `log_debug()` functions, graceful degradation with try/catch
- **Configuration**: All settings in `config.py` with fallback defaults in main modules

## Project Structure
- Main entry: `script.py` (optimized multi-threaded version)
- Configuration: `config.py` (threading, delays, timeouts)
- Core modules: `teams.py`, `players_in_team.py`, `get_miniface.py`
- Output directory: `MinifaceServer/content/miniface-server/`
- Test suite: `test.py`

## Key Patterns
- Thread-safe global state using locks (e.g., `done_players_lock`)
- Configurable delays and timeouts for rate limiting
- Concurrent processing at team, player, and image levels
- Progress tracking with detailed logging