"""
Cog module for the translate commands.
"""

import re
from urllib.parse import quote

import aiohttp
import discord
import discord.ui as UI

from ..main import BaseCog

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


class TranslateCog(BaseCog):
    """
    The cog class for the translate commands.
    """

    re_replace_space = re.compile(r" +")

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

        # get cache from local datebase
        result = await self.db.get_translate(message.content)
        if result is None:
            # fetch result from google API
            result = "=".join(
                filter(None, [await self.translate(substr) for substr in message.content.split("=")])
            )

        if not result:
            await ctx.respond("無法翻譯此訊息，可能是拼字有誤。")
            return

        embed = discord.Embed(
            title="精靈文翻譯",
            description=result,
            color=0x2B2D31,
            timestamp=message.created_at,
        )
        embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
        if message.guild:
            embed.set_footer(text=message.channel.name)

        await ctx.respond(embed=embed, view=UI.View(UI.Button(label="跳至原始訊息", url=message.jump_url)))

        await self.db.insert_translate(message.content, result)

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        guess = await self.db.get_translate(message.content)
        if guess is None:
            return
            
        count = await self.db.get_translate_count(message.content)
        if count is None or count < 3:
            return
            
        embed = discord.Embed(title="你是不是想說：", description=guess, color=0x2B2D31)
        embed.set_author(name="精靈文翻譯系統")
        await message.reply(embed=embed, mention_author=False, view=DeleteMessageUI(message))


def setup(client: discord.AutoShardedBot) -> None:
    """
    The setup function of the cog.
    """
    client.add_cog(TranslateCog(client))


class DeleteMessageUI(UI.View):
    def __init__(self, message: discord.Message):
        super().__init__(timeout=60)
        self.orignial_message = message

    @UI.button(label="不，我並沒有這個意思", custom_id="button:delete_message", style=discord.ButtonStyle.red)
    async def delete_message(self, _: UI.Button, interaction: discord.Interaction):
        if interaction.user != self.orignial_message.author:
            await interaction.respond("你不能使用這顆按鈕。", ephemeral=True)
            return
        await interaction.message.delete()
        self.stop()

    # TODO: report systme
    # @UI.button(label="回報問題", custom_id="button:report")
    # async def report(self, _: UI.Button, interaction: discord.Interaction): ...

    async def on_timeout(self) -> None:
        await self.message.edit(view=None)
