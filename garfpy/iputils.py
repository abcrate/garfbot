import discord
import ipaddress
import subprocess
from garfpy import logger


class IPUtils:
    def is_private(self, target):
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

    async def scan(self, message, user, guild, query):
        split = query.split()
        target = split[-1]
        if self.is_private(target):
            return

        if query.startswith("garfping "):
            try:
                logger.info(
                    f"Ping Request - User: {user}, Server: {guild}, Target: {target}"
                )
                await message.channel.send(f"`Pinging {target}...`")
                result = subprocess.run(
                    ["ping", "-c", "4", target], capture_output=True, text=True
                )
                embed = discord.Embed(title=f"Ping result: {target}", color=0x4D4D4D, description=f"```{result.stdout}```")
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.channel.send(f"`GarfBot Error: {str(e)}`")

        if query.startswith("garfdns "):
            try:
                logger.info(
                    f"NSLookup Request - User: {user}, Server: {guild}, Target: {target}"
                )
                await message.channel.send(f"`Requesting {target}...`")
                result = subprocess.run(
                    ["nslookup", target], capture_output=True, text=True
                )
                embed = discord.Embed(title=f"NSLookup result: {target}", color=0x4D4D4D, description=f"```{result.stdout}```")
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.channel.send(f"`GarfBot Error: {str(e)}`")

        if query.startswith("garfhack "):
            try:
                logger.info(
                    f"Nmap Request - User: {user}, Server: {guild}, Target: {target}"
                )
                await message.channel.send(f"`Scanning {target}...`")
                result = subprocess.run(
                    ["nmap", "-Pn", "-O", "-v", target], capture_output=True, text=True
                )
                embed = discord.Embed(title=f"Nmap scan result: {target}", color=0x4D4D4D, description=f"```{result.stdout}```")
                embed.set_footer(text="https://nmap.org/")
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.channel.send(f"`GarfBot Error: {str(e)}`")
