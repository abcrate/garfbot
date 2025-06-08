import config
import asyncio
import discord
from discord.ext import commands

from garfpy import (
    help,
    logger,
    IPUtils,
    aod_message,
    generate_qr,
    Kroger,
    GarfAI,
    GarfbotRespond,
    WeatherAPI,
)


gapikey = config.GIF_TOKEN
garfkey = config.GARFBOT_TOKEN
txtmodel = config.TXT_MODEL
imgmodel = config.IMG_MODEL

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

garfbot = commands.Bot(command_prefix=["Garfbot ", "garfbot ","Garf", "garf", "$"], intents=intents)
garfbot.remove_command("help")

garf_respond = GarfbotRespond()
garfield = GarfAI()
iputils = IPUtils()
kroger = Kroger()
weather = WeatherAPI()


@garfbot.event
async def on_ready():
    try:
        garf_respond.load_responses()
        asyncio.create_task(garfield.process_image_requests())
        logger.info(
            f"Logged in as {garfbot.user.name} running {txtmodel} and {imgmodel}."  # type: ignore
        )
    except Exception as e:
        logger.error(e)


@garfbot.command(name="ping")
async def garfbot_ping(ctx, *, target):
    """Ping a target"""
    logger.info(
        f"Ping Request - User: {ctx.author.name}, Server: {ctx.guild.name}, Target: {target}"
    )
    await iputils.ping(ctx, target)


@garfbot.command(name="dns")
async def garfbot_dns(ctx, *, target):
    """DNS lookup for a target"""
    logger.info(
        f"NSLookup Request - User: {ctx.author.name}, Server: {ctx.guild.name}, Target: {target}"
    )
    await iputils.dns(ctx, target)


@garfbot.command(name="hack")
async def garfbot_hack(ctx, *, target):
    """Nmap scan a target"""
    logger.info(
        f"Nmap Request - User: {ctx.author.name}, Server: {ctx.guild.name}, Target: {target}"
    )
    await iputils.scan(ctx, target)


@garfbot.command(name="qr")
async def garfbot_qr(ctx, *, text):
    logger.info(
        f"QR Code Request - User: {ctx.author.name}, Server: {ctx.guild.name}, Text: {text}"
    )
    if len(text) > 1000:
        await ctx.send("❌ Text too long! Maximum 1000 characters.")
    else:
        try:
            qr_code = await generate_qr(text)
            sendfile = discord.File(fp=qr_code, filename="qrcode.png")
            await ctx.send(file=sendfile)
        except Exception as e:
            logger.error(e)
            await ctx.send(e)


@garfbot.command(name="wiki")
async def garfbot_wiki(ctx, *, query):
    summary = await garfield.wikisum(query)
    await ctx.send(summary)


@garfbot.command(name="shop")
async def garfbot_shop(ctx, *, query):
    try:
        response = kroger.garfshop(query)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"`GarfBot Error: {str(e)}`")


@garfbot.command(name="weather")
async def garfbot_weather(ctx, *, location):
    await weather.weather(ctx, location)


@garfbot.command(name="chat")
async def garfchat(ctx, *, prompt):
    answer = await garfield.generate_chat(prompt)
    logger.info(
        f"Chat Request - User: {ctx.author.name}, Server: {ctx.guild.name}, Prompt: {prompt}"
    )
    await ctx.send(answer)


@garfbot.command(name="pic")
async def garfpic(ctx, *, prompt):
    logger.info(
        f"Image Request - User: {ctx.author.name}, Server: {ctx.guild.name}, Prompt: {prompt}"
    )
    await ctx.send(f"`Please wait... image generation queued: {prompt}`")
    await garfield.garfpic(ctx, prompt)


@garfbot.command(name="help")
async def garfbot_help(ctx):
    if ctx:
        await help(ctx)


@garfbot.event
async def on_message(message):
    if message.author == garfbot.user:
        return

    content = message.content.strip()
    lower = content.lower()

    # Chats & pics
    if lower.startswith("hey garfield") or isinstance(
        message.channel, discord.DMChannel
    ):
        ctx = await garfbot.get_context(message)
        await garfchat(ctx, prompt=content)

    # Auto-responses
    elif message.guild:
        guild_id = message.guild.id

        # Army of Dawn Server only!!
        if guild_id == 719605634772893757:
            await aod_message(garfbot, message)

        responses = garf_respond.get_responses(guild_id)

        if lower.startswith("garfbot response "):
            await garf_respond.garfbot_response(message, content)
            return

        for trigger, response in responses.items():
            if trigger.lower() in lower:
                await message.channel.send(response)
                break

    await garfbot.process_commands(message)


# Run GarfBot
async def garfbot_connect():
    while True:
        try:
            await garfbot.start(garfkey)
        except Exception as e:
            e = str(e)
            logger.error(f"Garfbot couldn't connect! {e}")
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(garfbot_connect())
