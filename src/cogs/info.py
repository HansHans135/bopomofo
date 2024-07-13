"""
Cog module for the informational commands.
"""
import sqlite3

import discord
from discord.ext import commands


class InfoCog(commands.Cog):
    """
    The cog class for the informational commands.
    """

    def __init__(self, client: discord.AutoShardedBot) -> None:
        self.client = client

    @discord.slash_command(name="help", description="幫助選單")
    async def help(self, ctx: discord.ApplicationContext) -> None:
        """
        The slash command to show the help menu.

        :param ctx: The context of the slash command.
        :type ctx: discord.ApplicationContext
        """
        await ctx.defer()

        with sqlite3.connect("data.db") as db:
            db_date = db.execute("SELECT * FROM translate")
        times = 0
        for befor, after in db_date.fetchall():
            times += 1

        eb = discord.Embed(
            title="如何使用",
            description="""
            想想看當你在聊天的時候看到`su3cl3`
            你會認為他是忘記切輸入法吧？
            現在，透過機器人直接翻譯對話吧！
            """,
        )
        eb.add_field(
            name="機器人原始碼",
            value="[GitHub](https://github.com/HansHans135/bopomofo/)",
        )
        eb.add_field(
            name="相關連結",
            value="[支援群組](https://discord.gg/JayWx9RygN)．[邀請機器人](https://discord.com/application-directory/1126517167966396436)．[Discord TW](https://discordservers.tw/bots/1126517167966396436)",
            inline=False,
        )
        eb.set_image(url="https://raw.githubusercontent.com/HansHans135/bopomofo/main/example.gif")

        eb2 = discord.Embed(title="一些酷酷的資料")
        eb2.add_field(name="群組數量", value=f"{len(self.client.guilds)}", inline=False)
        eb2.add_field(name="用戶數量", value=f"{len(self.client.users)}", inline=False)
        eb2.add_field(name="翻譯數量", value=f"{times}", inline=False)
        await ctx.respond(embeds=[eb, eb2])


def setup(client: discord.AutoShardedBot) -> None:
    """
    The setup function of the cog.
    """
    client.add_cog(InfoCog(client))
