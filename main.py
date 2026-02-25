import os
import requests
import discord
import asyncio
from discord import app_commands
from datetime import datetime

API_KEY = os.getenv("PNW_API_KEY")
ALLIANCE_ID = os.getenv("ALLIANCE_ID")
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

last_transaction_id = None

async def check_transactions():
    global last_transaction_id
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        url = f"https://politicsandwar.com/api/v2/alliance-bank-records/{ALLIANCE_ID}/?key={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "data" in data and len(data["data"]) > 0:
            latest = data["data"][0]

            if latest["id"] != last_transaction_id:
                last_transaction_id = latest["id"]

                embed = discord.Embed(
                    title="🏦 Alliance Bank Transaction",
                    color=0x2ecc71
                )

                embed.add_field(name="Nation", value=latest["nation_name"], inline=False)
                embed.add_field(name="Type", value=latest["type"], inline=True)
                embed.add_field(name="Money", value=f"${latest['money']}", inline=True)
                embed.add_field(name="Food", value=latest["food"], inline=True)
                embed.add_field(name="Oil", value=latest["oil"], inline=True)
                embed.add_field(name="Steel", value=latest["steel"], inline=True)

                embed.set_footer(text=datetime.utcnow().strftime("%d %b %Y %H:%M UTC"))

                await channel.send(embed=embed)

        await asyncio.sleep(60)


@tree.command(name="balance", description="Check alliance bank balance")
async def balance(interaction: discord.Interaction):
    url = f"https://politicsandwar.com/api/v2/alliance/{ALLIANCE_ID}/?key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    embed = discord.Embed(title="🏦 Alliance Bank Balance", color=0x3498db)

    embed.add_field(name="Money", value=f"${data['money']}", inline=True)
    embed.add_field(name="Food", value=data["food"], inline=True)
    embed.add_field(name="Oil", value=data["oil"], inline=True)
    embed.add_field(name="Steel", value=data["steel"], inline=True)

    await interaction.response.send_message(embed=embed)


@tree.command(name="last", description="Show last 5 transactions")
async def last(interaction: discord.Interaction):
    url = f"https://politicsandwar.com/api/v2/alliance-bank-records/{ALLIANCE_ID}/?key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    embed = discord.Embed(title="📜 Last 5 Transactions", color=0xf1c40f)

    for txn in data["data"][:5]:
        embed.add_field(
            name=f"{txn['nation_name']} ({txn['type']})",
            value=f"💵 ${txn['money']} | 🌾 {txn['food']}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


@client.event
async def on_ready():
    await tree.sync()
    client.loop.create_task(check_transactions())
    print("Bot is online")


client.run(TOKEN)
