import io
import openai
import config
import aiohttp
import asyncio
import discord
from openai import AsyncOpenAI
from garfpy import logger


class GarfAI:
    def __init__(self):
        self.openaikey = config.OPENAI_TOKEN
        self.txtmodel = config.TXT_MODEL
        self.imgmodel = config.IMG_MODEL
        self.image_request_queue = asyncio.Queue()

    async def garfpic(self, message, prompt):
        await self.image_request_queue.put({'message': message, 'prompt': prompt})

    async def generate_image(self, prompt):
        try:
            client = AsyncOpenAI(api_key = self.openaikey)
            response = await client.images.generate(
                model=self.imgmodel,
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

    async def process_image_requests(self):
        async with aiohttp.ClientSession() as session:
            while True:
                request = await self.image_request_queue.get()
                message = request['message']
                prompt = request['prompt']
                image_url = await self.generate_image(prompt)
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
                self.image_request_queue.task_done()
                await asyncio.sleep(2)

    # GarfChats
    @staticmethod
    async def generate_chat(self, question):
        try:
            client = AsyncOpenAI(api_key = self.openaikey)
            response = await client.chat.completions.create(
                model=self.txtmodel,
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
