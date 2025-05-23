import config
import asyncio
import discord
import subprocess

from garfpy import(
    logger, is_private,
    kroger_token, find_store, search_product,
    picture_time, process_image_requests, generate_chat,
    aod_message, wikisum)


gapikey = config.GIF_TOKEN
garfkey = config.GARFBOT_TOKEN
txtmodel = config.TXT_MODEL
imgmodel = config.IMG_MODEL

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
garfbot = discord.Client(intents=intents)


@garfbot.event
async def on_ready():
    try:
        asyncio.create_task(process_image_requests())
        logger.info(f"Logged in as {garfbot.user.name} running {txtmodel} and {imgmodel}.")
    except Exception as e:
        logger.error(e)


@garfbot.event
async def on_message(message):
    if message.author == garfbot.user:
        return

    if message.content.lower().startswith("hey garfield") or isinstance(message.channel, discord.DMChannel):
        question = message.content[12:] if message.content.lower().startswith("hey garfield") else message.content
        answer = await generate_chat(question)
        logger.info(f"Chat Request - User: {user}, Server: {server}, Prompt: {question}")
        await message.channel.send(answer)

    if message.content.lower().startswith('garfpic '):
        user = message.author.name
        server = message.guild.name if message.guild else "Direct Message"
        prompt = message.content[8:]
        logger.info(f"Image Request - User: {user}, Server: {server}, Prompt: {prompt}")
        await message.channel.send(f"`Please wait... image generation queued: {prompt}`")
        await picture_time(message, prompt)

    if message.content.lower().startswith('garfwiki '):
        search_term = message.content[9:]
        summary = await wikisum(search_term)
        await message.channel.send(summary)

    if message.content.lower().startswith("garfping "):
        try:
            query = message.content.split()
            user = message.author.name
            server = message.guild.name if message.guild else "Direct Message"
            target = query[-1]
            logger.info(f"Ping Request - User: {user}, Server: {server}, Target: {target}")
            if is_private(target):
                rejection = await generate_chat("Hey Garfield, explain to me why I am dumb for trying to hack your private computer network.")
                await message.channel.send(rejection)
            else:
                result = subprocess.run(['ping', '-c', '4', target], capture_output=True, text=True)
                await message.channel.send(f"`Ping result for {target}:`\n```\n{result.stdout}\n```")
        except Exception as e:
            await message.channel.send(f"`GarfBot Error: {str(e)}`")

    if message.content.lower().startswith("garfdns "):
        try:
            query = message.content.split()
            user = message.author.name
            server = message.guild.name if message.guild else "Direct Message"
            target = query[-1]
            logger.info(f"NSLookup Request - User: {user}, Server: {server}, Target: {target}")
            if is_private(target):
                rejection = await generate_chat("Hey Garfield, explain to me why I am dumb for trying to hack your private computer network.")
                await message.channel.send(rejection)
            else:
                result = subprocess.run(['nslookup', target], capture_output=True, text=True)
                await message.channel.send(f"`NSLookup result for {target}:`\n```\n{result.stdout}\n```")
        except Exception as e:
            await message.channel.send(f"`GarfBot Error: {str(e)}`")

    if message.content.lower().startswith("garfhack "):
        try:
            query = message.content.split()
            user = message.author.name
            server = message.guild.name if message.guild else "Direct Message"
            target = query[-1]
            logger.info(f"Nmap Request - User: {user}, Server: {server}, Target: {target}")
            if is_private(target):
                rejection = await generate_chat("Hey Garfield, explain to me why I am dumb for trying to hack your private computer network.")
                await message.channel.send(rejection)
            else:
                await message.channel.send(f"`Scanning {target}...`")
                result = subprocess.run(['nmap', '-Pn', '-O', '-v', target], capture_output=True, text=True)
                await message.channel.send(f"`Ping result for {target}:`\n```\n{result.stdout}\n```")
        except Exception as e:
            await message.channel.send(f"`GarfBot Error: {str(e)}`")

    # Kroger Shopping
    if message.content.lower().startswith("garfshop "):
        try:
            kroken = kroger_token()
            kroger_query = message.content.split()
            product = " ".join(kroger_query[1:-1])
            zipcode = kroger_query[-1]
            loc_data = find_store(zipcode, kroken)
            loc_id = loc_data['data'][0]['locationId']
            store_name = loc_data['data'][0]['name']
            product_query = search_product(product, loc_id, kroken)
            products = product_query['data']
            sorted_products = sorted(products, key=lambda item: item['items'][0]['price']['regular'])
            response = f"Prices for `{product}` at `{store_name}` near `{zipcode}`:\n"
            for item in sorted_products:
                product_name = item['description']
                price = item['items'][0]['price']['regular']
                response += f"- `${price}`: {product_name} \n"
            await message.channel.send(response)
        except Exception as e:
            await message.channel.send(f"`GarfBot Error: {str(e)}`")

    # Army of Dawn Server only!!
    if message.guild and message.guild.id == 719605634772893757:

        await aod_message(garfbot, message)


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
