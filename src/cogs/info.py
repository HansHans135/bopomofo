"""
Cog module for the informational commands.
"""

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
        eb.set_image(url="https://raw.githubusercontent.com/HansHans135/bopomofo/main/example.gif")

        await ctx.respond(embed=eb)


def setup(client: discord.AutoShardedBot) -> None:
    """
    The setup function of the cog.
    """
    client.add_cog(InfoCog(client))
