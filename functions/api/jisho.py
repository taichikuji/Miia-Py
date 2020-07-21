from discord.ext import commands
from discord.ext.commands import Cog
from utils.paginator import Paginator
from discord import Embed
from typing import Dict, List, Set
from re import finditer


class api(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jisho_url = "http://jisho.org/search/{}"

    @commands.command(name="jisho",
                      brief="Search a term on Jisho's dictionary",
                      description="Search a term in both English and Japanese using Jisho's dictionary",
                      usage="`jisho <keyword>`")
    async def jisho_(self, ctx, *, keyword: str):
        async with ctx.typing():
            params = {
                'keyword': keyword
            }
            async with self.bot.session.get(
                    'https://jisho.org/api/v1/search/words', params=params) as api_result:
                try:
                    # returns api result
                    stats_json = (await api_result.json())['data']
                    results = self._parse(keyword, stats_json)
                    await Paginator(results).start(ctx)
                except:
                    await ctx.send(":x: Error handling the API")
                    return None

    @jisho_.error
    async def run_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"You need to input an argument, {ctx.author.mention}!")
        else:
            raise error

    def _parse(self, keyword,  response=[]):
        results = []
        for data in response:
            readings: Set[str] = set()
            words: Set[str] = set()
            kanji_link: Set[str] = set()

            for kanji in data['japanese']:
                reading: str = kanji.get('reading')
                if reading and reading not in readings:
                    readings.add(reading)
                word: str = kanji.get('word')

                if word and word not in words:
                    words.add(word)

            for word in words:
                for res in finditer('[一-龯]', word):
                    if res and res not in kanji_link:
                        res = f'[{res.group(0)}](https://jisho.org/search/{res.group(0)}%23kanji)'
                        kanji_link.add(res)

            senses: Dict[str, List[str]] = {
                'english': [],
                'parts_of_speech': []
            }

            for sense in data['senses']:
                senses['english'].extend(
                    sense.get('english_definitions', ()))
                sense['parts_of_speech'].extend(
                    sense.get('parts_of_speech', ()))

            try:
                senses['parts_of_speech'].remove('Wikipedia definition')
            except ValueError:
                pass

            result = {'readings': list(
                readings), 'words': list(words), 'kanji': list(kanji_link), **senses}
            results.append(result)
        return self.jisho_embed(keyword, results)

    def jisho_embed(self, keywords, stats_json):
        results = []
        if not stats_json:
            return None

        size = len(stats_json)
        for start, res in enumerate(stats_json, 1):
            res = {key: "\n".join(val) or "None" for key,
                   val in res.items()}
            res['english'] = ", ".join(res['english'].split("\n"))
            em = {
                "title": keywords,
                "color": self.bot.color,
                "url": self.jisho_url.format("%20".join(keywords.split())),
                "fields": [{
                    "name": "Words",
                    "value": res['words']
                }, {
                    "name": "Kanji",
                    "value": res['kanji']
                }, {
                    "name": "Readings",
                    "value": res['readings']
                }, {
                    "name": "Parts of Speech",
                    "value": res['parts_of_speech']
                }, {
                    "name": "Meanings",
                    "value": res['english']
                }],
                "footer": {"text": f"Page {start}/{size}"}
            }
            embed = Embed.from_dict(em)
            results.append(embed)
        return results


def setup(bot):
    bot.add_cog(api(bot))
