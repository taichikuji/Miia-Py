from discord import Embed
from discord.ext import commands
from config import OPENWEATHER_MAP
from datetime import datetime


class api(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="weather",
                      brief="Retrieve information from OpenWeatherMap's API",
                      description="Retrieve weather information from OpenWeatherMap's API, the default value for city is Madrid",
                      usage="`weather ( f | fahrenheit | c | celsius ) <city>`")
    async def weather(self, ctx, *args: str):
        async with ctx.typing():
            unit, values = self.unit_value(args)
            # token comes from config.py file through the import config at the start of this file
            params = {
                'q': values['city'],
                'appid': OPENWEATHER_MAP,
                'units': values['unit']
            }
            async with self.bot.session.get(
                    'https://api.openweathermap.org/data/2.5/weather', params=params) as api_result:
                # returns api result
                stats_json = await api_result.json()
                embed = self.weather_embed(stats_json, unit)
                await ctx.send(embed=embed)

    def unit_value(self, args):
        # Tries to get optional values like fahrenheit or celsius for proper measurement
        if args:
            if args[0] in ['f', 'fahrenheit', 'imperial']:
                unit = {
                    'temp': '°F',
                    'speed': 'mph'
                }
                params = {
                    'unit': 'imperial',
                    'city': ' '.join(str(tup) for tup in args[1:])
                }
            elif args[0] in ['m', 'celsius', 'metric']:
                unit = {
                    'temp': '°C',
                    'speed': 'm/s'
                }
                params = {
                    'unit': 'metric',
                    'city': ' '.join(str(tup) for tup in args[1:])
                }
            else:
                unit = {
                    'temp': '°C',
                    'speed': 'm/s'
                }
                params = {
                    'unit': 'metric',
                    'city': ' '.join(str(tup) for tup in args[0:])
                }
        else:
            unit = {
                'temp': '°C',
                'speed': 'm/s'
            }
            params = {
                'unit': 'metric',
                'city': 'Madrid'
            }
        return unit, params

    def icon(self, stats_json_array):
        # Depending on the icon that it receives, it puts one emoji or another
        icon = stats_json_array['weather'][0]['icon']
        if icon == '01d':
            icon = '☀️'
        elif icon == '01n':
            icon = '🌕'
        elif icon in ['02d', '02n']:
            icon = '⛅'
        elif icon in ['03d', '03n', '04d', '04n']:
            icon = '☁️'
        elif icon in ['09d', '09n', '10d', '10n']:
            icon = '🌧️'
        elif icon in ['11d', '11n']:
            icon = '🌩️'
        elif icon in ['13d', '13n']:
            icon = '❄️'
        elif icon in ['50d', '50n']:
            icon = '🌫️'
        return icon

    def weather_embed(self, stats_json_array, unit):
        try:
            ws = stats_json_array
            emoji = self.icon(ws)
            # creation of embed with all important OpenWeatherMap's json info
            em = {
                "title": f"Weather in **{ws['name']}**, **{ws['sys']['country']}**",
                "description": f"{emoji} {ws['weather'][0]['main']}, {ws['weather'][0]['description']}",
                "color": self.bot.color,
                "thumbnail": {"url": f"https://openweathermap.org/img/wn/{ws['weather'][0]['icon']}@2x.png"},
                "fields": [{"name": "Weather",
                            "value":
                            f"**Temperature**: {ws['main']['temp']}{unit['temp']}, feels like {ws['main']['feels_like']}{unit['temp']}\n"
                            f"**Wind**: {ws['wind']['speed']}{unit['speed']}\n"
                            f"**Clouds**: {ws['clouds']['all']}%\n"
                            f"**Humidity**: {ws['main']['humidity']}%\n",
                            "inline": True},
                           {"name": "Time",
                            "value":
                            f"**Sunrise**: {datetime.fromtimestamp(ws['sys']['sunrise']+ws['timezone']).strftime('%H:%M')}\n"
                            f"**Sunset**: {datetime.fromtimestamp(ws['sys']['sunset']+ws['timezone']).strftime('%H:%M')}\n"}],
                # careful with the footer information, if you see data is wrong, try removing the timezone and check again
                "footer": {"text": f"Data collected at {datetime.fromtimestamp(ws['dt']+ws['timezone']).strftime('%H:%M:%S')}"}
            }
            embed = Embed.from_dict(em)
            return embed
        except KeyError as error:
            embed = Embed(color=self.bot.color)
            embed.description = f""":x: Error handling the API
                                Value {error} wasn't found or is incorrect"""
            return embed


def setup(bot):
    bot.add_cog(api(bot))
