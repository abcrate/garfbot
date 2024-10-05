import io
import openai
import config
import aiohttp
import asyncio
import discord
from openai import AsyncOpenAI
from garfpy import logger

openaikey = config.OPENAI_TOKEN

txtmodel = config.TXT_MODEL
imgmodel = config.IMG_MODEL

# GarfPics
image_request_queue = asyncio.Queue()

async def picture_time(message, prompt):
    await image_request_queue.put({'message': message, 'prompt': prompt})

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
        logger.error(e)
        return f"`GarfBot Error: ({e.status_code}) - Monday`"
    except Exception as e:
        logger.error(e)
        return f"`GarfBot Error: Lasagna`"

async def process_image_requests():
    async with aiohttp.ClientSession() as session:
        while True:
            request = await image_request_queue.get()
            message = request['message']
            prompt = request['prompt']
            image_url = await generate_image(prompt)
            if "GarfBot Error" not in image_url:
                logger.info("Downloading & sending image...")
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        ram_image = io.BytesIO(image_data)
                        ram_image.seek(0)
                        timestamp = message.created_at.strftime('%Y%m%d%H%M%S')
                        filename = f"{timestamp}_generated_image.png"
                        sendfile = discord.File(fp=ram_image, filename=filename)
                        try:
                            await message.channel.send(file=sendfile)
                        except Exception as e:
                            logger.error(e)
                    else:
                        await message.channel.send("`GarfBot Error: Odie`")
            else:
                await message.channel.send(image_url)
            image_request_queue.task_done()
            await asyncio.sleep(2)

# GarfChats
async def generate_chat(question):
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
        logger.info(e, flush=True)
        return f"`GarfBot Error: Monday`"
    except Exception as e:
        logger.info(e, flush=True)
        return f"`GarfBot Error: Lasagna`"
