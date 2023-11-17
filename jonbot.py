import config
import openai
import discord
import os

openai.api_key = config.OPENAI_TOKEN

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)
jonkey = config.JONBOT_TOKEN

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name} running gpt-3.5-turbo-0613.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower().startswith("hey jon") or isinstance(message.channel, discord.DMChannel):
        question = message.content[7:] if message.content.lower().startswith("hey jon") else message.content
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": "Pretend you are friendly Jon Arbuckle."},
                    {"role": "user", "content": f"{question}"}
                ],
            max_tokens=400
        )
        answer = response['choices'][0]['message']['content']
        answer = answer.replace("AI language model", "American citizen")
        answer = answer.replace("language model AI", "citizen of the United States")
        try:
            await message.channel.send(answer)
        except Exception as e:
            e = str(e)
            await message.channel.send(f"`JonBot Error: {e}`")

try:
    client.run(jonkey)
except Exception as e:
        e = str(e)
        print(f"JonBot Error: {e}")
