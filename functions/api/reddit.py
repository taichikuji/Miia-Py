from discord import Embed
from discord.ext import commands
from praw import Reddit
# from re import compile
from config import reddit_id, reddit_token
from utils.paginator import Paginator


class api(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = None
        # self.regex_video = compile(
        #     r'https://(www\.)?reddit\.com/r/[^/]+/comments/[^/]+')
        if reddit_id and reddit_token:
            self.reddit = Reddit(client_id=reddit_id,
                                 client_secret=reddit_token,
                                 user_agent='Miia:%s:0.1.7' % reddit_id)

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.author != self.bot.user:
    #         regex_match = self.regex_video.findall(message.content)
    #         if regex_match:
    #             async with self.bot.session.get("https://reddit.tube/parse", params={'url': message.content}) as api_result:
    #                 try:
    #                     url = (await api_result.json())['share_url']
    #                     em = {
    #                         "title": "Reddit video",
    #                         "url": message.content,
    #                         "color": self.bot.color,
    #                         "video": {"url": url}
    #                     }
    #                     await message.channel.send(embed=Embed.from_dict(em))
    #                 except:
    #                     return None

    @commands.command(name="reddit",
                      brief="reddit example",
                      description="reddit example's command using praw")
    async def rpost(self, ctx, *args: str):
        async with ctx.channel.typing():
            if self.reddit and args:
                subreddit, optional = self.optional_value(args)
                results = await self._parse(ctx, subreddit, optional)
                await Paginator(results).start(ctx)
            else:
                await ctx.send(":x: Error handling the request or API, try again with a parameter (subreddit)")

    def optional_value(self, args):
        # Tries to get optional value, if it can't it puts the first value as a subreddit
        if args[0] in ['s', 'shuffle', 'r', 'rising'] and args[1]:
            optional = args[0]
            subreddit = args[1]
        else:
            optional = None
            subreddit = args[0]
        return subreddit, optional

    def is_safe(self, submission, ctx):
        # This filters out posts that aren't compatible
        # (both channel and post have to be either sfw or nsfw)
        if (not ctx.channel.is_nsfw() and submission.over_18):
            safe = False
        else:
            safe = True
        return safe

    def is_image(self, submission):
        value = None
        # This filters out any links that don't have pictures
        if any(extension in submission.url
               for extension in ('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            value = submission.url
        return value

    async def _parse(self, ctx, subreddit, optional):
        results = []
        # This select the proper command depending on the optional input
        if optional:
            option = self.reddit.subreddit(subreddit).random_rising(limit=20)
        else:
            option = self.reddit.subreddit(subreddit).hot(limit=20)

        for submission in option:
            if self.is_safe(submission, ctx):
                if self.is_image(submission):
                    em = {
                        "title": f"{submission.title}",
                        "url": submission.url
                    }
                    results.append(em)

        return self.reddit_embed(results)

    def reddit_embed(self, results):
        embed_results = []
        size = len(results)
        if size == 0:
            return None
        for start, values in enumerate(results, 1):
            em = {
                "title": values['title'],
                "url": values['url'],
                "color": self.bot.color,
                "image": {"url": values['url']},
                "footer": {"text": f"Page {start}/{size}"}
            }
            embed = Embed.from_dict(em)
            embed_results.append(embed)
        return embed_results

    @rpost.error
    async def run_error(self, error):
        raise error


def setup(bot):
    bot.add_cog(api(bot))
