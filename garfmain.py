import config
import asyncio
import discord

from garfpy import (
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
garfbot = discord.Client(intents=intents)

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
            f"Logged in as {garfbot.user.name} running {txtmodel} and {imgmodel}."
        )
    except Exception as e:
        logger.error(e)


@garfbot.event
async def on_message(message):
    if message.author == garfbot.user:
        return

    content = message.content.strip()
    lower = content.lower()
    user_name = message.author.name
    guild_id = message.guild.id
    guild_name = message.guild.name if message.guild else "Direct Message"

    # IP utils
    if message.guild and lower.startswith(("garfping ", "garfdns ", "garfhack ")):
        await iputils.scan(message, user_name, guild_name, lower)

    # Wikipedia
    if lower.startswith("garfwiki "):
        query = message.content[9:]
        summary = await garfield.wikisum(query)
        await message.channel.send(summary)

    # QR codes
    if lower.startswith("garfqr "):
        text = message.content[7:]
        if len(text) > 1000:
            await message.channel.send("❌ Text too long! Maximum 1000 characters.")
        else:
            try:
                qr_code = await generate_qr(text)
                sendfile = discord.File(fp=qr_code, filename="qrcode.png")
                await message.channel.send(file=sendfile)
            except Exception as e:
                logger.error(e)
                await message.channel.send(e)

    # Kroger Shopping
    if lower.startswith("garfshop "):
        try:
            query = message.content[9:]
            response = kroger.garfshop(query)
            await message.channel.send(response)
        except Exception as e:
            await message.channel.send(f"`GarfBot Error: {str(e)}`")

    # Chats & pics
    elif lower.startswith("hey garfield") or isinstance(
        message.channel, discord.DMChannel
    ):
        prompt = content[12:] if lower.startswith("hey garfield") else message.content
        answer = await garfield.generate_chat(prompt)
        logger.info(
            f"Chat Request - User: {user_name}, Server: {guild_name}, Prompt: {prompt}"
        )
        await message.channel.send(answer)

    elif lower.startswith("garfpic "):
        prompt = content[8:]
        logger.info(
            f"Image Request - User: {user_name}, Server: {guild_name}, Prompt: {prompt}"
        )
        await message.channel.send(
            f"`Please wait... image generation queued: {prompt}`"
        )
        await garfield.garfpic(message, prompt)

    # Weather
    elif lower.startswith("garfbot weather "):
        location = lower[16:]
        embed = await weather.weather(location)
        await message.channel.send(embed=embed)

    # GarfBot help
    elif lower.strip() == "garfbot help":
        embed = discord.Embed(title="**Need help?**", color=0x4D4D4D)
        embed.add_field(
            name="hey garfield `prompt`", value="*Responds with text.*", inline=True
        )
        embed.add_field(
            name="garfpic `prompt`", value="*Responds with an image.*", inline=True
        )
        embed.add_field(
            name="garfping `target`",
            value="*Responds with iputils-ping result from target.*",
            inline=True,
        )
        embed.add_field(
            name="garfdns `target`",
            value="*Responds with dns lookup result from target.*",
            inline=True,
        )
        embed.add_field(
            name="garfhack `target`",
            value="*Responds with nmap scan result from target.*",
            inline=True,
        )
        embed.add_field(
            name="garfwiki `query`",
            value="*Garfbot looks up a wikipedia article and will summarize it for you.*",
            inline=True,
        )
        embed.add_field(
            name="garfshop `item` `zip`",
            value="*Responds with 10 grocery items from the nearest Kroger location, cheapest first.*",
            inline=True,
        )
        embed.add_field(
            name="garfqr `text`",
            value="*Create a QR code for any string up to 1000 characters.*",
            inline=True,
        )
        embed.add_field(
            name="garfbot response `add` `trigger` `response`",
            value='*Add a GarfBot auto response for your server. Use "quotes" if you like.*',
            inline=True,
        )
        embed.add_field(
            name="garfbot response `remove` `trigger`",
            value="*Remove a GarfBot auto response for your server.*",
            inline=True,
        )
        embed.add_field(
            name="garfbot response `list`",
            value="*List current GarfBot auto responses for your server.*",
            inline=True,
        )
        embed.add_field(
            name="garfbot help", value="*Show a list of these commands.*", inline=True
        )
        await message.channel.send(embed=embed)

    # Army of Dawn Server only!!
    elif message.guild and message.guild.id == 719605634772893757:
        await aod_message(garfbot, message)

    # Auto-responses
    elif message.guild:
        responses = garf_respond.get_responses(guild_id)

        if lower.startswith("garfbot response "):
            await garf_respond.garfbot_response(message, content)
            return

        for trigger, response in responses.items():
            if trigger.lower() in lower:
                await message.channel.send(response)
                break


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
