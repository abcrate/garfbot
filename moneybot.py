import config
import openai
import discord
import os

openai.api_key = config.OPENAI_TOKEN
moneykey = config.MONEYBOT_TOKEN

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name} running gpt-3.5-turbo-0613.", flush=True)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower().startswith("hey money") or isinstance(message.channel, discord.DMChannel):
        question = message.content[9:] if message.content.lower().startswith("hey money") else message.content
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                        {"role": "system", "content": "Pretend you are eccentric conspiracy theorist Planetside 2 gamer named Dr. Moneypants."},
                        {"role": "user", "content": f"{question} please keep it short with religious undertones"}
                    ],
                max_tokens=400
            )
            answer = response['choices'][0]['message']['content']
            answer = answer.replace("an AI language model", "a man of God")
            answer = answer.replace("language model", "man of God")
            await message.channel.send(answer)
        except Exception as e:
            e = str(e)
            await message.channel.send(f"`MoneyBot Error: {e}`")

client.run(moneykey)
