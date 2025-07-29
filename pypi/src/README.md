A weather app in terminal.

## What You Get

- Current weather conditions with ASCII art
- 3-day forecast
- No API keys needed (uses wttr.in)

## Install from PyPI

```bash
pip install pyrain-weather
pyrain-weather
```

## How to Use

Type a city name, hit Enter. That's it.

**Keyboard shortcuts:**
- `R` - Refresh weather
- `Ctrl+C` - Exit

**Weather displays:**
- **Current** - Right now conditions with ASCII weather art
- **Forecast** - Next 3 days overview
- **Hourly** - Today and tomorrow every 3 hours
- **Details** - Location info, moon

## Technical Notes

**Data source:** [wttr.in](https://wttr.in) - free weather API, no signup required

## Troubleshooting

**"Network Error"** - Check your internet connection

**"City Not Found"** - Try the full city name or add country (e.g., "London, UK")

**Import errors** - Make sure all dependencies are installed: `pip install textual httpx rich`