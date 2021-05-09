from discord import Embed
from discord.ext import commands

from config import WAIFU_TOKEN


class api(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="waifu",
        brief="Enlarge and enchance an image!",
        description="Enlarge and enchance an image using DeepAI's API. Resolution is limited to 1600p.",
        usage="`waifu <url> | <embedded image> | <previous url> | <previous embedded image>`",
    )
    async def waifu(self, ctx, *, image=None):
        async with ctx.typing():
            # token comes from config.py file through the import config at the start of this file
            image_url = await self.get_img(ctx, image=image)
            async with self.bot.session.post(
                "https://api.deepai.org/api/waifu2x",
                data={"image": image_url},
                headers={"api-key": WAIFU_TOKEN},
            ) as api_result:
                try:
                    # returns api result
                    image_url = (await api_result.json())["output_url"]
                    em = {
                        "url": image_url,
                        "title": f"{ctx.author.name}'s Waifu2x image",
                        "color": self.bot.color,
                        "image": {"url": image_url},
                    }
                    await ctx.send(embed=Embed.from_dict(em))
                except:
                    await ctx.send(":x: Error handling the API")
                    return None

    async def get_img(self, ctx, image=None):
        if image is None:
            if ctx.message.attachments:
                image = ctx.message.attachments[0].url
            else:
                # gets last message's information
                msg = await ctx.history(limit=2).flatten()
                # if message has an attachment, tries to apply it to image
                if len(msg[1].attachments) != 0:
                    image = msg[1].attachments[0].url
                # if message has an embed type image, apply the url of the image to image
                elif len(msg[1].embeds) == 1 and msg[1].embeds[0].type == "image":
                    image = msg[1].embeds[0].url
                else:
                    await ctx.send(f":x: No image was found, try again!")
                    return None
        return image


def setup(bot):
    bot.add_cog(api(bot))
