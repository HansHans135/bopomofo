import os
import urllib.parse

import discord
import aiohttp

from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Login as {bot.user}")


@bot.slash_command(name="help", description="幫助選單")
async def help(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="如何使用",
        description="想想看當你在聊天的時候看到`su3cl3`\n你會認為他是忘記切輸入法吧？\n現在，透過機器人直接翻譯對話吧！",  # noqa
    )
    embed.add_field(
        name="機器人原始碼",
        value="[GitHub](https://github.com/HansHans135/bopomofo/)",
    )
    embed.set_image(url="https://raw.githubusercontent.com/HansHans135/bopomofo/main/how_use.gif")  # noqa

    await ctx.respond(embed=embed)


async def translate(string: str, space_at_end: bool = False) -> str | None:
    if space_at_end:
        string += "="
    url_string = urllib.parse.quote(string.replace(" ", "="))
    async with aiohttp.request(
        "GET",
        f"https://www.google.com/inputtools/request?text={url_string}&ime=zh-hant-t-i0&cb=?",  # noqa
    ) as response:
        result = await response.json()

    if not result[1][0][1]:
        return None
    if result[1][0][3].get("matched_length") and not space_at_end:
        return await translate(string, True)

    return result[1][0][1][0]


@bot.message_command(name="精靈文翻譯")
async def translate_command(
    ctx: discord.ApplicationContext,
    message: discord.Message,
):
    result = await translate(message.content)
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
