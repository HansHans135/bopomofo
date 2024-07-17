"""
Cog module for the informational commands.
"""

import discord

from ..main import BaseCog


class InfoCog(BaseCog):
    """
    The cog class for the informational commands.
    """

    @discord.slash_command(name="help", description="幫助選單")
    async def help(self, ctx: discord.ApplicationContext) -> None:
        """
        The slash command to show the help menu.
        """
        await ctx.defer()

        embed = discord.Embed(
            title="如何使用",
            description=(
                # intro
                "想想看當你在聊天的時候看到 `su3cl3`\n"
                "你會認為他是忘記切輸入法吧？\n"
                "現在，透過機器人直接翻譯對話吧！\n\n"
                # urls
                "[GitHub](https://github.com/HansHans135/bopomofo/)．"
                "[Discord](https://discord.gg/JayWx9RygN)．"
                "[邀請機器人](https://discord.com/application-directory/1126517167966396436)．"
                "[Discord TW](https://discordservers.tw/bots/1126517167966396436)"
            ),
            image="https://raw.githubusercontent.com/HansHans135/bopomofo/main/example.gif",
        )

        await ctx.respond(embed=embed)

    @discord.slash_command(name="info", description="機器人資訊")
    async def info(self, ctx: discord.ApplicationContext) -> None:
        """
        The slash command to show the bot information.
        """
        await ctx.defer()

        times = await self.db.get_info("translated_count")
        embed = discord.Embed(
            title="機器人資訊",
            description=(
                # fmt: off
                f"　群組數量：{len(self.bot.guilds):,}\n"
                f"使用者數量：{len(self.bot.users):,}\n"
                f"總翻譯數量：{int(times):,}"
                # fmt: on
            ),
        )
        await ctx.respond(embed=embed)


def setup(client: discord.AutoShardedBot) -> None:
    """
    The setup function of the cog.
    """
    client.add_cog(InfoCog(client))
