import os
import json
import config
import random
import openai
import logging
import aiohttp
import asyncio
import discord
import requests
import ipaddress
import subprocess
from base64 import b64encode
from openai import AsyncOpenAI
from datetime import datetime
from collections import defaultdict
from operator import itemgetter
from logging.handlers import TimedRotatingFileHandler


# Log Setup
logger = logging.getLogger('garflog')
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler(
    'garfbot.log',
    when='midnight',
    interval=1,
    backupCount=7,
    delay=True # Flush output immediately
    )
formatter=logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )
handler.setFormatter(formatter)
logger.addHandler(handler)


# Bot Setup
openaikey = config.OPENAI_TOKEN
gapikey = config.GIF_TOKEN
garfkey = config.GARFBOT_TOKEN
txtmodel = "gpt-4o-mini"
imgmodel = "dall-e-3"

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
garfbot = discord.Client(intents=intents)


# Network Utils Setup
def is_private(target):
    try:
        ip_obj = ipaddress.ip_address(target)
        if ip_obj.is_private:
            return True
    except ValueError:
        if "crate.lan" in target.lower():
            return True
        if "crate.zip" in target.lower():
            return True
        if "memtec.org" in target.lower():
            return True
        if "crateit.net" in target.lower():
            return True
        if "garfbot.art" in target.lower():
            return True
    return False


# Kroger Setup
client_id = config.CLIENT_ID
client_secret = config.CLIENT_SECRET

auth = b64encode(f"{client_id}:{client_secret}".encode()).decode()

def kroger_token():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {auth}'
    }
    
    response = requests.post('https://api.kroger.com/v1/connect/oauth2/token', headers=headers, data={
        'grant_type': 'client_credentials',
        'scope': 'product.compact'
    })

    response.raise_for_status()
    return response.json()['access_token']

def find_store(zipcode, kroken):
    headers = {
        'Authorization': f'Bearer {kroken}',
    }
    params = {
        'filter.zipCode.near': zipcode,
        'filter.limit': 1,
    }
    response = requests.get('https://api.kroger.com/v1/locations', headers=headers, params=params)
    return response.json()

def search_product(product, loc_id, kroken):
    headers = {
        'Authorization': f'Bearer {kroken}',
    }
    params = {
        'filter.term': product,
        'filter.locationId': loc_id,
        'filter.limit': 10
    }
    response = requests.get('https://api.kroger.com/v1/products', headers=headers, params=params)
    return response.json()


# Meows Json Handling
meows_file = "meow_counts.json"
stats_file = "user_stats.json"

def json_load(file_path, default):
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        return default

meow_counts = defaultdict(int, json_load(meows_file, {}))
user_stats = json_load(stats_file, {})


# GarfBot Ready!
@garfbot.event
async def on_ready():
    asyncio.create_task(process_image_requests()) # Important!
    logger.info(f"Logged in as {garfbot.user.name} running {txtmodel} and {imgmodel}.")
    print(f"Logged in as {garfbot.user.name} running {txtmodel} and {imgmodel}.", flush=True)


# GarfChats
async def generate_chat_response(question):
    try:
        client = AsyncOpenAI(api_key = openaikey)
        response = await client.chat.completions.create(
            model=txtmodel,
            messages=[
            	{"role": "system", "content": "Pretend you are sarcastic Garfield."},
            	{"role": "user", "content": f"{question}"}
            ],
            max_tokens=400
        )
        answer = response.choices[0].message.content
        return answer.replace("an AI language model", "a cartoon animal")
    except openai.BadRequestError as e:
        return f"`GarfBot Error: {e}`"
    except openai.APIError as e:
        print(e, flush=True)
        return f"`GarfBot Error: Monday`"
    except Exception as e:
        print(e, flush=True)
        return f"`GarfBot Error: Lasagna`"


