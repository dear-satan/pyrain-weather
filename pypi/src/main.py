import httpx
import os
from datetime import datetime, timedelta
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static, Button, TabbedContent, TabPane
from textual.timer import Timer
from rich.text import Text
from .art import get_colored_weather_art, APP_HEADER, FORECAST_HEADER


class AsciiArtDisplay(Static):
    """Widget to display weather ASCII art."""

    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.border_title = "WEATHER ART"

    def update_art(self, condition):
        """Update ASCII art based on weather condition."""
        if not condition:
            self.update("No weather art available")
            return

        art_text = Text()
        art_text.append(
            f"CONDITION: {condition.upper()}\n\n", style="bold cyan")
        art_text.append(get_colored_weather_art(condition))
        art_text.append(
            f"\n\nUPDATED: {datetime.now().strftime('%H:%M:%S')}", style="dim white")

        self.update(art_text)


class WeatherDisplay(Static):
    """Widget to display weather data"""

    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.border_title = "CURRENT WEATHER"

    def update_weather(self, weather_data):
        if not weather_data:
            self.update("*** No weather data available ***")
            return

        weather_text = Text()
        weather_text.append(APP_HEADER, style="bold cyan")

        # Define data fields
        data_fields = [
            ("LOCATION", "location", "bold cyan"),
            ("TEMPERATURE", "temperature", "bold yellow"),
            ("CONDITION", "condition", "bold blue"),
            ("HUMIDITY", "humidity", "bold cyan"),
            ("WIND", "wind", "bold magenta"),
            ("VISIBILITY", "visibility", "bold green"),
            ("PRESSURE", "pressure", "bold bright_blue"),
            ("UV INDEX", "uv_index", "bold yellow"),
            ("SUNRISE", "sunrise", "bold orange1"),
            ("SUNSET", "sunset", "bold orange3")
        ]

        for label, key, style in data_fields:
            value = weather_data.get(key, 'N/A')
            weather_text.append(f"{label}: ", style=style)
            weather_text.append(f"{value}\n", style="white")

        self.update(weather_text)


class ForecastDisplay(Static):
    """Simplified forecast display widget."""

    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.border_title = "3-DAY FORECAST"

    def update_forecast(self, forecast_data):
        if not forecast_data:
            self.update("*** No forecast data available ***")
            return

        forecast_text = Text()
        forecast_text.append(FORECAST_HEADER, style="bold cyan")

        for i, day in enumerate(forecast_data[:5]):
            if i > 0:
                forecast_text.append("─" * 35 + "\n", style="dim white")

            forecast_text.append(
                f"{day.get('day', f'Day {i+1}')}\n", style="bold cyan")
            forecast_text.append(f"{day.get('temp', 'N/A')}\n", style="yellow")
            forecast_text.append(
                f"{day.get('condition', 'N/A')}\n", style="white")

            # Show precipitation data
            if day.get('precipitation'):
                forecast_text.append(
                    f"Rain: {day.get('precipitation')}\n", style="blue")
            if day.get('chance_rain'):
                forecast_text.append(
                    f"Rain chance: {day.get('chance_rain')}\n", style="blue")

        self.update(forecast_text)


class HourlyDisplayBase(Static):
    """Base class for hourly weather forecast displays."""

    def __init__(self, title, **kwargs):
        super().__init__("", **kwargs)
        self.border_title = title
        self._title = title

    def format_hourly_display(self, hourly_data, header_text):
        """Common method to format hourly data display."""
        if not hourly_data:
            return f"*** No {self._title.lower()} data available ***"

        hourly_text = Text()
        hourly_text.append(
            "╔═══════════════════════════════════════╗\n", style="bold cyan")
        hourly_text.append(
            f"║{header_text:^39}║\n", style="bold cyan")
        hourly_text.append(
            "╚═══════════════════════════════════════╝\n\n", style="bold cyan")

        # Display hourly data in columns (4 hours per row)
        hours_per_row = 4
        total_hours = min(24, len(hourly_data))

        for row_start in range(0, total_hours, hours_per_row):
            row_end = min(row_start + hours_per_row, total_hours)
            row_hours = hourly_data[row_start:row_end]

            # Time row
            times = " │ ".join(
                [f"{hour.get('time', 'N/A'):>12}" for hour in row_hours])
            hourly_text.append(f"{times}\n", style="bold yellow")

            # Temperature row
            temps = " │ ".join(
                [f"{hour.get('temp_short', 'N/A'):>12}" for hour in row_hours])
            hourly_text.append(f"{temps}\n", style="bold orange1")

            # Condition row
            conditions = " │ ".join(
                [f"{hour.get('condition_short', 'N/A'):>12}" for hour in row_hours])
            hourly_text.append(f"{conditions}\n", style="white")

            # Rain chance row (if any hour has rain data) - fixed alignment
            if any(hour.get('chance_rain') for hour in row_hours):
                rain_chances = " │ ".join(
                    [f"{hour.get('chance_rain', ''):>12}" for hour in row_hours])
                hourly_text.append(f"{rain_chances}\n", style="blue")

            # Separator
            if row_end < total_hours:
                hourly_text.append("─" * 60 + "\n", style="dim white") # who named those colors smh

        return hourly_text


