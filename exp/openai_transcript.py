from pydantic import BaseModel
from openai import OpenAI
import json
from src.utils.config import settings
from src.data_client.alpaca import Stock
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import datetime as dt
# A sentiment response model for Openai contains two fields: sentiment score between -1 and 1, and explanation of the sentiment
# https://platform.openai.com/docs/guides/structured-outputs/introduction
class SentimentResponse(BaseModel):
    sentiment_score: float 
    sentiment_explanation: str

# def fetchPreMarket(symbol, exchange):
#     link    = f"https://www.google.com/finance/quote/{symbol}:{exchange}"
#     content = requests.get(link).text
#     soup    = BeautifulSoup(content, "html.parser")
#     info    = json.loads(content[3:])[0]
#     ts      = str(info["elt"])    # time stamp
#     last    = float(info["l"])    # close price (previous trading day)
#     pre     = float(info["el"])   # stock price in pre-market (after-hours)
#     return (ts, last, pre)


def main():
    # Create an instance of OpenAI
    client = OpenAI(api_key=settings['OPENAI_API_KEY'])

    # read downloaded transcript
    with open("data/fool_transcripts.json","r") as f:
        transcripts = json.load(f)
    
    transcript = transcripts[0]

    system_prompt =  """You are an advanced AI model specializing in analyzing financial earnings call transcripts. Your primary task is to evaluate the overall sentiment of an earnings call on a scale from -1 to 1. A score of -1 signifies a highly negative sentiment, indicative of potential poor future stock performance, while a score of 1 indicates a highly positive sentiment, suggesting strong future stock performance. Your analysis must provide a sentiment score and a detailed explanation that justifies the score, ensuring that it reflects the sentiment of the market immediately following the call. This will help in deciding whether to open a position in the stock, anticipating a price increase following day if the sentiment is positive, or a decrease if negative.

     Consider the following aspects when analyzing the earnings call:

    Tone and Language: Evaluate the tone used by executives and analysts. Positive language, confidence, and constructive discussions should push the sentiment score higher, while negative language, uncertainty, and defensiveness should lower it.
    Financial Performance: Analyze mentions of revenue, profit margins, earnings per share, and other financial metrics. Surpassing expectations is positive; missing them is negative.
    Guidance and Future Outlook: Focus on the company's guidance and future outlook. Positive guidance should increase the sentiment score, while negative or uncertain guidance should decrease it.
    Market and Industry Context: Consider any discussion of market conditions or industry trends that might affect the company's performance.

    For each earnings call, provide:
    Sentiment Score (-1 to 1): A numerical score reflecting the overall sentiment.
    Explanation: A detailed explanation covering the key factors that influenced the sentiment score.

    Additional Instructions:
    
    Critique Negative Findings Harshly: Ensure that any negative findings, particularly those that may influence poor future performance, are critiqued rigorously.
    Market Sentiment Alignment: Your score should align with the immediate sentiment of the market post-call to help determine the potential direction of the stock price."""

    # print(str(transcript["body"]))
    sentiment_response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": str(transcript["body"])}

        ],
        response_format= SentimentResponse
    )
    
    print(sentiment_response)

# Output 

# ParsedChatCompletion[SentimentResponse](id='chatcmpl-A0S3y8SyvRGjmdp38C6xo8kaexGZj', choices=[ParsedChoice[SentimentResponse](finish_reason='stop', index=0, logprobs=None, message=ParsedChatCompletionMessage[SentimentResponse](content='{"sentiment_score":0.9,"sentiment_explanation":"The earnings call for CAVA demonstrated a highly positive sentiment overall, reflected through several key indicators. Executives expressed confidence with strong growth statistics such as a 35.2% revenue increase year-over-year, significant same-restaurant sales growth, and achieving positive net income that surpassed the entire previous year in just one quarter. The discussion included detailed insights into operational success, including the successful rollout of new menu items and effective marketing strategies that resonated with consumers. Furthermore, the company\'s strong expansion strategy, with 18 new restaurants opened in the quarter and a robust outlook for future growth, indicated a well-positioned brand in the market. While management acknowledged external economic uncertainties, they emphasized their strong value proposition and consumer engagement, suggesting optimism for continued performance. Overall, the tone was very confident, and the financial performance exceeded expectations significantly, justifying the high sentiment score."}', refusal=None, role='assistant', function_call=None, tool_calls=[], parsed=SentimentResponse(sentiment_score=0.9, sentiment_explanation="The earnings call for CAVA demonstrated a highly positive sentiment overall, reflected through several key indicators. Executives expressed confidence with strong growth statistics such as a 35.2% revenue increase year-over-year, significant same-restaurant sales growth, and achieving positive net income that surpassed the entire previous year in just one quarter. The discussion included detailed insights into operational success, including the successful rollout of new menu items and effective marketing strategies that resonated with consumers. Furthermore, the company's strong expansion strategy, with 18 new restaurants opened in the quarter and a robust outlook for future growth, indicated a well-positioned brand in the market. While management acknowledged external economic uncertainties, they emphasized their strong value proposition and consumer engagement, suggesting optimism for continued performance. Overall, the tone was very confident, and the financial performance exceeded expectations significantly, justifying the high sentiment score.")))], created=1724671238, model='gpt-4o-mini-2024-07-18', object='chat.completion', service_tier=None, system_fingerprint='fp_f3db212e1c', usage=CompletionUsage(completion_tokens=187, prompt_tokens=13292, total_tokens=13479))

def get_premarket_movement(tickers_exhange:list):
    "get premarket movement of the stocks from yahoo finance"
    pass
    # todo
    #  premarket=[]
    # for i in tickers_exhange:
    #     ticker,exchange = i.split(",")
    #     ts, last, pre = fetchPreMarket("AAPL", "NASDAQ")
    #     if (pre != prev):
    #         prev = pre
    #         print(("%s\t%.2f\t%.2f\t%+.2f\t%+.2f%%" %
    #                 (ts, last, pre, pre - last, (pre / last - 1) * 100.)))
    #     premarket.append((ticker,pre))
    # return dict(premarket)

def get_next_day_opening_price(tickers_exchange:list):
    tickers = [i.split(",")[0] for i in tickers_exchange]
    date = dt.date.today() - dt.timedelta(days=1)
    data = yf.download(tickers, start=date.strftime("%Y-%m-%d"))
    #print(data[['Open','Adj Close']])
    #print((data['Open'].iloc[-1] - data['Adj Close'].iloc[0]) / data['Adj Close'].iloc[0])
    return ((data['Open'].iloc[-1] - data['Adj Close'].iloc[0]) / data['Adj Close'].iloc[0]).apply(lambda x : str(round(x*100,2))+"%").to_dict()

if __name__ == "__main__":
    # main()
    res = {
    "ULTA,NASDAQ": -0.4,
    "MDB,NASDAQ" : 0.6,
    "ADSK,NASDAQ": 0.7,
    "DDD,NYSE" : 0.2,
    "ESTC,NYSE": -0.2,
    "MRVL,NASDAQ": 0.8,
    "GPS,NYSE": 0.7,
    }
    tickers= list(res.keys())
    # premarket_movement = get_premarket_movement(tickers)
    # print(premarket_movement)
    next_day_opening_price = get_next_day_opening_price(tickers)
    print("------------SENTIMENT RESULT----------------")
    print(res)
    print("\n")
    print("------------Next-Day Premarket Movements----------------")
    print(next_day_opening_price)
