import io
import openai
import config
import aiohttp
import asyncio
import discord
import wikipedia
from openai import AsyncOpenAI
from garfpy import logger


class GarfAI:
    def __init__(self):
        self.openaikey = config.OPENAI_TOKEN
        self.txtmodel = config.TXT_MODEL
        self.imgmodel = config.IMG_MODEL
        self.image_request_queue = asyncio.Queue()

    async def garfpic(self, ctx, prompt):
        await self.image_request_queue.put({"ctx": ctx, "prompt": prompt})

    async def generate_image(self, prompt):
        client = AsyncOpenAI(api_key=self.openaikey)
        try:
            response = await client.images.generate(
                model=self.imgmodel, prompt=prompt, n=1, size="1024x1024"
            )
        except openai.BadRequestError as e:
            return f"`GarfBot Error: ({e.status_code}) - Your request was rejected as a result of our safety system.`"
        except openai.InternalServerError as e:
            logger.error(e)
            return f"`GarfBot Error: ({e.status_code}) - Monday`"
        except Exception as e:
            logger.error(e)
            return "`GarfBot Error: Lasagna`"
        data = getattr(response, "data", None)
        if not data:
            logger.error("No data in response")
            return "`GarfBot Error: No images generated`"

        first_image = data[0] if len(data) > 0 else None
        if not first_image:
            logger.error("No image in response data")
            return "`GarfBot Error: No images generated`"

        image_url = getattr(first_image, "url", None)
        if not image_url:
            logger.error("No URL in image response")
            return "`GarfBot Error: No image URL returned`"

        return image_url

    async def process_image_requests(self):
        async with aiohttp.ClientSession() as session:
            while True:
                request = await self.image_request_queue.get()
                ctx = request["ctx"]
                prompt = request["prompt"]
                image_url = await self.generate_image(prompt)
                if image_url and "GarfBot Error" not in image_url:
                    logger.info("Downloading & sending image...")
                    async with session.get(image_url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            image = io.BytesIO(image_data)
                            image.seek(0)
                            timestamp = ctx.message.created_at.strftime("%Y%m%d%H%M%S")
                            filename = f"{timestamp}_generated_image.png"
                            sendfile = discord.File(fp=image, filename=filename)
                            try:
                                await ctx.send(file=sendfile)
                            except Exception as e:
                                logger.error(e)
                        else:
                            await ctx.send("`GarfBot Error: Odie`")
                else:
                    await ctx.send(image_url)
                self.image_request_queue.task_done()
                await asyncio.sleep(2)

    async def generate_chat(self, question):
        try:
            client = AsyncOpenAI(api_key=self.openaikey)
            response = await client.chat.completions.create(
                model=self.txtmodel,
                messages=[
                    {
                        "role": "system",
                        "content": "Pretend you are sarcastic Garfield.",
                    },
                    {"role": "user", "content": f"{question}"},
                ],
                max_tokens=400,
            )
            answer = str(response.choices[0].message.content)
            return answer.replace("an AI language model", "a cartoon animal")
        except openai.BadRequestError as e:
            logger.error(e)
            return f"`GarfBot Error: {e}`"
        except openai.APIError as e:
            logger.error(e)
            return "`GarfBot Error: Monday`"
        except Exception as e:
            logger.error(e)
            return "`GarfBot Error: Lasagna`"

    async def wikisum(self, query):
        try:
            summary = wikipedia.summary(query)
            garfsum = await self.generate_chat(
                f"Please summarize in your own words: {summary}"
            )
            return garfsum
        except Exception as e:
            return e
