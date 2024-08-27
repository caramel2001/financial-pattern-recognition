from pydantic import BaseModel
from openai import OpenAI
import json
from src.utils.config import settings
# A sentiment response model for Openai contains two fields: sentiment score between -1 and 1, and explanation of the sentiment
class SentimentResponse(BaseModel):
    sentiment_score: float 
    sentiment_explanation: str

def main():
    # Create an instance of OpenAI
    client = OpenAI(api_key=settings['OPENAI_API_KEY'])

    # read downloaded transcript
    with open("data/fool_transcripts.json","r") as f:
        transcripts = json.load(f)
    
    transcript = transcripts[0]

    system_prompt = """ You are an AI model designed to analyze financial earnings call transcripts. Your task is to evaluate the sentiment of the earnings call on a scale from -1 to 1. A score of -1 indicates a very negative earnings call, likely predicting poor future stock performance, while a score of 1 indicates a highly positive earnings call, suggesting strong future stock performance. The score should be accompanied by a explanation justifying the sentiment analysis.

    Consider the following aspects when analyzing the earnings call:

    Tone and Language: Evaluate the tone used by executives and analysts. Positive language, confidence, and constructive discussions should push the sentiment score higher, while negative language, uncertainty, and defensiveness should lower it.
    Financial Performance: Analyze mentions of revenue, profit margins, earnings per share, and other financial metrics. Surpassing expectations is positive; missing them is negative.
    Guidance and Future Outlook: Focus on the company's guidance and future outlook. Positive guidance should increase the sentiment score, while negative or uncertain guidance should decrease it.
    Market and Industry Context: Consider any discussion of market conditions or industry trends that might affect the company's performance.
    For each earnings call, provide:"""

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

if __name__ == "__main__":
    main()