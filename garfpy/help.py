import discord


async def help(message):
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