# GarfPics
async def generate_image(prompt):
    try:
        client = AsyncOpenAI(api_key = openaikey)
        response = await client.images.generate(
            model=imgmodel,
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        return image_url
    except openai.BadRequestError as e:
        return f"`GarfBot Error: ({e.status_code}) - Your request was rejected as a product_query of our safety system.`"
    except openai.InternalServerError as e:
        logger.error(e)
        print(e, flush=True)
        return f"`GarfBot Error: ({e.status_code}) - Monday`"
    except Exception as e:
        logger.error(e)
        print(e, flush=True)
        return f"`GarfBot Error: Lasagna`"

image_request_queue = asyncio.Queue()

async def process_image_requests():
    async with aiohttp.ClientSession() as session:
        while True:
            request = await image_request_queue.get()
            message = request['message']
            prompt = request['prompt']
            image_url = await generate_image(prompt)
            if "GarfBot Error" not in image_url:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        timestamp = message.created_at.strftime('%Y%m%d%H%M%S')
                        save_filename = f"images/{timestamp}_generated_image.png"
                        send_filename = f"{timestamp}_generated_image.png" # There is probably a better way to do this.
                        with open(save_filename, "wb") as f:
                            f.write(image_data)
                        with open(save_filename, "rb") as f:
                            await message.channel.send(file=discord.File(f, send_filename))
                    else:
                        await message.channel.send("`GarfBot Error: Odie`")
            else:
                await message.channel.send(image_url)
            image_request_queue.task_done()
            await asyncio.sleep(2)


# Message Listener
@garfbot.event
async def on_message(message):
    if message.author == garfbot.user:
        return

    if message.content.lower().startswith("hey garfield") or isinstance(message.channel, discord.DMChannel):
        question = message.content[12:] if message.content.lower().startswith("hey garfield") else message.content
        answer = await generate_chat_response(question)
        await message.channel.send(answer)

    if message.content.lower().startswith('garfpic '):
        user = message.author.name
        server = message.guild.name if message.guild else "Direct Message"
        prompt = message.content[8:]
        logger.info(f"Image Request - User: {user}, Server: {server}, Prompt: {prompt}")
        print(f"Image Request - User: {user}, Server: {server}, Prompt: {prompt}", flush=True)
        await message.channel.send(f"`Please wait... image generation queued: {prompt}`")
        await image_request_queue.put({'message': message, 'prompt': prompt})

    if message.content.lower() == "lasagna":
        await send_gif(message, "garfield lasagna")

    if message.content.lower() == "monday":
        await send_gif(message, "garfield monday")

    if message.content.lower().startswith("garfgif "):
        search_term = message.content[8:]
        await send_gif(message, search_term)
    
    if message.content.lower().startswith("garfping "):
        try:
            query = message.content.split()
            user = message.author.name
            server = message.guild.name if message.guild else "Direct Message"
            target = query[-1]
            print(f"Ping Request - User: {user}, Server: {server}, Target: {target}", flush=True)
            if is_private(target):
                rejection = await generate_chat_response("Hey Garfield, explain to me why I am dumb for trying to hack your private computer network.")
                await message.channel.send(rejection)
            else:
                result = subprocess.run(['ping', '-c', '4', target], capture_output=True, text=True)
                await message.channel.send(f"`Ping result for {target}: {result.stdout}`")
        except Exception as e:
            await message.channel.send(f"`GarfBot Error: {str(e)}`")

    if message.content.lower().startswith("garfdns "):
        try:
            query = message.content.split()
            user = message.author.name
            server = message.guild.name if message.guild else "Direct Message"
            target = query[-1]
            print(f"NSLookup Request - User: {user}, Server: {server}, Target: {target}", flush=True)
            if is_private(target):
                rejection = await generate_chat_response("Hey Garfield, explain to me why I am dumb for trying to hack your private computer network.")
                await message.channel.send(rejection)
            else:
                result = subprocess.run(['nslookup', target], capture_output=True, text=True)
                await message.channel.send(f"`NSLookup result for {target}: {result.stdout}`")
        except Exception as e:
            await message.channel.send(f"`GarfBot Error: {str(e)}`")

    if message.content.lower().startswith("garfhack "):
        try:
            query = message.content.split()
            user = message.author.name
            server = message.guild.name if message.guild else "Direct Message"
            target = query[-1]
            print(f"Nmap Request - User: {user}, Server: {server}, Target: {target}", flush=True)
            if is_private(target):
                rejection = await generate_chat_response("Hey Garfield, explain to me why I am dumb for trying to hack your private computer network.")
                await message.channel.send(rejection)
            else:
                await message.channel.send(f"`Scanning {target}...`")
                result = subprocess.run(['nmap', '-Pn', '-O', '-v', target], capture_output=True, text=True)
                await message.channel.send(f"`Ping result for {target}: {result.stdout}`")
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

        if "meow" in message.content.lower():
            logger.info(f"Meow detected! {message.author.name} said: {message.content}")
            print(f"Meow detected! {message.author.name} said: {message.content}", flush=True)

            meow_counts[str(message.author.id)] += 1

            with open(meows_file, "w") as f:
                json.dump(dict(meow_counts), f)

            if message.content.lower() == "meowcount":
                response = f"My records show that <@{message.author.id}> has meowed {meow_counts[str(message.author.id)]} time(s). Have a nice day."
                await message.channel.send(response)

            if message.content.lower() == "top meowers":
                top_meowers = sorted(meow_counts.items(), key=itemgetter(1), reverse=True)[:10]
                embed = discord.Embed(title="Top Meowers :cat:", color=0x000000)
                for i, (user_id, meow_count) in enumerate(top_meowers):
                    user = await garfbot.fetch_user(int(user_id))
                    embed.add_field(name=f"{i+1}. {user.name}", value=f"{meow_count} meows", inline=False)
                await message.channel.send(embed=embed)

        if message.content.lower() == "checking in":
            user_id = str(message.author.id)
            if user_id in user_stats and user_stats[user_id]["check_in_time"] is not None:
                await message.channel.send(f"{message.author.mention} You are already checked in. Please check out first.")
                return

            check_in_time = datetime.utcnow().timestamp()
            if user_id not in user_stats:
                user_stats[user_id] = {"check_ins": 0, "total_time": 0, "check_in_time": None}
            user_stats[user_id]["check_in_time"] = check_in_time
            await message.channel.send(f"{message.author.mention} You have been checked in. Please mute your microphone.")

        elif message.content.lower() == "checking out":
            user_id = str(message.author.id)
            if user_id not in user_stats or user_stats[user_id]["check_in_time"] is None:
                await message.channel.send(f"{message.author.mention} You have not checked in yet. Please check in first.")
                return

            check_out_time = datetime.utcnow().timestamp()
            check_in_time = user_stats[user_id]["check_in_time"]
            time_delta = check_out_time - check_in_time
            user_stats[user_id]["check_ins"] += 1
            user_stats[user_id]["total_time"] += time_delta
            user_stats[user_id]["check_in_time"] = None

            with open("user_stats.json", "w") as f:
                json.dump(user_stats, f)
            await message.channel.send(f"{message.author.mention} You have been checked out. Your session was {time_delta:.2f} seconds.")

        elif message.content.lower() == "stats":
            stats_embed = discord.Embed(title="User stats  :trophy:", color=0x000000)
            sorted_user_stats = sorted(user_stats.items(), key=lambda x: x[1]["total_time"], reverse=True)
            table_rows = [["Name", "Check-ins", "Total Time"]]
            for user_id, stats in sorted_user_stats:
                if stats["check_in_time"] is None:
                    total_time_seconds = stats["total_time"]
                    hours, total_time_seconds = divmod(total_time_seconds, 3600)
                    minutes, total_time_seconds = divmod(total_time_seconds, 60)
                    seconds, fractions = divmod(total_time_seconds, 1)
                    fractions_str = f"{fractions:.3f}"[2:]
                    username = garfbot.get_user(int(user_id)).name
                    table_rows.append([username, str(stats["check_ins"]), f"{int(hours)}h {int(minutes)}m {int(seconds)}s {fractions_str}ms"])
                else:
                    username = garfbot.get_user(int(user_id)).name
                    table_rows.append([username, "Currently checked in", "-"])
            table_columns = list(zip(*table_rows[1:]))
            table_fields = table_rows[0]
            for field, values in zip(table_fields, table_columns):
                stats_embed.add_field(name=field, value="\n".join(values), inline=True)
            await message.channel.send(embed=stats_embed)


# GarfGifs
@garfbot.event
async def send_gif(message, search_term):
    lmt = 50
    ckey = "garfbot"
    r = requests.get(f"https://tenor.googleapis.com/v2/search?q={search_term}&key={gapikey}&client_key={ckey}&limit={lmt}")
    if r.status_code == 200:
        top_50gifs = json.loads(r.content)
        gif_url = random.choice(top_50gifs["product_querys"])["itemurl"]
        print(gif_url)
        try:
            await message.channel.send(gif_url)
        except KeyError:
            await message.channel.send("Oops, something went wrong.")
    else:
        await message.channel.send(f"`Oops, something went wrong. Error code: {r.status_code}`")


# discord.py Error Handling
@garfbot.event
async def on_error(event, *args, **kwargs):
    logger.error(f'GarfBot Error: {event}')
    print(f'GarfBot Error: {event}', flush=True)


# Run GarfBot!
try:
    garfbot.run(garfkey)
except Exception as e:
        e = str(e)
        logger.error(f"GarfBot Init Error: {e}")
        print(f"GarfBot Init Error: {e}", flush=True)
