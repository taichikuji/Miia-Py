from typing import Optional
from discord import Embed
from discord.utils import get
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.menus import MenuPages, ListPageSource


def syntax(command):
    cmd_and_aliases = "|".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(
                value) else f"<{key}>")

    params = " ".join(params)

    return f"`{cmd_and_aliases} {params}`"


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        super().__init__(data, per_page=5)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)
        # fields is created but empty so that it can add the values afterwards
        em = {
            "title": "Help",
            "description": "Uh... Yes! I'll do my best! Here are the commands",
            "color": self.ctx.bot.color,
            "thumbnail": {"url": str(self.ctx.guild.me.avatar_url)},
            "footer": {"text": f"Page {offset:,} - {min(len_data, offset+self.per_page-1):,}/{len_data}"},
            "fields": []
        }
        for name, value in fields:
            em["fields"].append({
                "name": name,
                "value": value,
                "inline": False})
        embed = Embed.from_dict(em)
        return embed

    async def format_page(self, menu, entries):
        fields = []

        for entry in entries:
            fields.append((entry.brief or "No description", syntax(entry)))

        return await self.write_page(menu, fields)


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    async def cmd_help(self, ctx, command):
        em = {
            "title": f"`{command}`",
            "description": syntax(command),
            "color": self.bot.color,
            "fields": [{"name": "Command description",
                        "value": f"{command.description}"},
                       {"name": "Command usage",
                        "value": f"{command.usage}"}]
        }
        embed = Embed.from_dict(em)
        await ctx.send(embed=embed)

    @command(name="help",
             brief="Shows a list of the available commands",
             description="Shows a list of the available commands, a brief description and the parameters!",
             usage="`help ( <command> )`")
    async def show_help(self, ctx, cmd: Optional[str]):
        if cmd is None:
            menu = MenuPages(source=HelpMenu(
                ctx, list(self.bot.commands)), delete_message_after=True, timeout=60.0)
            await menu.start(ctx)
        else:
            if (command := get(self.bot.commands, name=cmd)):
                await self.cmd_help(ctx, command)

            else:
                await ctx.send("That command does not exist.")


def setup(bot):
    bot.add_cog(Help(bot))
