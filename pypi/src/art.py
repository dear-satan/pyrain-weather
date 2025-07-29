"""ASCII art for pyrain-weather conditions with colors."""

from rich.text import Text


def get_colored_weather_art(condition):
    """Get colored ASCII art for weather condition."""
    condition = condition.lower()
    art = Text()

    if 'rain' in condition or 'shower' in condition or 'drizzle' in condition:
        art.append("""
      .---.     
     (     )    
    (___.___)   
   ' ' ' ' ' '  
  ' ' ' ' ' ' ' 
    """, style="blue")

    elif 'snow' in condition or 'blizzard' in condition:
        art.append("""
      .---.     
     (     )    
    (___.___)   
   * * * * * *  
  * * * * * * * 
    """, style="white")

    elif 'thunder' in condition or 'storm' in condition:
        art.append("""
      .---.     
     (     )    
    (___.___)   
   '  ⚡ ' ⚡ ' ' 
  ' ⚡ ' ' ' ⚡ ⚡ 
    """, style="yellow")

    elif 'sun' in condition or 'clear' in condition or 'sunny' in condition:
        art.append("""
      \   /
       .-.
    ― (   ) ―
       `-’
      /   \  
    """, style="yellow")

    elif 'cloud' in condition or 'overcast' in condition:
        art.append("""
      .---.     
     (     )    
    (___..__) 
    """, style="bright_black")

    elif 'mist' in condition or 'fog' in condition:
        art.append("""
≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈
 ≈ ≈ ≈ ≈ ≈ ≈ ≈ 
≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈
 ≈ ≈ ≈ ≈ ≈ ≈ ≈ 
≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈
    """, style="dim white")

    elif 'wind' in condition:
        art.append("""
~ ~ ~ ~ ~ ~ ~ ~ >
 ~ ~ ~ ~ ~ ~ ~ > 
~ ~ ~ ~ ~ ~ ~ ~ >
 ~ ~ ~ ~ ~ ~ ~ > 
~ ~ ~ ~ ~ ~ ~ ~ >
    """, style="cyan")

    else:  # default
        art.append("""
      .---.     
     (  ?  )    
    (___.___) 
    """, style="white")

    return art

# Keep old function for backward compatibility
def get_weather_art(condition):
    """Get plain ASCII art for weather condition."""
    return get_colored_weather_art(condition).plain


APP_HEADER = """
╔═══════════════════════════════════════╗
║        PYRAIN-WEATHER CURRENT         ║
╚═══════════════════════════════════════╝
"""

FORECAST_HEADER = """
╔═══════════════════════════════════════╗
║         PYRAIN-WEATHER FORECAST       ║
╚═══════════════════════════════════════╝
"""
APP_HEADER = """
╔═══════════════════════════════════════╗
║        PYRAIN-WEATHER CURRENT         ║
╚═══════════════════════════════════════╝
"""

FORECAST_HEADER = """
╔═══════════════════════════════════════╗
║         PYRAIN-WEATHER FORECAST       ║
╚═══════════════════════════════════════╝
"""
