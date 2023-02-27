import asyncio
import datetime as dt
import logging
import threading
import time as t
from datetime import datetime, time, timedelta

import discord
import pytz
from discord.ext import commands

import bitfinex_portfolio
import discord_display_functions

# pip install py-cord==2.0.0b1 # This installation is essential!
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('discord.http').setLevel(logging.WARNING)
logging.getLogger('discord').setLevel(logging.CRITICAL)

MY_DISCORD_TOKEN = "" # Insert your Discord Bot Token here.
CHANNEL_ID = 1 # Here you should put the channel ID on which you would like to have the daily PNL snapshots.

logging.basicConfig(level=logging.INFO) # Configuration of the logging to output INFO level logs
intents = discord.Intents.default() # Set up the Discord bot client with a command prefix and member intent
intents.members = True
client = commands.Bot(command_prefix="/B ", intents=intents)

@client.event
async def on_ready():
    """
    This function sends the regular snapshots. One first, then each day at 17:00 (London time).
    """
    channel = await client.fetch_channel(CHANNEL_ID) 
    while True:
        portfolio = bitfinex_portfolio.BitfinexPortfolio()
        money_made = portfolio.ledgers()
        total_usd_active_loans = portfolio.usd_active_loans()
        total_usd_funding_offers = portfolio.usd_funding_offers()
        total_usd_in_account = portfolio.usd_in_account()
        percent_usd_active_loans = 100*total_usd_active_loans/total_usd_in_account
        percent_usd_funding_offers = 100*total_usd_funding_offers/total_usd_in_account
        output = discord_display_functions.snapshot(money_made, total_usd_active_loans, total_usd_funding_offers, total_usd_in_account, percent_usd_active_loans, percent_usd_funding_offers)
        await channel.send(embed = output)
        # Get the current time in London
        london_tz = pytz.timezone('Europe/London')
        now = datetime.now(tz=london_tz)
        # Calculate the time difference between now and 17:00 London time
        target_time = london_tz.localize(datetime.now().replace(hour=17, minute=0, second=0, microsecond=0)) # get datetime object 
        tms_target_time = int(target_time.astimezone(pytz.utc).timestamp()) # convert datetime to timestamp in UTC
        if t.time() > tms_target_time:
            tms_target_time += dt.timedelta(days=1)
        time_diff = tms_target_time - t.time()
        # Wait until 17:00 London time has passed
        await asyncio.sleep(time_diff) # asyncio.sleep() is used instead of time.sleep() to ensure that the loop doesn't block the event loop.

@client.command(name="Lending")
async def bitfinex_lending_positions(ctx):
    """
    This is a Discord command responding to "\B Lending" and sending the requested Bitfinex lending informations.
    """
    portfolio = bitfinex_portfolio.BitfinexPortfolio()
    credit_positions = portfolio.active_credit_positions()
    totals = discord_display_functions.totals(credit_positions)
    output = discord_display_functions.table(credit_positions, totals)
    #await ctx.send(f"Here are your current Bitfinex lending open positions:\n{str(credit_positions)}")
    await ctx.send(f"Here are your currently open Bitfinex lending positions:\n```\n{output}\n```")

# client.run(MY_DISCORD_TOKEN)

async def main():
    # Start the Discord bot
    await client.start(MY_DISCORD_TOKEN)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())