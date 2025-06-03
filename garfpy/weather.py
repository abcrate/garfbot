import discord
import requests
import json

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather_by_zip(self, zip_code, country_code='US', units='metric'):
        """
        Get weather data by zip code
        
        Args:
            zip_code (str): ZIP code
            country_code (str): Country code (default: 'US')
            units (str): 'metric', 'imperial', or 'standard'
        """
        params = {
            'zip': f'{zip_code},{country_code}',
            'appid': self.api_key,
            'units': units
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
    
def weather_embed(self, weather_data):
    if not weather_data:
        embed = discord.Embed(
            title="❌ Error",
            description="Could not fetch weather data",
            color=discord.Color.red()
        )
        return embed
    
    weather_emojis = {
        'clear sky': '☀️',
        'few clouds': '🌤️',
        'scattered clouds': '⛅',
        'broken clouds': '☁️',
        'shower rain': '🌦️',
        'rain': '🌧️',
        'thunderstorm': '⛈️',
        'snow': '❄️',
        'mist': '🌫️'
    }
    
    condition = weather_data['weather'][0]['description'].lower()
    emoji = weather_emojis.get(condition, '🌍')
    
    embed = discord.Embed(
        title=f"{emoji} Weather in {weather_data['name']}",
        description=f"{weather_data['weather'][0]['description'].title()}",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🌡️ Temperature", 
        value=f"{weather_data['main']['temp']}°C\nFeels like {weather_data['main']['feels_like']}°C", 
        inline=True
    )
    
    embed.add_field(
        name="💧 Humidity", 
        value=f"{weather_data['main']['humidity']}%", 
        inline=True
    )
    
    embed.add_field(
        name="🗜️ Pressure", 
        value=f"{weather_data['main']['pressure']} hPa", 
        inline=True
    )
    
    if 'wind' in weather_data:
        embed.add_field(
            name="💨 Wind Speed", 
            value=f"{weather_data['wind']['speed']} m/s", 
            inline=True
        )
    
    if 'visibility' in weather_data:
        embed.add_field(
            name="👁️ Visibility", 
            value=f"{weather_data['visibility']/1000} km", 
            inline=True
        )
    
    embed.set_footer(
        text=f"Lat: {weather_data['coord']['lat']}, Lon: {weather_data['coord']['lon']}"
    )
    
    return embed

@commands.command(name='weather')
async def weather_command(self, ctx, zip_code: str, country_code: str = 'US'):
    """
    Get weather by zip code
    Usage: !weather 10001 US
    """
    await ctx.typing()
    
    weather_data = await self.get_weather_by_zip(zip_code, country_code)
    embed = self.create_weather_embed(weather_data)
    
    await ctx.send(embed=embed)



    # def display_weather(self, weather_data):
    #     """Pretty print weather information"""
    #     if not weather_data:
    #         print("No weather data available")
    #         return
        
    #     print(f"\n🌤️  Weather for {weather_data['name']}")
    #     print(f"Temperature: {weather_data['main']['temp']}°C")
    #     print(f"Feels like: {weather_data['main']['feels_like']}°C")
    #     print(f"Condition: {weather_data['weather'][0]['description'].title()}")
    #     print(f"Humidity: {weather_data['main']['humidity']}%")
    #     print(f"Pressure: {weather_data['main']['pressure']} hPa")
    #     if 'visibility' in weather_data:
    #         print(f"Visibility: {weather_data['visibility']/1000} km")

# if __name__ == "__main__":
#     API_KEY = "x"
    
#     weather = WeatherAPI(API_KEY)
    
#     zip_codes = ['10001', '90210', '60601']
    
#     for zip_code in zip_codes:
#         data = weather.get_weather_by_zip(zip_code)
#         weather.display_weather(data)
#         print("-" * 40)