import discord
from discord.ext import commands
from config import weatherstack_token


class api(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="weather",
                      brief="Retrieve information from WeatherStack's API",
                      description="Retrieve weather information from WeatherStack's API, the default value for city is Madrid")
    async def weather(self, ctx, *, city='Madrid'):
        async with ctx.typing():
            # token comes from config.py file through the import config at the start of this file
            params = {
                'access_key': weatherstack_token,
                'query': city
            }
            async with self.bot.session.get(
                    'http://api.weatherstack.com/current', params=params) as api_result:
                try:
                    # returns api result
                    stats_json = await api_result.json()
                    embed = self.weather_embed(ctx, stats_json)
                    await ctx.send(embed=embed)
                except:
                    await ctx.send(":x: Error handling the API")
                    return None

    def weather_embed(self, ctx, stats_json_array):
        try:
            ws = stats_json_array
            # creation of embed with all important WeatherStack's json info
            em = {
                "title": "WeatherStack",
                "description": f"Weather in **{ws['location']['name']}, {ws['location']['region']}**",
                "color": 0xFF3351,
                "thumbnail": {"url": f"{ws['current']['weather_icons'][0]}"},
                "fields": [{"name": "Temperature",
                            "value": f"{ws['current']['temperature']}°C",
                            "inline": True},
                           {"name": "Feels like",
                            "value": f"{ws['current']['temperature']}°C",
                            "inline": True},
                           {"name": "Weather Description",
                            "value": f"{ws['current']['weather_descriptions'][0]}",
                            "inline": True},
                           {"name": "Humidity",
                            "value": f"{ws['current']['humidity']}%",
                            "inline": True},
                           {"name": "Wind Speed",
                            "value": f"{ws['current']['wind_speed']} kph",
                            "inline": True},
                           {"name": "Wind Direction",
                            "value": f"{ws['current']['wind_dir']}",
                            "inline": True},
                           {"name": "Local Time",
                            "value": f"{ws['location']['localtime']}"}]
            }
            embed = discord.Embed.from_dict(em)
            return embed
        except KeyError as error:
            embed = discord.Embed(color=0xFF3351)
            embed.description = f""":x: Error handling the API
                                Value {error} wasn't found or is incorrect"""
            return embed


def setup(bot):
    bot.add_cog(api(bot))
