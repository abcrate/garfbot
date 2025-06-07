import discord
import ipaddress
import subprocess


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

    async def ping(self, ctx, target):
        if self.is_private(target):
            return
        try:
            await ctx.send(f"`Pinging {target}...`")
            result = subprocess.run(
                ["ping", "-c", "4", target], capture_output=True, text=True
            )
            embed = discord.Embed(
                title=f"Ping result: {target}",
                color=discord.Color.light_gray(),
                description=f"```{result.stdout}```",
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"`GarfBot Error: {str(e)}`")

    async def dns(self, ctx, target):
        if self.is_private(target):
            return
        try:
            await ctx.send(f"`Requesting {target}...`")
            result = subprocess.run(
                ["nslookup", target], capture_output=True, text=True
            )
            embed = discord.Embed(
                title=f"NSLookup result: {target}",
                color=discord.Color.light_gray(),
                description=f"```{result.stdout}```",
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"`GarfBot Error: {str(e)}`")

    async def scan(self, ctx, target):
        try:
            await ctx.send(f"`Scanning {target}...`")
            result = subprocess.run(
                ["nmap", "-Pn", "-O", "-v", target], capture_output=True, text=True
            )
            embed = discord.Embed(
                title=f"Nmap scan result: {target}",
                color=discord.Color.light_gray(),
                description=f"```{result.stdout}```",
            )
            embed.set_footer(text="https://nmap.org/")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"`GarfBot Error: {str(e)}`")
