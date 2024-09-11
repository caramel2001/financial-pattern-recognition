from src.data_client.earnings_transcript import MotleyFoolEarningsTranscript, CapIQEarningsTranscript,SeekingAlpha
from datetime import datetime,timedelta,date
import json
import yfinance as yf
from loguru import logger
from src.database.mongoDB import MongoDB

def get_estimates(symbol):
    ticker = yf.Ticker(symbol)
    ticker.info
    revenue_estimate = {
        "Average Revenue Estimate": str(ticker.revenue_estimate.iloc[0]['avg']/1000000)+" Million",
        "Number of Analysts": str(ticker.revenue_estimate.iloc[0]['numberOfAnalysts']),
        "High Revenue Estimate": str(ticker.revenue_estimate.iloc[0]['high']/1000000)+" Million",
        "Low Revenue Estimate": str(ticker.revenue_estimate.iloc[0]['low']/1000000)+" Million", 
    }
    eps_estimate = {
        "Average EPS Estimate": str(ticker.earnings_estimate.iloc[0]['avg']),
        "Number of Analysts": str(ticker.earnings_estimate.iloc[0]['numberOfAnalysts']),
        "High EPS Estimate": str(ticker.earnings_estimate.iloc[0]['high']),
        "Low EPS Estimate": str(ticker.earnings_estimate.iloc[0]['low']), 
    }
    return revenue_estimate,eps_estimate

if __name__ == "__main__":
    mongo_client = MongoDB()

    scraper = MotleyFoolEarningsTranscript()
    date = datetime.now() - timedelta(days=1)
    transcripts = scraper.get_transcripts(pages=1,date=date)

    logger.debug("Getting estimates")
    for transcript in transcripts:
        # only extract for NASDAQ and NYSE
        logger.debug(f"Getting estimates for {transcript['ticker']}")
        symbol = transcript['ticker']
        revenue_estimate,eps_estimate = get_estimates(symbol)
        transcript['revenue_estimate'] = revenue_estimate
        transcript['eps_estimate'] = eps_estimate
        transcript['source'] = "Motley Fool"
    with open(f"data/fool_transcripts_{date.date()}.json","w") as f:
        json.dump(transcripts,f)
    
    

    # have to automate this cookie part
    # cookie_str = """"""
    # capiq = CapIQEarningsTranscript()
    # data = capiq.get_transcripts(since=date.today() - timedelta(days=1))

    # logger.debug("Getting estimates")
    # for transcript in data:
    #     # only extract for NASDAQ and NYSE
    #     logger.debug(f"Getting estimates for {transcript['ticker']}")
    #     if transcript['exchange']=="NYSE" or "Nasdaq" in transcript['exchange']:
    #         symbol = transcript['ticker']
    #         revenue_estimate,eps_estimate = get_estimates(symbol)
    #         transcript['revenue_estimate'] = revenue_estimate
    #         transcript['eps_estimate'] = eps_estimate
    #     else:
    #         transcript['revenue_estimate'] = {}
    #         transcript['eps_estimate'] = {}
    #     transcript['source'] = "CapIQ"

    # with open(f"data/capiq_transcripts_{date.today()}.json","w") as f:
    #     json.dump(data,f)

    # store the transcripts in mongoDB
    mongo_client.store_transcripts(transcripts)

    # seeking = SeekingAlpha()
    # data = seeking.get_transcripts()
    # with open(f"data/seeking_alpha_transcripts_{date.today()}.json","w") as f:
    #     json.dump(data,f)