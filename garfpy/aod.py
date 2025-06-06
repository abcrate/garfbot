import os
import json
import discord
from garfpy import logger
from datetime import datetime
from operator import itemgetter
from collections import defaultdict


# Meows Json Handling
meows_file = "meow_counts.json"
stats_file = "user_stats.json"


def json_load(file_path, default):
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        return default


meow_counts = defaultdict(int, json_load(meows_file, {}))
user_stats = json_load(stats_file, {})


async def aod_message(garfbot, message):
    if "meow" in message.content.lower():
        logger.info(f"Meow detected! {message.author.name} said: {message.content}")

        meow_counts[str(message.author.id)] += 1

        with open(meows_file, "w") as f:
            json.dump(dict(meow_counts), f)

        if message.content.lower() == "meowcount":
            response = f"My records show that <@{message.author.id}> has meowed {meow_counts[str(message.author.id)]} time(s). Have a nice day."
            await message.channel.send(response)

        if message.content.lower() == "top meowers":
            top_meowers = sorted(meow_counts.items(), key=itemgetter(1), reverse=True)[
                :10
            ]
            embed = discord.Embed(title="Top Meowers :cat:", color=0x000000)
            for i, (user_id, meow_count) in enumerate(top_meowers):
                user = await garfbot.fetch_user(int(user_id))
                embed.add_field(
                    name=f"{i + 1}. {user.name}",
                    value=f"{meow_count} meows",
                    inline=False,
                )
            await message.channel.send(embed=embed)

    if message.content.lower() == "checking in":
        user_id = str(message.author.id)
        if user_id in user_stats and user_stats[user_id]["check_in_time"] is not None:
            await message.channel.send(
                f"{message.author.mention} You are already checked in. Please check out first."
            )
            return

        check_in_time = datetime.now().timestamp()
        if user_id not in user_stats:
            user_stats[user_id] = {
                "check_ins": 0,
                "total_time": 0,
                "check_in_time": None,
            }
        user_stats[user_id]["check_in_time"] = check_in_time
        await message.channel.send(
            f"{message.author.mention} You have been checked in. Please mute your microphone."
        )

    elif message.content.lower() == "checking out":
        user_id = str(message.author.id)
        if user_id not in user_stats or user_stats[user_id]["check_in_time"] is None:
            await message.channel.send(
                f"{message.author.mention} You have not checked in yet. Please check in first."
            )
            return

        check_out_time = datetime.now().timestamp()
        check_in_time = user_stats[user_id]["check_in_time"]
        time_delta = check_out_time - check_in_time
        user_stats[user_id]["check_ins"] += 1
        user_stats[user_id]["total_time"] += time_delta
        user_stats[user_id]["check_in_time"] = None

        with open("user_stats.json", "w") as f:
            json.dump(user_stats, f)
        await message.channel.send(
            f"{message.author.mention} You have been checked out. Your session was {time_delta:.2f} seconds."
        )

    elif message.content.lower() == "stats":
        stats_embed = discord.Embed(title="User stats  :trophy:", color=0x000000)
        sorted_user_stats = sorted(
            user_stats.items(), key=lambda x: x[1]["total_time"], reverse=True
        )
        table_rows = [["Name", "Check-ins", "Total Time"]]
        for user_id, stats in sorted_user_stats:
            if stats["check_in_time"] is None:
                total_time_seconds = stats["total_time"]
                hours, total_time_seconds = divmod(total_time_seconds, 3600)
                minutes, total_time_seconds = divmod(total_time_seconds, 60)
                seconds, fractions = divmod(total_time_seconds, 1)
                fractions_str = f"{fractions:.3f}"[2:]
                username = garfbot.get_user(int(user_id)).name
                table_rows.append(
                    [
                        username,
                        str(stats["check_ins"]),
                        f"{int(hours)}h {int(minutes)}m {int(seconds)}s {fractions_str}ms",
                    ]
                )
            else:
                username = garfbot.get_user(int(user_id)).name
                table_rows.append([username, "Currently checked in", "-"])
        table_columns = list(zip(*table_rows[1:]))
        table_fields = table_rows[0]
        for field, values in zip(table_fields, table_columns):
            stats_embed.add_field(name=field, value="\n".join(values), inline=True)
        await message.channel.send(embed=stats_embed)
