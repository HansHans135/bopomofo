"""
Cog module for the translate commands.
"""

import re
import sqlite3
from urllib.parse import quote

import aiohttp
import discord
import discord.ui as UI
from discord.ext import commands

BOPOMOFO = {
    "ㄅ": "1",
    "ㄆ": "q",
    "ㄇ": "a",
    "ㄈ": "z",
    "ㄉ": "2",
    "ㄊ": "w",
    "ㄋ": "s",
    "ㄌ": "x",
    "ㄍ": "e",
    "ㄎ": "d",
    "ㄏ": "c",
    "ㄐ": "r",
    "ㄑ": "f",
    "ㄒ": "v",
    "ㄓ": "5",
    "ㄔ": "t",
    "ㄕ": "g",
    "ㄖ": "b",
    "ㄗ": "y",
    "ㄘ": "h",
    "ㄙ": "n",
    "ㄧ": "u",
    "ㄨ": "j",
    "ㄩ": "m",
    "ㄚ": "8",
    "ㄛ": "i",
    "ㄜ": "k",
    "ㄝ": ",",
    "ㄞ": "9",
    "ㄟ": "o",
    "ㄠ": "l",
    "ㄡ": ".",
    "ㄢ": "0",
    "ㄣ": "p",
    "ㄤ": ";",
    "ㄥ": "/",
    "ㄦ": "-",
    "ˇ": "3",
    "ˋ": "4",
    "ˊ": "6",
    "˙": "7",
}


def bopomofo_to_eng(msg: str):
    for k, v in BOPOMOFO.items():
        msg = msg.replace(k, v)
    return msg


class TranslateCog(commands.Cog):
    """
    The cog class for the translate commands.
    """

    def __init__(self, client: discord.AutoShardedBot) -> None:
        self.client = client
        self.re_replace_space = re.compile(r" +")

    def _replace_space(self, match: re.Match) -> str:
        """
        Replace the first space in multiple consecutive spaces with "=".
        """
        return f"={match.group(0)[1:]}"

    async def translate(self, string: str) -> str:
        """
        Translate the bopomofo string to Chinese.

        :param string: The bopomofo string.
        :type string: str

        :return: The translated string.
        :rtype: str
        """
        string = bopomofo_to_eng(string)
        if (not string) or string == "=":
            return ""

        string_ = re.sub(self.re_replace_space, self._replace_space, string)
        if string[0] == " ":
            string_ = f" {string_[1:]}"
        text = quote(string_)

        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"https://www.google.com/inputtools/request?text={text}=&ime=zh-hant-t-i0&cb=?"
            ) as r:
                data = await r.json()
                result = data[1][0]

        if not result[1]:
            return string
        if match_len := result[3].get("matched_length"):
            return f"{result[1][0]}{await self.translate(string[match_len[0]:]) or ''}"
        return result[1][0]

    @discord.message_command(
        name="精靈文翻譯",
        integration_types={discord.IntegrationType.guild_install, discord.IntegrationType.user_install},
    )
    async def translate_command(self, ctx: discord.ApplicationContext, message: discord.Message) -> None:
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
            title="精靈文翻譯",
            description=result,
            timestamp=message.created_at,
        )
        embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
        embed.set_footer(text=message.channel.name)

        await ctx.respond(embed=embed, view=UI.View(UI.Button(label="跳至原始訊息", url=message.jump_url)))
        return
        # TODO: transalte data db
        with sqlite3.connect("data.db") as db:
            db_date = db.execute("SELECT * FROM translate")
            data = {}
            for befor, after in db_date.fetchall():
                data[befor] = after
            if message.content not in data:
                db.execute(
                    f"""
    INSERT INTO translate VALUES
        ('{message.content}','{result}')
        """
                )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        return
        if message.author == self.client.user:
            return
        # TODO: transalte data db
        with sqlite3.connect("data.db") as db:
            db_date = db.execute("SELECT * FROM translate")
        data = {}
        for befor, after in db_date.fetchall():
            data[befor] = after
        if message.content in data:
            await message.channel.send(f"你是不是想說:`{data[message.content]}`")


def setup(client: discord.AutoShardedBot) -> None:
    """
    The setup function of the cog.
    """
    client.add_cog(TranslateCog(client))
