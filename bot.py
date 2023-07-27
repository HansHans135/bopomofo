import os
import urllib.parse

import aiohttp
import discord
from dotenv import load_dotenv

load_dotenv()

intents: discord.Intents = discord.Intents.default()

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready() -> None:
    print(f"Login as {bot.user}")


@bot.slash_command()
async def help(ctx: discord.ApplicationContext) -> None:
    """幫助選單"""
    embed = discord.Embed(
        title="如何使用",
        description="想想看當你在聊天的時候看到`su3cl3`\n你會認為他是忘記切輸入法吧？\n現在，透過機器人直接翻譯對話吧！",  # noqa
    )
    embed.add_field(
        name="機器人原始碼",
        value="[GitHub](https://github.com/HansHans135/bopomofo/)",
    )
    embed.set_image(
        url="https://raw.githubusercontent.com/HansHans135/bopomofo/main/demo.gif"
    )  # noqa

    await ctx.respond(embed=embed)


async def translate(string: str) -> (str | None):
    if (not string) or string == "=":
        return None
    url_string = urllib.parse.quote(
        (
            (" " + string[1:].replace(" ", "="))
            if string[0] == " "
            else string.replace(" ", "=")
        )
        + "="
    )
    async with aiohttp.request(
        "GET",
        f"https://www.google.com/inputtools/request?text={url_string}&ime=zh-hant-t-i0&cb=?",  # noqa
    ) as response:
        result = (await response.json())[1][0]
        jresult: dict = result[3]

    if not result[1]:
        return string

    if match_len := jresult.get("matched_length"):
        return result[1][0] + (await translate(string[match_len[0] :]) or "")

    return result[1][0]


@bot.message_command(name="精靈文翻譯")
async def translate_command(
    ctx: discord.ApplicationContext,
    message: discord.Message,
) -> discord.Interaction | discord.WebhookMessage | None:
    result = "=".join(
        filter(None, [await translate(substr) for substr in message.content.split("=")])
    )  # noqa
    if not result:
        return await ctx.respond("無法翻譯此訊息，可能是拼字有誤。", ephemeral=True)

    embed = discord.Embed(
        title="精靈文翻譯結果:",
        description=f"From: {message.jump_url}\n{message.content}\n⬇️\n{result}",  # noqa
    )
    embed.set_author(
        name=message.author.name,
        icon_url=message.author.avatar.url,
    )
    await ctx.respond(embed=embed)


if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
