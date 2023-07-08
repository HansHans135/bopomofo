import discord
import requests

intents = discord.Intents.default()
intents.messages = True

bot = discord.Bot()


@bot.event
async def on_ready():
    print('Bot is ready')


@bot.slash_command(name="help", description="幫助選單")
async def help(ctx: discord.ApplicationContext):
    embed = discord.Embed(title="如何使用", description="""想想看你在聊天的時候看到`su3cl3`
會想到他一定是忘記切輸入法吧
現在透過機器人可以直接翻譯對話""")
    embed.add_field(name="但現在有點小毛病",value="不支援部分的一聲(空格)")
    embed.add_field(name="機器人原始碼",value="[github](https://github.com/HansHans135/bopomofo/)")
    embed.set_image(
        url="https://raw.githubusercontent.com/HansHans135/bopomofo/main/how_use.gif")
    
    await ctx.respond(embed=embed)


@bot.message_command(name="翻譯")
async def get_message_id(ctx, message: discord.Message):
    try:
        rt=""
        text=message.content.split(" ")
        for i in text:
            if i!=text[-1]:
                i+="%20"
            a = requests.get(
            f"https://www.google.com/inputtools/request?text={i}&ime=zh-hant-t-i0&cb=?")
            rt+=eval(a.text)[1][0][1][0]    
        await ctx.respond(f"**{message.author.name}** : `{message.content}` --> {rt}")
        print(f"{message.content} --> {rt}")
    except:
        a = requests.get(
            f"https://www.google.com/inputtools/request?text={message.content}&ime=zh-hant-t-i0&cb=?")
        await ctx.respond(f"你確定這是可以翻譯的?\n`{a.text}`", ephemeral=True)
    

bot.run('')
