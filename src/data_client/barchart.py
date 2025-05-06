import requests
import urllib.parse
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import pandas as pd

class BarchartAPI:
    BASE_URL = "https://www.barchart.com/proxies/core-api/v1"
    HEADERS = {
        "User-Agent": "Mozilla/5.0"
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.cookies = {}
        self.xsrf_token = ""

    async def fetch_cookies(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            try:
                await page.goto("https://www.barchart.com", timeout=10000)
            except:
                pass
            await page.wait_for_timeout(5000)

            cookies = await context.cookies()
            cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}

            await browser.close()

        required_cookies = [
            'cto_bundle', 'ic_tagmanager', 'XSRF-TOKEN', 'webinarClosed',
            'laravel_token', 'bcFreeUserPageView', 'laravel_session', 'market'
        ]
        self.cookies = {k: v for k, v in cookie_dict.items() if k in required_cookies}
        self.xsrf_token = urllib.parse.unquote(self.cookies.get('XSRF-TOKEN', ''))
        self.session.cookies.update(self.cookies)
        self.session.headers["x-xsrf-token"] = self.xsrf_token

    def get_quote(self, symbol="$SPX"):
        endpoint = f"{self.BASE_URL}/quotes/get"
        params = {
            "symbols": symbol,
            "raw": "true",
            "fields": ",".join([
                "symbol", "symbolType", "symbolCode", "symbolName", "nextEarningsDate",
                "contractName", "lastPrice", "priceChange", "percentChange", "hasOptions",
                "dividendYield", "exchange", "tradeTime"
            ])
        }
        return self.session.get(endpoint, params=params).json()

    def get_historical_volatility(self, symbol="$SPX", period=30, limit=999):
        endpoint = f"{self.BASE_URL}/historical-volatility"
        params = {
            "symbols": symbol,
            "fields": "volatility,tradeTime",
            "period": period,
            "limit": limit,
            "orderBy": "tradeTime",
            "orderDir": "desc"
        }
        return self.session.get(endpoint, params=params).json()

    def get_historical_prices(self, symbol="$SPX", limit=360):
        endpoint = f"{self.BASE_URL}/historical/get"
        params = {
            "symbol": symbol,
            "fields": "openPrice,lastPrice,priceChange,percentChange,tradeTime.format(Y-m-d)",
            "type": "eod",
            "limit": limit
        }
        return self.session.get(endpoint, params=params).json()

    def get_iv_by_delta(self, symbol="$SPX", limit=999):
        endpoint = f"{self.BASE_URL}/options/delta/get"
        fields = [
            f"delta{d}_30_puts,delta{d}_30_calls,delta{d}_30_both"
            for d in range(5, 100, 5)
        ]
        params = {
            "symbol": symbol,
            "fields": "date," + ",".join(fields),
            "limit": limit,
            "orderBy": "date",
            "orderDir": "desc"
        }
        return self.session.get(endpoint, params=params).json()

    def get_iv_rank(self, symbol="$SPX", limit=360):
        endpoint = f"{self.BASE_URL}/options-historical/get"
        params = {
            "symbol": symbol,
            "fields": "impliedVolatilityRank1y,impliedVolatilityPercentile1y,totalVolume,totalOpenInterest,historicalLastPrice,volatility,date",
            "limit": limit,
            "orderBy": "date",
            "orderDir": "desc"
        }
        return self.session.get(endpoint, params=params).json()

    def get_volatility_term_structure(self, symbol="$SPX", expirations=None):
        endpoint = f"{self.BASE_URL}/options/delta/get"
        fields = [
            f"delta{d}_puts,delta{d}_calls,delta{d}_both" for d in range(5, 100, 5)
        ]
        params = {
            "symbol": symbol,
            "fields": "date," + ",".join(fields),
            "eq(date)": "latest"
        }
        if expirations:
            params["expirations"] = ",".join(expirations)
        return self.session.get(endpoint, params=params).json()

    def get_gamma_exposure(self, symbol="$SPX", expirations=None):
        endpoint = f"{self.BASE_URL}/options/get"
        fields = [
            "symbol", "strikePrice", "optionType", "baseDailyLastPrice", "baseLastPrice",
            "dailyGamma", "gamma", "dailyOpenInterest", "openInterest",
            "dailyVolume", "volume", "daysToExpiration", "expirationDate"
        ]
        params = {
            "symbols": symbol,
            "raw": 1,
            "fields": ",".join(fields),
            "groupBy": "strikePrice",
            "le(nearestToLast)": "40"
        }
        if expirations:
            params["expirations"] = ",".join(expirations)
            print(params)
        return self.session.get(endpoint, params=params).json()

    def get_option_expirations(self, symbol="$SPX"):
        endpoint = f"{self.BASE_URL}/options-expirations/get"
        params = {
            "symbols": symbol,
            "fields": "expirationDate,expirationType,baseUpperPrice,baseLowerPrice,impliedMove,impliedMovePercent",
            "raw": "true"
        }
        return self.session.get(endpoint, params=params).json()

    def get_in_play_dates(self,expirations):
        expirations_df =  pd.DataFrame(expirations['data'])
        expirations_df['expirationDate'] = pd.to_datetime(expirations_df['expirationDate'])

        # Step 1: Get first 2 monthly expirations
        monthly_expirations = expirations_df[expirations_df['expirationType'] == 'monthly']
        first_two_monthlies = monthly_expirations.nsmallest(2, 'expirationDate')['expirationDate'].tolist()

        # Step 2: Add weekly expirations from the same month as the first monthly
        # get current month
        target_month = datetime.now().month
        weekly_expirations = expirations_df[
            (expirations_df['expirationType'] == 'weekly') &
            (expirations_df['expirationDate'].dt.month == target_month)
        ]
        weekly_same_month = weekly_expirations['expirationDate'].tolist()

        # Step 3: Add the 3 most recent (future) expirations not already included
        all_dates = expirations_df.sort_values('expirationDate', ascending=True)['expirationDate']
        recent_extras = [d for d in all_dates][:3]

        # Final combined list
        in_play_expiry_dates = list(dict.fromkeys(first_two_monthlies + weekly_same_month + recent_extras))  # remove dupes, preserve order

        # convert format to 2025-05-16
        in_play_expiry_dates = [d.strftime('%Y-%m-%d') for d in in_play_expiry_dates]
        
        return in_play_expiry_dates