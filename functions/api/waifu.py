import discord
from discord.ext import commands
from config import waifu_token
import io


class waifu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="waifu",
                      brief="Enlarge and enchance an image!",
                      description="Enlarge and enchance an image! -> ?waifu <link>")
    async def waifu(self, ctx, *, image=None):
        async with ctx.typing():
            # token comes from config.py file through the import config at the start of this file
            image_url = await self.get_img(ctx, image=image)
            async with self.bot.session.post("https://api.deepai.org/api/waifu2x", data={'image': image_url}, headers={'api-key': waifu_token}) as api_result:
                if api_result.status == 200:
                    # returns api result
                    image_url = (await api_result.json())['output_url']
                    # THIS PART OF THE (commented) CODE IS MEANT TO BE USED IF YOU PLAN ON PASTING THE CONTENT DIRECTLY
                    # IF YOU PLAN ON DOING THIS, PLEASE REFRAIN FROM USING AN EMBED, OR ELSE IT WON'T WORK
                    # gets image link
                    # async with self.bot.session.get(image_url) as response:
                    # gets image file
                    # image_file = io.BytesIO(await response.read())
                    # uploads image file and sends it back as file
                    embed = discord.Embed(url=image_url,
                                          title=f"{ctx.author.name}'s Waifu2x image", color=0xFF3351)
                    embed.set_image(url=image_url)
                    # await ctx.send(file=discord.File(image_file, 'waifu.png'))
                    await ctx.send(embed=embed)

    async def get_img(self, ctx, image=None):
        if image is None:
            if ctx.message.attachments:
                image = ctx.message.attachments[0].url
            else:
                # code gets messy from here, gets last message's information
                msg = await ctx.history(limit=2).flatten()
                # if message has an attachment, tries to apply it to image
                if len(msg[1].attachments) != 0:
                    image = msg[1].attachments[0].url
                 # if message has an embed type image, apply the url of the image to image
                elif len(msg[1].embeds) == 1 and msg[1].embeds[0].type == "image":
                    image = msg[1].embeds[0].url
                else:
                    return None
        return image


def setup(bot):
    bot.add_cog(waifu(bot))
