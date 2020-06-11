import discord
from discord.ext import commands
from config import weatherstack_token
import requests


class weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="weather",
                      brief="Retrieve information from WeatherStack's API",
                      description="Retrieve information from WeatherStack's API -> ?weather <string> (by default it's Madrid)")
    async def weather(self, ctx, *, city='Madrid'):
        # token comes from config.py file through the import config at the start of this file
        params = {
            'access_key': weatherstack_token,
            'query': city
        }
        api_result = requests.get(
            'http://api.weatherstack.com/current', params)
        # saves json into ws
        ws = api_result.json()
        # creation of embed with all important WeatherStack's json info
        embed = discord.Embed(title="WeatherStack",
                              description=f"Weather in **{ws['location']['name']}, {ws['location']['region']}**", color=0xFF3351)
        embed.set_thumbnail(url=f"{ws['current']['weather_icons'][0]}")
        embed.add_field(name="Temperature",
                        value=f"{ws['current']['temperature']}°C")
        embed.add_field(name="Feels like",
                        value=f"{ws['current']['feelslike']}°C")
        embed.add_field(name="Weather Description",
                        value=f"{ws['current']['weather_descriptions'][0]}")
        embed.add_field(name="Humidity",
                        value=f"{ws['current']['humidity']}%")
        embed.add_field(name="Wind Speed",
                        value=f"{ws['current']['wind_speed']} kph")
        embed.add_field(name="Wind Direction",
                        value=f"{ws['current']['wind_dir']}")
        embed.add_field(name="Local Time",
                        value=f"{ws['location']['localtime']}")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(weather(bot))
