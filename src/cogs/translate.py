"""
Cog module for the translate commands.
"""

from urllib.parse import quote

import aiohttp
import discord
from discord.ext import commands


class Translate(commands.Cog):
    """
    The cog class for the translate commands.
    """

    def __init__(self, client: discord.AutoShardedBot) -> None:
        self.client = client

    async def translate(self, string: str) -> str:
        """
        Translate the bopomofo string to Chinese.

        :param string: The bopomofo string.
        :type string: str

        :return: The translated string.
        :rtype: str
        """
        if (not string) or string == "=":
            return ""

        string = string.replace(" ", "=")
        if string[0] == "=":
            string = f" {string[1:]}"
        text = quote(string)

        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"https://www.google.com/inputtools/request?text={text}=&ime=zh-hant-t-i0&cb=?"
            ) as r:
                data = await r.json()
                result = data[1][0]

        if not result[1]:
            return string
        if match_len := result[3].get("matched_length"):
            return result[1][0] + (await self.translate(string[match_len[0] :]) or "")
        return result[1][0]

    @discord.message_command(name="精靈文翻譯")
    async def translate_command(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ) -> None:
        """
        The message command to translate the message to Chinese.

        :param ctx: The context of the message command.
        :type ctx: discord.ApplicationContext
        :param message: The message to translate.
        :type message: discord.Message
        """
        await ctx.defer()

        result = "=".join(
            filter(None, [await self.translate(substr) for substr in message.content.split("=")])
        )

        if not result:
            await ctx.respond("無法翻譯此訊息，可能是拼字有誤。")
            return

        embed = discord.Embed(
            title="精靈文翻譯結果:",
            description=f"原始訊息位置: {message.jump_url}\n{message.content}\n⬇️\n{result}",
        ).set_author(name=message.author.name, icon_url=message.author.avatar.url)
        await ctx.respond(embed=embed)


def setup(client: discord.AutoShardedBot) -> None:
    """
    The setup function of the cog.
    """
    client.add_cog(Translate(client))
