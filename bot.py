import os
import json
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


async def translate(string: str) -> str | None:
    string = string.replace(" ", "=")
    url_string = urllib.parse.quote(string)
    async with aiohttp.request(
        "GET",
        f"https://www.google.com/inputtools/request?text={url_string}&ime=zh-hant-t-i0&cb=?",  # noqa
    ) as response:
        text = await response.text()

    result_list = json.loads(text)[1][0][1]
    if result_list:
        return result_list[0]

    return None


@bot.message_command(name="精靈文翻譯")
async def translate_command(
    ctx: discord.ApplicationContext,
    message: discord.Message,
):
    result = await translate(message.content)
    if not result:
        return await ctx.respond("無法翻譯此訊息，請見諒", ephemeral=True)

    embed = discord.Embed(
        title="精靈文翻譯結果:",
        description=f"```{message.content}```⬇️```{result}```",
    )
    embed.set_author(
        name=message.author.name,
        icon_url=message.author.avatar.url,
    )
    await ctx.respond(embed=embed)

if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
