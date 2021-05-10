from config import REDDIT_ID, REDDIT_TOKEN
from discord import Embed
from discord.ext import commands
from praw import Reddit
from prawcore import BadRequest, Forbidden, NotFound
from utils.paginator import Paginator


class miia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = None
        if REDDIT_ID and REDDIT_TOKEN:
            self.reddit = Reddit(
                client_id=REDDIT_ID,
                client_secret=REDDIT_TOKEN,
                user_agent="Miia:%s:0.1.7" % REDDIT_ID,
            )

    @commands.command(
        name="reddit",
        aliases=["r"],
        brief="Shows a list of posts from a subreddit",
        description="Shows a list of posts from a subreddit, with pagination!",
        usage="`reddit <subreddit>`\n"
        "`r | reddit ( s | shuffle | r | rising ) <subreddit>`",
    )
    async def rpost(self, ctx, *args: str):
        async with ctx.typing():
            try:
                results = await self._parse(ctx, self.subreddit(args))
                await Paginator(results).start(ctx)
            except BadRequest:
                await ctx.send(
                    ":x: Bad request, have you written the subreddit correctly?"
                )
            except Forbidden:
                await ctx.send(":x: Forbidden request, I can't access it!")
            except NotFound:
                await ctx.send(":x: Subreddit not found!")
            except IndexError:
                await ctx.send(
                    ":x: `IndexError`, did you type a subreddit? Check `help reddit` for more information!"
                )
            except TypeError:
                await ctx.send(
                    ":x: `TypeError`, it didn't find any results or you're searching nsfw posts on a sfw channel!"
                )
            except Exception:
                await ctx.send(":x: Unexpected exception!")

    def subreddit(self, args):
        # Tries to get optional value, if it can't it puts the first value as a subreddit
        if args[0] in ["s", "shuffle", "r", "rising"] and args[1]:
            option = self.reddit.subreddit(args[1]).random_rising(limit=20)
        else:
            option = self.reddit.subreddit(args[0]).hot(limit=20)
        return option

    def is_safe(self, submission, ctx):
        # This filters out posts that aren't compatible
        # (both channel and post have to be either sfw or nsfw)
        if not ctx.channel.is_nsfw() and submission.over_18:
            safe = False
        else:
            safe = True
        return safe

    def is_image(self, submission):
        value = None
        # This filters out any links that don't have pictures
        if any(
            extension in submission.url
            for extension in (".jpg", ".jpeg", ".png", ".gif", ".webp")
        ):
            value = submission.url
        return value

    async def _parse(self, ctx, option):
        results = []
        # This select the proper command depending on the optional input
        for submission in option:
            if self.is_safe(submission, ctx):
                if self.is_image(submission):
                    em = {
                        "title": f"{submission.title}",
                        "url": submission.url,
                        "permalink": submission.permalink,
                    }
                    results.append(em)
        return await self.reddit_embed(results)

    async def reddit_embed(self, results):
        embed_results = []
        size = len(results)

        if size == 0:
            return None
        for start, values in enumerate(results, 1):
            em = {
                "title": values["title"],
                "url": f"https://reddit.com{values['permalink']}",
                "color": self.bot.color,
                "image": {"url": values["url"]},
                "footer": {"text": f"Page {start}/{size}"},
            }
            embed = Embed.from_dict(em)
            embed_results.append(embed)
        return embed_results


def setup(bot):
    bot.add_cog(miia(bot))