class HourlyDisplay(HourlyDisplayBase):
    """Widget to display hourly weather forecast in columns."""

    def __init__(self, **kwargs):
        super().__init__("HOURLY FORECAST", **kwargs)

    def update_hourly(self, hourly_data):
        hourly_text = self.format_hourly_display(
            hourly_data, "HOURLY FORECAST")
        self.update(hourly_text)


class TomorrowHourlyDisplay(HourlyDisplayBase):
    """tommorows weather"""

    def __init__(self, **kwargs):
        super().__init__("TOMORROW HOURLY FORECAST", **kwargs)

    def update_hourly(self, hourly_data):
        hourly_text = self.format_hourly_display(
            hourly_data, "TOMORROW HOURLY FORECAST")
        self.update(hourly_text)


class DetailedDisplay(Static):
    """location etc."""

    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.border_title = "DETAILED INFORMATION"

    def update_details(self, detailed_data):
        if not detailed_data:
            self.update("*** No detailed data available ***")
            return

        details_text = Text()
        details_text.append(
            "╔═══════════════════════════════════════╗\n", style="bold cyan")
        details_text.append(
            "║           DETAILED WEATHER            ║\n", style="bold cyan")
        details_text.append(
            "╚═══════════════════════════════════════╝\n\n", style="bold cyan")

        # Filter out N/A values and organize sections
        def filter_na_values(fields_data):
            return [(label, key) for label, key in fields_data
                    if detailed_data.get(key) and detailed_data.get(key) != 'N/A']

        sections = [
            ("LOCATION", [
                ("Area", "area_name"), ("Region",
                                        "region"), ("Country", "country"),
                ("Latitude", "latitude"), ("Longitude", "longitude")
            ], "bold green"),
            ("ASTRONOMY", [
                ("Moon Phase", "moon_phase"), ("Moon Illumination", "moon_illumination"),
                ("Moonrise", "moonrise"), ("Moonset", "moonset")
            ], "bold blue")
        ]

        for section_title, fields, title_style in sections:
            filtered_fields = filter_na_values(fields)
            if filtered_fields:  # Only show section if it has data
                details_text.append(f"{section_title}\n", style=title_style)
                details_text.append("─" * 40 + "\n", style="dim white")

                for label, key in filtered_fields:
                    value = detailed_data.get(key)
                    details_text.append(f"{label}: {value}\n", style="white")
                details_text.append("\n")

        details_text.append(
            f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim white")
        self.update(details_text)


class WeatherApp(App):
    """Simplified weather app with side-by-side layout."""

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_city = "London"

        # Load CSS
        css_path = os.path.join(os.path.dirname(__file__), 'styles.css.txt')
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                self.CSS = f.read()

    def compose(self) -> ComposeResult:
        """Create child widgets with side-by-side layout."""
        yield Header()

        with Container(classes="title"):
            yield Static("PYRAIN-WEATHER APPLICATION")

        with Container(classes="search-container"):
            with Horizontal():
                yield Input(placeholder="Enter city name", id="city_input")
                yield Button("SEARCH", id="search_btn", variant="primary")

        with TabbedContent():
            with TabPane("Current", id="current_tab"):
                with Horizontal():
                    with Container(classes="weather-container"):
                        yield WeatherDisplay(id="weather_display")
                    with Container(classes="art-container"):
                        yield AsciiArtDisplay(id="art_display")

            with TabPane("Forecast", id="forecast_tab"):
                with Container(classes="forecast-container"):
                    yield ForecastDisplay(id="forecast_display")

            with TabPane("Hourly", id="hourly_tab"):
                with TabbedContent():
                    with TabPane("Today", id="today_hourly_tab"):
                        with Container(classes="hourly-container"):
                            yield HourlyDisplay(id="hourly_display")

                    with TabPane("Tomorrow", id="tomorrow_hourly_tab"):
                        with Container(classes="hourly-container"):
                            yield TomorrowHourlyDisplay(id="tomorrow_hourly_display")

            with TabPane("Details", id="details_tab"):
                with Container(classes="details-container"):
                    yield DetailedDisplay(id="detailed_display")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize app."""
        self.title = "pyrain-weather"
        self.sub_title = "Press R to refresh • Ctrl+C to quit"
        self.call_after_refresh(self.get_weather, self.current_city)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "search_btn":
            city_input = self.query_one("#city_input", Input)
            city = city_input.value.strip()
            if city:
                await self.get_weather(city)
            else:
                self.notify("Please enter a city name", severity="warning")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        city = event.value.strip()
        if city:
            await self.get_weather(city)
        else:
            self.notify("Please enter a city name", severity="warning")

    async def action_refresh(self):
        """Manually refresh weather."""
        await self.get_weather(self.current_city)
        self.notify("Weather refreshed", severity="information")

    def action_quit(self):
        """Quit the application."""
        self.exit()

    def parse_weather_data(self, weather_json):
        """Extract and format weather data."""
        try:
            current = weather_json.get('current_condition', [{}])[0]
            nearest_area = weather_json.get('nearest_area', [{}])[0]
            astronomy = weather_json.get('weather', [{}])[
                0].get('astronomy', [{}])[0]

            def get_value(item):
                if isinstance(item, list) and item:
                    return item[0].get('value', 'N/A')
                elif isinstance(item, dict):
                    return item.get('value', item)
                return 'N/A'

            area_name = get_value(nearest_area.get('areaName', 'N/A'))
            country = get_value(nearest_area.get('country', 'N/A'))

            return {
                'location': f"{area_name}, {country}",
                'temperature': f"{current.get('temp_C', 'N/A')}°C ({current.get('temp_F', 'N/A')}°F)",
                'condition': get_value(current.get('weatherDesc', 'N/A')),
                'humidity': f"{current.get('humidity', 'N/A')}%",
                'wind': f"{current.get('windspeedKmph', 'N/A')} km/h {current.get('winddir16Point', '')}".strip(),
                'visibility': f"{current.get('visibility', 'N/A')} km",
                'pressure': f"{current.get('pressure', 'N/A')} mb",
                'uv_index': current.get('uvIndex', 'N/A'),
                'sunrise': astronomy.get('sunrise', 'N/A'),
                'sunset': astronomy.get('sunset', 'N/A')
            }
        except Exception as e:
            return {'error': f"Error parsing weather data: {str(e)}"}

    def parse_detailed_data(self, weather_json):
        """Extract detailed weather data."""
        try:
            nearest_area = weather_json.get('nearest_area', [{}])[0]
            astronomy = weather_json.get('weather', [{}])[
                0].get('astronomy', [{}])[0]

            def get_value(item):
                if isinstance(item, list) and item:
                    return item[0].get('value', '')
                elif isinstance(item, dict):
                    return item.get('value', item)
                return ''

            return {
                'area_name': get_value(nearest_area.get('areaName', '')),
                'region': get_value(nearest_area.get('region', '')),
                'country': get_value(nearest_area.get('country', '')),
                'latitude': nearest_area.get('latitude', ''),
                'longitude': nearest_area.get('longitude', ''),
                'moon_phase': astronomy.get('moon_phase', ''),
                'moon_illumination': f"{astronomy.get('moon_illumination', '')}%" if astronomy.get('moon_illumination') else '',
                'moonrise': astronomy.get('moonrise', ''),
                'moonset': astronomy.get('moonset', '')
            }
        except Exception:
            return {}

    def parse_hourly_data(self, weather_json):
        """Extract hourly weather data optimized for column display."""
        hourly_data = []
        try:
            today = weather_json.get('weather', [{}])[0]

            for hour in today.get('hourly', []):
                time_24 = hour.get('time', '0')

                try:
                    time_int = int(str(time_24).zfill(4)[:4])
                    hours = time_int // 100
                    minutes = time_int % 100
                    time_formatted = f"{hours:02d}:{minutes:02d}"
                except:
                    time_formatted = "00:00"

                condition = hour.get('weatherDesc', [{}])[
                    0].get('value', 'N/A')
                condition_short = condition[:12] if len(
                    condition) > 12 else condition

                hourly_data.append({
                    'time': time_formatted,
                    'temp': f"{hour.get('tempC', 'N/A')}°C",
                    'temp_short': f"{hour.get('tempC', 'N/A')}°",
                    'condition': condition,
                    'condition_short': condition_short,
                    'chance_rain': f"{hour.get('chanceofrain', '')}%" if hour.get('chanceofrain') else '',
                    'humidity': f"{hour.get('humidity', '')}%" if hour.get('humidity') else '',
                    'wind': f"{hour.get('windspeedKmph', '')}kmh" if hour.get('windspeedKmph') else '',
                })

            return hourly_data
        except Exception:
            return []

    def parse_tomorrow_hourly_data(self, weather_json):
        """Extract tomorrow's hourly weather data optimized for column display."""
        hourly_data = []
        try:
            weather_days = weather_json.get('weather', [])
            if len(weather_days) < 2:
                return []

            tomorrow = weather_days[1]

            for hour in tomorrow.get('hourly', []):
                time_24 = hour.get('time', '0')

                try:
                    time_int = int(str(time_24).zfill(4)[:4])
                    hours = time_int // 100
                    minutes = time_int % 100
                    time_formatted = f"{hours:02d}:{minutes:02d}"
                except:
                    time_formatted = "00:00"

                condition = hour.get('weatherDesc', [{}])[
                    0].get('value', 'N/A')
                condition_short = condition[:12] if len(
                    condition) > 12 else condition

                hourly_data.append({
                    'time': time_formatted,
                    'temp': f"{hour.get('tempC', 'N/A')}°C",
                    'temp_short': f"{hour.get('tempC', 'N/A')}°",
                    'condition': condition,
                    'condition_short': condition_short,
                    'chance_rain': f"{hour.get('chanceofrain', '')}%" if hour.get('chanceofrain') else '',
                    'humidity': f"{hour.get('humidity', '')}%" if hour.get('humidity') else '',
                    'wind': f"{hour.get('windspeedKmph', '')}kmh" if hour.get('windspeedKmph') else '',
                })

            return hourly_data
        except Exception:
            return []

    async def get_weather(self, city: str) -> None:
        """Optimized weather fetching with better error handling."""
        displays = {
            'weather': self.query_one("#weather_display", WeatherDisplay),
            'art': self.query_one("#art_display", AsciiArtDisplay),
            'forecast': self.query_one("#forecast_display", ForecastDisplay),
            'hourly': self.query_one("#hourly_display", HourlyDisplay),
            'tomorrow_hourly': self.query_one("#tomorrow_hourly_display", TomorrowHourlyDisplay),
            'detailed': self.query_one("#detailed_display", DetailedDisplay)
        }

        # Show loading state
        for display in displays.values():
            display.update("Loading...")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                weather_url = f"https://wttr.in/{city}?format=j1"
                response = await client.get(weather_url)

                if response.status_code == 200:
                    weather_json = response.json()

                    # Parse all data
                    weather_data = self.parse_weather_data(weather_json)
                    detailed_data = self.parse_detailed_data(weather_json)
                    hourly_data = self.parse_hourly_data(weather_json)
                    tomorrow_hourly_data = self.parse_tomorrow_hourly_data(
                        weather_json)

                    # Parse forecast with proper rain data
                    forecast_data = []
                    for day in weather_json.get('weather', []):
                        # Get average rain chance from hourly data
                        hourly_rain = [h.get('chanceofrain', '0')
                                       for h in day.get('hourly', [])]
                        avg_rain = sum(int(r) for r in hourly_rain if r.isdigit(
                        )) // len(hourly_rain) if hourly_rain else 0

                        # Get total precipitation
                        total_precip = day.get('totalprecipMM', '0')

                        forecast_data.append({
                            'day': day.get('date', 'N/A'),
                            'temp': f"{day.get('mintempC', 'N/A')}°C - {day.get('maxtempC', 'N/A')}°C",
                            'condition': day.get('hourly', [{}])[0].get('weatherDesc', [{}])[0].get('value', 'N/A'),
                            'chance_rain': f"{avg_rain}%",
                            'precipitation': f"{total_precip}mm" if total_precip and total_precip != '0' else None,
                        })

                    # Update all displays
                    displays['weather'].update_weather(weather_data)
                    displays['art'].update_art(
                        weather_data.get('condition', ''))
                    displays['forecast'].update_forecast(forecast_data)
                    displays['hourly'].update_hourly(hourly_data)
                    displays['tomorrow_hourly'].update_hourly(
                        tomorrow_hourly_data)
                    displays['detailed'].update_details(detailed_data)

                    self.current_city = city
                    self.notify(
                        f"Weather updated for {city} (pyrain-weather)", severity="information")
                else:
                    raise Exception(f"HTTP {response.status_code}")

        except Exception as e:
            error_msg = f"Failed to get weather data for '{city}'\nError: {str(e)}"
            for key, display in displays.items():
                display.update(
                    f"{key.title()} unavailable" if key != 'weather' else error_msg)
            self.notify(f"Error: {str(e)} (pyrain-weather)", severity="error")


def main(): # for pypi
    """Run the pyrain-weather app."""
    app = WeatherApp()
    app.run()


if __name__ == "__main__":
    main()