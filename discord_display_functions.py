import datetime
import time

import discord
from table2ascii import Merge, PresetStyle
from table2ascii import table2ascii as t2a


def time_left(mts_opening, period):
    """
    It is a function giving the remaining time until the loan expires in the timestamp format.
    """
    opening_time = datetime.datetime.fromtimestamp(mts_opening / 1000)
    expiry_time = opening_time + datetime.timedelta(days=period)
    time_left = expiry_time - datetime.datetime.now()
    return time_left

def time_left_seconds(time_left):
    """
    It is a function giving the remaining time until the loan expires in number of seconds.
    """
    return time_left.seconds+time_left.days*24*3600

def time_left_to_str(time_left_seconds):
    """
    It is a function giving nice str corresponding to the remaining time until the loan expires.
    """
    days_left = ""
    days = int(time_left_seconds // (3600*24))
    if days == 1: # Here I'm just making the display fancier by correcting plurals :)
        days_left = str(days) + " Day "
    elif days > 1:
        days_left = str(days) + " Days "
    hours_left = int((time_left_seconds // 3600) % 24)
    hours_left_str = ""
    if hours_left == 1:
        hours_left_str = str(hours_left) + " Hour "
    elif hours_left > 1:
        hours_left_str = str(hours_left) + " Hours "
    mins_left = int((time_left_seconds // 60) % 60)
    mins_left_str = ""
    if mins_left == 1:
        mins_left_str = str(mins_left) + " Min "
    elif mins_left > 1:
        mins_left_str = str(mins_left) + " Mins "
    return days_left + hours_left_str + mins_left_str

def totals(positions):
    """
    This function returns the desired sums and weighted avgs.
    """
    amount_sum = 0
    rate_avg = 0
    apr_avg = 0
    time_left_avg = 0
    for p in positions:
        amount_sum += p["amount"]
        rate_avg += p["rate"]*p["amount"]
        apr_avg += p["APR"]*p["amount"]
        time_left_avg += p["time_left_seconds"]*p["amount"]
    rate_avg *= 1/amount_sum
    apr_avg *= 1/amount_sum
    time_left_avg *= 1/amount_sum
    return {"amount_sum": amount_sum, "rate_avg": rate_avg, "apr_avg": apr_avg, "time_left_avg": time_left_to_str(time_left_avg)}

def table(positions, totals):
    """
    This function creates an str corresponding to a Discord table containing the positions and totals.
    """
    the_body = []
    for p in positions:
        if p["side"] != -1: # Here we are withdrawing the positions for which we are the borrower and not the lender.
            the_body.append([p["id"],f'{p["amount"]:,}',p["rate"], p["APR"], p["time_left_str"]])
    output = t2a(
    header=["ID", "Amount", "Rate", "APR", "Time Left"],
    body= the_body,
    footer=["Total", "Sum\n"+f'{totals["amount_sum"]:,}', "Weighted Average\n"+str(totals["rate_avg"]), "Weighted Average\n"+str(round(totals["apr_avg"],2)), "Weighted Average\n"+str(totals["time_left_avg"])],
    first_col_heading=True,
    style=PresetStyle.thin_compact
    )
    return output


def snapshot(money_made, total_usd_active_loans, total_usd_funding_offers, total_usd_in_account, percent_usd_active_loans, percent_usd_funding_offers):
    d = "```\nMoney made today: {}$\nMoney made all time: {}$\nAmount of USD in active loans: {}$ ({}%)\nAmount of USD on offers: {}$ ({}%)\nAmount of USD in account: {}$```".format(f'{money_made["money_made_today"]:,}', f'{money_made["money_made_all_time"]:,}', f'{total_usd_active_loans:,}', round(percent_usd_active_loans,2), f'{total_usd_funding_offers:,}', round(percent_usd_funding_offers,2), f'{total_usd_in_account:,}')
    return discord.Embed(title = 'Daily P&L Snapshot', description = d)