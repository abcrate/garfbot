from garfpy import logger
import discord
import json
import os
import re


class GarfbotRespond:
    def __init__(self):
        self.garfbot_guild_responses = {}
        self.responses_file = 'responses.json'

    def load_responses(self):
        global garfbot_guild_responses
        if os.path.exists(self.responses_file):
            try:
                with open(self.responses_file, 'r', encoding='utf-8') as f:
                    garfbot_guild_responses = json.load(f)
                garfbot_guild_responses = {int(k): v for k, v in garfbot_guild_responses.items()}
                total_responses = sum(len(responses) for responses in garfbot_guild_responses.values())
                logger.info(f"Loaded responses for {len(garfbot_guild_responses)} server(s), ({total_responses} total responses)")
            except Exception as e:
                logger.info(f"Error loading responses: {e}")
                garfbot_guild_responses = {}
        else:
            garfbot_guild_responses = {}

    def save_responses(self):
        try:
            save_data = {str(k): v for k, v in garfbot_guild_responses.items()}
            with open(self.responses_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            total_responses = sum(len(responses) for responses in garfbot_guild_responses.values())
            logger.info(f"Saved responses for {len(garfbot_guild_responses)} servers ({total_responses} total responses)")
        except Exception as e:
            logger.info(f"Error saving responses: {e}")

    def get_responses(guild_id):
        if guild_id not in garfbot_guild_responses:
            garfbot_guild_responses[guild_id] = {}
        return garfbot_guild_responses[guild_id]

    async def garfbot_response(self, message, content):
        guild_id = message.guild.id
        
        add_pattern = r'garfbot\s+response\s+add\s+["\']([^"\']+)["\']\s+["\']([^"\']+)["\']'
        add_match = re.search(add_pattern, content, re.IGNORECASE)
        
        if add_match:
            trigger = add_match.group(1)
            response_text = add_match.group(2)
            await self.add_response(message, guild_id, trigger, response_text)
            return
        
        add_simple_pattern = r'garfbot\s+response\s+add\s+(\S+)\s+(\S+)'
        add_simple_match = re.search(add_simple_pattern, content, re.IGNORECASE)
        
        if add_simple_match:
            trigger = add_simple_match.group(1)
            response_text = add_simple_match.group(2)
            await self.add_response(message, guild_id, trigger, response_text)
            return
        
        remove_pattern = r'garfbot\s+response\s+remove\s+(\S+)'
        remove_match = re.search(remove_pattern, content, re.IGNORECASE)
        
        if remove_match:
            trigger = remove_match.group(1).strip()
            await self.remove_response(message, guild_id, trigger)
            return
        
        if re.search(r'garfbot\s+response\s+list', content, re.IGNORECASE):
            await self.list_responses(message, guild_id)
            return
        
        await message.channel.send(
            "**Garfbot Auto-Response Commands:**\n"
            "`garfbot response add \"trigger\" \"response\"`\n"
            "`garfbot response remove \"trigger\"`\n"
            "`garfbot response list`\n\n"
            "**Examples:**\n"
            "`garfbot response add \"hi\" \"Hello there!\"`\n"
            "`garfbot response add \"that's what\" \"That's what she said!\"`\n"
            "`garfbot response remove \"hi\"`"
        )

    async def add_response(self, message, guild_id, trigger, response_text):
        if not response_text or not trigger:
            await message.channel.send("❌ Trigger and response must not be null.")
            return
        
        responses = self.get_responses(guild_id)
        responses[trigger] = response_text
        garfbot_guild_responses[guild_id] = responses
        self.save_responses()
        
        embed = discord.Embed(
            title="✅ Auto-response Added.",
            color=0x00ff00
        )
        embed.add_field(name="Trigger", value=f"`{trigger}`", inline=True)
        embed.add_field(name="Response", value=f"`{response_text}`", inline=True)
        embed.set_footer(text=f"Server: {message.guild.name}")
        
        await message.channel.send(embed=embed)

    async def remove_response(self, message, guild_id, trigger):
        responses = self.get_responses(guild_id)
        
        if trigger in responses:
            removed_response = responses[trigger]
            del responses[trigger]
            garfbot_guild_responses[guild_id] = responses
            self.save_responses()
            
            embed = discord.Embed(
                title="✅ Auto-response Removed.",
                color=0xff6b6b
            )
            embed.add_field(name="Trigger", value=f"`{trigger}`", inline=True)
            embed.add_field(name="Response", value=f"`{removed_response}`", inline=True)
            embed.set_footer(text=f"Server: {message.guild.name}")
            
            await message.channel.send(embed=embed)
            return
        
        for key in responses.keys():
            if key.lower() == trigger.lower():
                removed_response = responses[key]
                del responses[key]
                garfbot_guild_responses[guild_id] = responses
                self.save_responses()
                
                embed = discord.Embed(
                    title="✅ Auto-response Removed.",
                    color=0xff6b6b
                )
                embed.add_field(name="Trigger", value=f"`{key}`", inline=True)
                embed.add_field(name="Response", value=f"`{removed_response}`", inline=True)
                embed.set_footer(text=f"Server: {message.guild.name}")
                
                await message.channel.send(embed=embed)
                return
        
        await message.channel.send(f"❌ No auto-response found for trigger: `{trigger}`")

    async def list_responses(self, message, guild_id):
        responses = self.get_responses(guild_id)
        
        if not responses:
            await message.channel.send("No auto-responses configured for this server.")
            return
        
        embed = discord.Embed(
            title=f"Auto-Responses for {message.guild.name}",
            color=0x3498db
        )
        
        for i, (trigger, response) in enumerate(responses.items(), 1):
            display_response = response[:50] + "..." if len(response) > 50 else response
            embed.add_field(
                name=f"{i}. `{trigger}`",
                value=f"→ {display_response}",
                inline=False
            )
        
        embed.set_footer(text=f"Total responses: {len(responses)}")
        await message.channel.send(embed=embed)
