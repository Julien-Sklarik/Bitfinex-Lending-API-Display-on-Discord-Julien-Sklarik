import base64
import datetime
import hashlib
import hmac
import json
import time

import pytz
import requests

import discord_display_functions


class BitfinexPortfolio(object):
    """
    This class is meant to be like your Bitfinex portfolio. 
    It must give the full details of the Bitfinex Lending Positions.
    """
    BASE_URL = "https://api.bitfinex.com/"
    KEY="" # Insert your Bitfinex API Key here.
    SECRET="" # Insert your Bitfinex API Secret here.

    symbols = ["1INCH","AAA","AAVE","AAVEF0","ADA","ADAF0","AIX","ALBT","ALG","ALGF0","AMP","AMPF0","ANC","ANT","APE","APEF0","APENFT","APT","APTF0","ATLAS","ATO","ATOF0","AVAX","AVAXC","AVAXF0","AXS","AXSF0","B2M","BAL","BAND","BAT","BBB","BCH","BCHABC","BCHN","BEST","BFT","BFX","BG1","BG2","BMI","BMN","BNT","BOBA","BOO","BOSON","BSV","BTC","BTCDOMF0","BTCF0","BTG","BTSE","BTT","CAD","CCD","CEL","CHEX","CHF","CHSB","CHZ","CLO","CNH","CNHT","COMP","COMPF0","CONV","CRV","CRVF0","DAI","DGB","DOGE","DOGEF0","DORA","DOT","DOTF0","DRK","DSH","DUSK","DVF","EDO","EGLD","EGLDF0","ENJ","EOS","EOSF0","ETC","ETCF0","ETH","ETH2P","ETH2R","ETH2X","ETHF0","ETHS","ETHW","ETP","EUR","EURF0","EUS","EUT","EUTF0","EXRD","FBT","FCL","FET","FIL","FILF0","FLR","FORTH","FTM","FTMF0","FUN","GALA","GALAF0","GBP","GBPF0","GNO","GNT","GRT","GTX","GXT","HEC","HIX","HKD","HMT","HMTPLG","HTX","ICE","ICP","ICPF0","IDX","IOT","IOTF0","IQX","JASMY","JASMYF0","JPY","JPYF0","JST","KAI","KAN","KNC","KNCF0","KSM","LBT","LEO","LES","LET","LINK","LINKF0","LNX","LRC","LTC","LTCF0","LUNA","LUNA2","LUNAF0","LUXO","LYM","MATIC","MATICF0","MATICM","MIM","MIR","MKR","MKRF0","MLN","MNA","MOB","MXNT","NEAR","NEARF0","NEO","NEOF0","NEOGAS","NEXO","OCEAN","OGN","OMG","OMGF0","OMN","ONE","OXY","PAS","PAX","PLANETS","PLU","PNG","PNK","POLC","POLIS","QRDO","QTF","QTM","RBT","REEF","REP","REQ","RLY","ROSE","RRT","SAND","SANDF0","SENATE","SGB","SGD","SHFT","SHFTM","SHIB","SHIBF0","SIDUS","SMR","SNT","SNX","SOL","SOLF0","SPELL","SRM","STG","STGF0","STJ","SUKU","SUN","SUSHI","SUSHIF0","SWEAT","SXX","TERRAUST","TESTBTC","TESTBTCF0","TESTUSD","TESTUSDT","TESTUSDTF0","THB","THETA","TLOS","TRADE","TREEB","TRX","TRXF0","TRY","TSD","TWD","UDC","UNI","UNIF0","UOS","USD","UST","USTF0","UTK","VEE","VELO","VET","VRA","VSY","WAVES","WAVESF0","WAX","WBT","WILD","WNCG","WOO","XAGF0","XAUT","XAUTF0","XCAD","XCN","XDC","XLM","XLMF0","XMR","XMRF0","XRA","XRD","XRP","XRPF0","XTZ","XTZF0","XVG","YFI","ZCN","ZEC","ZECF0","ZIL","ZMT","ZRX"]
    # I got all the symbols from the documentation here: https://docs.bitfinex.com/reference/rest-public-tickers by clicking on "pub:list:currency".
    # This would be useful in case we would want to retrieve credit positions that are not in usd.

    def nonce(self):
        """
        This method generates a nonce (a unique number) that can be used in the headers for an API request.
        """
        return str(int(round(time.time() * 1000)))
    
    def headers(self, path, nonce, body):
        """
        This method is generates the headers needed for making HTTP requests to an API. 
        """
        signature = "/api/" + path + nonce + body
        h = hmac.new(self.SECRET.encode(encoding='UTF-8'),
                     signature.encode(encoding='UTF-8'), hashlib.sha384)
        signature = h.hexdigest()
        return {
            "bfx-nonce": nonce,
            "bfx-apikey": self.KEY,
            "bfx-signature": signature,
            "content-type": "application/json"
        }

    def active_credit_positions(self):
        """
        This method returns a list of the user's current funds used in active positions (each in a distinct dictionary).
        """
        nonce = self.nonce()
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/funding/credits/fUSD"
        headers = self.headers(path, nonce, rawBody)
        r = requests.post(self.BASE_URL + path, headers=headers, data=rawBody, verify=True)
        if r.status_code == 200:
            credit_positions = r.json()
            credit_positions_info = []
            for c in credit_positions:
                credit_position = {}
                credit_position["id"] = c[0] # The two first pieces of info are just in case it becomes useful (e.g.: for identification).
                credit_position["symbol"] = c[1]
                credit_position["side"] = c[2]
                credit_position["amount"] = round(c[5])
                credit_position["rate"] = c[11]*100 # I'm converting the rate in percent.
                credit_position["APR"] = c[11]*365*100
                credit_position["time_left"] = discord_display_functions.time_left(mts_opening=c[13], period=c[12])
                credit_position["time_left_seconds"] = discord_display_functions.time_left_seconds(credit_position["time_left"])
                credit_position["time_left_str"] = discord_display_functions.time_left_to_str(credit_position["time_left_seconds"])
                credit_positions_info.append(credit_position)
            return credit_positions_info
        else:
            print(r.status_code)
            print(r)
            return ''
        
    def ledgers(self):
        """
        This method returns the money made today and all time.
        """
        nonce = self.nonce()
        body = {'category': 22}
        rawBody = json.dumps(body)
        path = "v2/auth/r/ledgers/hist"
        headers = self.headers(path, nonce, rawBody)
        r = requests.post(self.BASE_URL + path, headers=headers, data=rawBody, verify=True)
        if r.status_code == 200:
            entries = r.json()
            money_made_today = 0
            money_made_all_time = 0
            london_tz = pytz.timezone('Europe/London') # set timezone to London
            morning = london_tz.localize(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)) # get datetime object for today at midnight
            morning_utc = int(morning.astimezone(pytz.utc).timestamp())*1000 # convert datetime to timestamp in UTC and in milliseconds
            for e in entries:
                if e[3] > morning_utc:
                    money_made_today += e[5]
                money_made_all_time += e[5]
            return {"money_made_today": round(money_made_today,2), "money_made_all_time": round(money_made_all_time,2)}

        else:
            print(r.status_code)
            print(r)
            return ''
        
    def usd_active_loans(self):
        """
        This method returns the amount of USD in active loans.
        """
        nonce = self.nonce()
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/funding/credits/fUSD"
        headers = self.headers(path, nonce, rawBody)
        r = requests.post(self.BASE_URL + path, headers=headers, data=rawBody, verify=True)
        if r.status_code == 200:
            credit_positions = r.json()
            total_usd = 0
            for c in credit_positions:
                if c[2] != -1: # We don't consider the cases where you are the borrower.
                    total_usd += c[5]
            return round(total_usd,2)
        else:
            print(r.status_code)
            print(r)
            return ''
        
    def usd_funding_offers(self):
        """
        This method returns the amount of USD in funding offers.
        """
        nonce = self.nonce()
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/funding/offers/fUSD"
        headers = self.headers(path, nonce, rawBody)
        r = requests.post(self.BASE_URL + path, headers=headers, data=rawBody, verify=True)
        if r.status_code == 200:
            positions = r.json()
            total_usd = 0
            for c in positions:
                total_usd += c[4]
            return round(total_usd,2)
        else:
            print(r.status_code)
            print(r)
            return ''
        
    def usd_in_account(self):
        """
        This method returns the total amount of USD in the account (by taking the sum of balances of USD portfolios).
        """
        nonce = self.nonce()
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/wallets"
        headers = self.headers(path, nonce, rawBody)
        r = requests.post(self.BASE_URL + path, headers=headers, data=rawBody, verify=True)
        if r.status_code == 200:
            wallets = r.json()
            total_usd = 0
            for w in wallets:
                if w[1] == "USD":
                    total_usd += w[2]
            return round(total_usd,2)
        else:
            print(r.status_code)
            print(r)
            return ''