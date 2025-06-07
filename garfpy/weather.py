import discord
import aiohttp
import config
from garfpy import logger


class WeatherAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or config.WEATHER_TOKEN
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def parse_location(self, location):
        location = location.strip().lower()

        if location.isdigit():
            if len(location) == 5:
                return {"zip": f"{location},US"}
            else:
                return {"zip": location}

        parts = location.split()

        if len(parts) == 1:
            return {"q": f"{parts[0]},US"}

        elif len(parts) == 2:
            city, second = parts

            if len(second) == 2 and second.upper() not in [
                "AK",
                "AL",
                "AR",
                "AZ",
                "CA",
                "CO",
                "CT",
                "DE",
                "FL",
                "GA",
                "HI",
                "IA",
                "ID",
                "IL",
                "IN",
                "KS",
                "KY",
                "LA",
                "MA",
                "MD",
                "ME",
                "MI",
                "MN",
                "MO",
                "MS",
                "MT",
                "NC",
                "ND",
                "NE",
                "NH",
                "NJ",
                "NM",
                "NV",
                "NY",
                "OH",
                "OK",
                "OR",
                "PA",
                "RI",
                "SC",
                "SD",
                "TN",
                "TX",
                "UT",
                "VA",
                "VT",
                "WA",
                "WI",
                "WV",
                "WY",
                "DC",
                "AS",
                "GU",
                "MP",
                "PR",
                "VI",
            ]:
                return {"q": f"{city},{second.upper()}"}
            else:
                return {"q": f"{city},{second},US"}

        elif len(parts) == 3:
            city, state, country = parts
            return {"q": f"{city},{state},{country.upper()}"}

        else:
            if len(parts[-1]) == 2:
                city_parts = parts[:-1]
                country = parts[-1]
                city_name = " ".join(city_parts)
                return {"q": f"{city_name},{country.upper()}"}

            elif len(parts) >= 2 and len(parts[-1]) == 2 and len(parts[-2]) <= 2:
                city_parts = parts[:-2]
                state = parts[-2]
                country = parts[-1]
                city_name = " ".join(city_parts)
                return {"q": f"{city_name},{state},{country.upper()}"}

            else:
                city_name = " ".join(parts)
                return {"q": f"{city_name},US"}

    async def get_weather(self, location, units="metric"):
        location_params = self.parse_location(location)

        params = {
            **location_params,
            "appid": self.api_key,
            "units": units,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching weather data for '{location}': {e}")
            return None

    def weather_embed(self, weather_data):
        if not weather_data:
            embed = discord.Embed(
                title="❌ Error",
                description="Could not fetch weather data",
                color=discord.Color.red(),
            )
            return embed

        weather_emojis = {
            "clear sky": "☀️",
            "few clouds": "🌤️",
            "scattered clouds": "⛅",
            "broken clouds": "☁️",
            "shower rain": "🌦️",
            "rain": "🌧️",
            "thunderstorm": "⛈️",
            "snow": "❄️",
            "mist": "🌫️",
        }

        condition = weather_data["weather"][0]["description"].lower()
        emoji = weather_emojis.get(condition, "🌍")

        embed = discord.Embed(
            title=f"{emoji} Weather in {weather_data['name']}",
            description=f"{weather_data['weather'][0]['description'].title()}",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="🌡️ Temperature",
            value=f"{weather_data['main']['temp']}°C\nFeels like {weather_data['main']['feels_like']}°C",
            inline=True,
        )

        embed.add_field(
            name="💧 Humidity",
            value=f"{weather_data['main']['humidity']}%",
            inline=True,
        )

        embed.add_field(
            name="🗜️ Pressure",
            value=f"{weather_data['main']['pressure']} hPa",
            inline=True,
        )

        if "wind" in weather_data:
            embed.add_field(
                name="💨 Wind Speed",
                value=f"{weather_data['wind']['speed']} m/s",
                inline=True,
            )

        if "visibility" in weather_data:
            embed.add_field(
                name="👁️ Visibility",
                value=f"{weather_data['visibility'] / 1000} km",
                inline=True,
            )

        embed.set_footer(
            text=f"Lat: {weather_data['coord']['lat']}, Lon: {weather_data['coord']['lon']}"
        )

        return embed

    async def weather(self, location):
        weather_data = await self.get_weather(location)
        embed = self.weather_embed(weather_data)
        return embed
