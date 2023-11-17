import os
import json
import config
import openai
import aiohttp
import asyncio
import discord
import requests
import random
from openai import AsyncOpenAI
from datetime import datetime
from collections import defaultdict
from operator import itemgetter

openaikey = config.OPENAI_TOKEN
gapikey = config.GIF_TOKEN
garfkey = config.GARFBOT_TOKEN
txtmodel = "gpt-3.5-turbo"
imgmodel = "dall-e-3"

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    asyncio.create_task(process_image_requests())
    print(f"Logged in as {client.user.name} running gpt-3.5-turbo.", flush=True)

# MeowCounts File
counts_file = "meow_counts.json"
meow_counts = defaultdict(int)
if os.path.isfile(counts_file):
    with open(counts_file, "r") as f:
        meow_counts.update(json.load(f))
elif os.path.exists(counts_file):
    with open(counts_file, "r") as f:
        meow_counts = json.load(f)
try:
    with open("user_stats.json", "r") as f:
        user_stats = json.load(f)
except FileNotFoundError:
    user_stats = {}

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
        return f"`GarfBot Error: ({e.status_code}) - Your request was rejected as a result of our safety system.`"
    except openai.InternalServerError as e:
        print(e, flush=True)
        return f"`GarfBot Error: {e.status_code} - Monday`"
    except Exception as e:
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
                        filename = f"images/{timestamp}_generated_image.png"
                        with open(filename, "wb") as f:
                            f.write(image_data)
                        with open(filename, "rb") as f:
                            await message.channel.send(file=discord.File(f))
                    else:
                        await message.channel.send("`GarfBot Error: Odie`")
            else:
                await message.channel.send(image_url)
            image_request_queue.task_done()
            await asyncio.sleep(2)

# Listen for messages
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith("hey garfield") or isinstance(message.channel, discord.DMChannel):
        question = message.content[12:] if message.content.lower().startswith("hey garfield") else message.content
        answer = await generate_chat_response(question)
        await message.channel.send(answer)

    if message.content.lower().startswith('garfpic '):
        user = message.author.name
        server = message.guild.name if message.guild else "Direct Message"
        prompt = message.content[8:]
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

    # Army of Dawn Server
    if message.guild and message.guild.id == 719605634772893757:

        if "meow" in message.content.lower():
            print(f"Meow detected: {message.content}")

            meow_counts[str(message.author.id)] += 1

            with open(counts_file, "w") as f:
                json.dump(dict(meow_counts), f)

            if message.content.lower() == "meowcount":
                response = f"My records show that <@{message.author.id}> has meowed {meow_counts[str(message.author.id)]} time(s). Have a nice day."
                await message.channel.send(response)

            if message.content.lower() == "top meowers":
                top_meowers = sorted(meow_counts.items(), key=itemgetter(1), reverse=True)[:10]
                embed = discord.Embed(title="Top Meowers :cat:", color=0x000000)
                for i, (user_id, meow_count) in enumerate(top_meowers):
                    user = await client.fetch_user(int(user_id))
                    embed.add_field(name=f"{i+1}. {user.name}", value=f"{meow_count} meows", inline=False)
                await message.channel.send(embed=embed)

        if message.content.lower() == "checking in":
            # Check if user has already checked in
            user_id = str(message.author.id)
            if user_id in user_stats and user_stats[user_id]["check_in_time"] is not None:
                await message.channel.send(f"{message.author.mention} You are already checked in. Please check out first.")
                return

            # Record check-in time and add user to user_stats if not already there
            check_in_time = datetime.utcnow().timestamp()
            if user_id not in user_stats:
                user_stats[user_id] = {"check_ins": 0, "total_time": 0, "check_in_time": None}
            user_stats[user_id]["check_in_time"] = check_in_time
            await message.channel.send(f"{message.author.mention} You have been checked in. Please mute your microphone.")

        elif message.content.lower() == "checking out":
            # Check if user has already checked in
            user_id = str(message.author.id)
            if user_id not in user_stats or user_stats[user_id]["check_in_time"] is None:
                await message.channel.send(f"{message.author.mention} You have not checked in yet. Please check in first.")
                return

            # Record check-out time and update user stats
            check_out_time = datetime.utcnow().timestamp()
            check_in_time = user_stats[user_id]["check_in_time"]
            time_delta = check_out_time - check_in_time
            user_stats[user_id]["check_ins"] += 1
            user_stats[user_id]["total_time"] += time_delta
            user_stats[user_id]["check_in_time"] = None

            # Save user stats to file
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
                    username = client.get_user(int(user_id)).name
                    table_rows.append([username, str(stats["check_ins"]), f"{int(hours)}h {int(minutes)}m {int(seconds)}s {fractions_str}ms"])
                else:
                    username = client.get_user(int(user_id)).name
                    table_rows.append([username, "Currently checked in", "-"])
            table_columns = list(zip(*table_rows[1:]))
            table_fields = table_rows[0]
            for field, values in zip(table_fields, table_columns):
                stats_embed.add_field(name=field, value="\n".join(values), inline=True)
            await message.channel.send(embed=stats_embed)

# GarfGifs
@client.event
async def send_gif(message, search_term):
    lmt = 50
    ckey = "garfbot"
    r = requests.get(f"https://tenor.googleapis.com/v2/search?q={search_term}&key={gapikey}&client_key={ckey}&limit={lmt}")
    if r.status_code == 200:
        top_50gifs = json.loads(r.content)
        gif_url = random.choice(top_50gifs["results"])["itemurl"]
        print(gif_url)
        try:
            await message.channel.send(gif_url)
        except KeyError:
            await message.channel.send("Oops, something went wrong.")
    else:
        await message.channel.send(f"`Oops, something went wrong. Error code: {r.status_code}`")

# Run GarfBot
try:
    client.run(garfkey)
except Exception as e:
        e = str(e)
        print(f"GarfBot Error: {e}")
