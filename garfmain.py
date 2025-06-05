import config
import asyncio
import discord
import subprocess

from garfpy import(
    logger, is_private,
    aod_message, generate_qr,
    Kroger, GarfAI, GarfbotRespond)


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
kroger = Kroger()


@garfbot.event
async def on_ready():
    try:
        garf_respond.load_responses()
        asyncio.create_task(garfield.process_image_requests())
        logger.info(f"Logged in as {garfbot.user.name} running {txtmodel} and {imgmodel}.")
    except Exception as e:
        logger.error(e)


@garfbot.event
async def on_message(message):

    content = message.content.strip()
    lower = content.lower()
    user = message.author.name
    guild = message.guild.name if message.guild else "Direct Message"
    guild_id = message.guild.id

    # Chats & pics
    if message.author == garfbot.user:
        return

    if lower.startswith("hey garfield") or isinstance(message.channel, discord.DMChannel):
        prompt = content[12:] if lower.startswith("hey garfield") else message.content
        answer = await garfield.generate_chat(prompt)
        logger.info(f"Chat Request - User: {user}, Server: {guild}, Prompt: {prompt}")
        await message.channel.send(answer)

    if lower.startswith('garfpic '):
        prompt = content[8:]
        logger.info(f"Image Request - User: {user}, Server: {guild}, Prompt: {prompt}")
        await message.channel.send(f"`Please wait... image generation queued: {prompt}`")
        await garfield.garfpic(message, prompt)

    # Wikipedia
    if lower.startswith('garfwiki '):
        query = message.content[9:]
        summary = await garfield.wikisum(query)
        await message.channel.send(summary)

    # QR codes
    if lower.startswith('garfqr '):
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

    # IP utils
    query = message.content.split()
    target = query[-1]

    if lower.startswith("garfping "):
        try:
            logger.info(f"Ping Request - User: {user}, Server: {guild}, Target: {target}")
            if is_private(target):
                rejection = await garfield.generate_chat("Hey Garfield, explain to me why I am dumb for trying to hack your private computer network.")
                await message.channel.send(rejection)
            else:
                result = subprocess.run(['ping', '-c', '4', target], capture_output=True, text=True)
                await message.channel.send(f"`Ping result for {target}:`\n```\n{result.stdout}\n```")
        except Exception as e:
            await message.channel.send(f"`GarfBot Error: {str(e)}`")

    if lower.startswith("garfdns "):
        try:
            logger.info(f"NSLookup Request - User: {user}, Server: {guild}, Target: {target}")
            if is_private(target):
                rejection = await garfield.generate_chat("Hey Garfield, explain to me why I am dumb for trying to hack your private computer network.")
                await message.channel.send(rejection)
            else:
                result = subprocess.run(['nslookup', target], capture_output=True, text=True)
                await message.channel.send(f"`NSLookup result for {target}:`\n```\n{result.stdout}\n```")
        except Exception as e:
            await message.channel.send(f"`GarfBot Error: {str(e)}`")

    if lower.startswith("garfhack "):
        try:
            logger.info(f"Nmap Request - User: {user}, Server: {guild}, Target: {target}")
            if is_private(target):
                rejection = await garfield.generate_chat("Hey Garfield, explain to me why I am dumb for trying to hack your private computer network.")
                await message.channel.send(rejection)
            else:
                await message.channel.send(f"`Scanning {target}...`")
                result = subprocess.run(['nmap', '-Pn', '-O', '-v', target], capture_output=True, text=True)
                await message.channel.send(f"`Ping result for {target}:`\n```\n{result.stdout}\n```")
        except Exception as e:
            await message.channel.send(f"`GarfBot Error: {str(e)}`")

    # Kroger Shopping
    if lower.startswith("garfshop "):
        try:
            query = message.content[9:]
            response = kroger.garfshop(query)
            await message.channel.send(response)
        except Exception as e:
            await message.channel.send(f"`GarfBot Error: {str(e)}`")

    # Army of Dawn Server only!!
    if message.guild and message.guild.id == 719605634772893757:
        await aod_message(garfbot, message)

    # Auto-responses
    if message.guild:
        responses = garf_respond.get_responses(guild_id)
        
        if lower.startswith('garfbot response '):
            await garf_respond.garfbot_response(message, content)
            return
            
        for trigger, response in responses.items():
            if trigger.lower() in lower:
                await message.channel.send(response)
                break

# Run Garfbot
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
