from src.data_client.earnings_transcript import MotleyFoolEarningsTranscript, CapIQEarningsTranscript,SeekingAlpha
from datetime import datetime,timedelta,date
import json
import yfinance as yf
from loguru import logger

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
    # scraper = MotleyFoolEarningsTranscript()
    # date = datetime.now() - timedelta(days=2)
    # transcripts = scraper.get_transcripts(pages=1,date=date)
    # with open(f"data/fool_transcripts_{date.date()}.json","w") as f:
    #     json.dump(transcripts,f)

    # have to automate this cookie part
    cookie_str = """_ga=GA1.2.1756279722.1723549018; machineIdCookie=692380096; liveagent_oref=https://www.capitaliq.com/CIQDotNet/my/dashboard.aspx; liveagent_ptid=96a50c2f-c42a-4e8d-9f75-15fdc7804f81; BIGipServercapitaliq-ssl=!ETn5qny1Jtl4fDE12585szMCRwMLn9AWesjFov3SejW8/RIVZdbt0GWK+hqBxhZm0/yzzcUqraXQ6c0=; X-User-CountryCode=IN; BIGipServerQTS-PRD-WEB-IDM-8080-PL=2879024279.36895.0000; uoid=1199570856; __utmc=21616681; liveagent_sid=5e0e23af-fff5-45b7-96b2-33b51c89631b; liveagent_vc=3; OptanonAlertBoxClosed=2024-09-02T17:19:24.819Z; _gid=GA1.2.1166819902.1725541302; _gat=1; _ga_D3TQ6N52TE=GS1.2.1725543260.18.1.1725543914.60.0.0; ASP.NET_SessionId=dlyu1akwt5qce5ilcssa3la4; SP_SSO_OKTA_RT_COOKIE=x8HJH7cDVWpZm4_fjzxoPNY1B_4llDQawd7VxNyxjjU; SP_SSO_OKTA_SESS_EXPIRE=20240906074523; SP_SSO_OKTA_EXPIRE=20240905144023; SP_SSO_OKTA_COOKIE=eyJraWQiOiJPLVlDdlpGSzlIekd3N3o5QjR5YTc2M3ViS1RjeU9mMW52clRRa0w4V0I0IiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULmdXWlpjRHhrTVZVMlk5VU1NeEhwZWVtZzByWUFYaHQtcktxMFlfeDBhSjAub2FyczB4bTRwV2pLSDk1SlUxZDYiLCJpc3MiOiJodHRwczovL3NlY3VyZS5zaWduaW4uc3BnbG9iYWwuY29tL29hdXRoMi9zcGdsb2JhbCIsImF1ZCI6ImFwaTovL3NwZ2xvYmFsIiwiaWF0IjoxNzI1NTQzOTIzLCJleHAiOjE3MjU1NDc1MjMsImNpZCI6IjBvYTFvMnc1bTV4ckFaVEtnMWQ4IiwidWlkIjoiMDB1MW51bmZkMGF4OW93N1ExZDgiLCJzY3AiOlsiY2lxIiwib2ZmbGluZV9hY2Nlc3MiLCJwcm9maWxlIiwib3BlbmlkIl0sImF1dGhfdGltZSI6MTcyNTU0MzkyMSwic3ViIjoiUFJBVEhBTTAwMUBFLk5UVS5FRFUuU0ciLCJsYXN0TmFtZSI6IlBSQVRIQU0iLCJjb3VudHJ5IjoiTk9UX0ZPVU5EIiwiZmlyc3ROYW1lIjoiQUdBUldBTEEiLCJFbWFpbCI6IlBSQVRIQU0wMDFARS5OVFUuRURVLlNHIiwiU1BfU1NPX0FQUFMiOlsiU0MiLCJDUyIsIk1LVFBMIiwiQ0lRIiwiTUkiXSwiY29tcGFueSI6W10sIkZlZDIiOltdLCJGZWQxIjpbIjExOTk1NzA4NTZAY2lxIiwiNzE3MzQ5MTM4QGxlZ2FjeWNpcSJdLCJUZW1wbGF0ZUlkIjoiTlRVU0FNTEBudHUuZWR1LnNnIn0.PysjDZia2rvSeubSXKG_y8qbsSr8eGXIRgXCMmgGqePYX2TcUv0QRWLoG_r-phHFIAShkvBrBtVaE2b4pa7piZt_RuIwuLQ29ow-M2VEWNNxBdRoEcJ_Kxzmzb15zQtH52u3oAUVfSi5HCZI9JX2sKZpd76LZPIGywAqgpxVjgobrqXDH50aMufM1Yl0q9tSlyz6rQbVe7zbNvndml7cS_dPKTmSQ84oPgZtmX86RWGrpmQSxf_rDbUqQV_KLH8R7QAwuuV9BMlbaDvz0NuuHG1iUXZimHrCCw1Nftn6J9eGHZ4qMWgMQ0wNbXC_OeEhQ-r9dxwbxga_uXhT5dD17A; SP_SSO_JWT_COOKIE=x8HJH7cDVWpZm4_fjzxoPNY1B_4llDQawd7VxNyxjjU; SP_SSO_SESS_EXPIRE=20240906074523; SP_SSO_AT_COOKIE=eyJraWQiOiJPLVlDdlpGSzlIekd3N3o5QjR5YTc2M3ViS1RjeU9mMW52clRRa0w4V0I0IiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULmdXWlpjRHhrTVZVMlk5VU1NeEhwZWVtZzByWUFYaHQtcktxMFlfeDBhSjAub2FyczB4bTRwV2pLSDk1SlUxZDYiLCJpc3MiOiJodHRwczovL3NlY3VyZS5zaWduaW4uc3BnbG9iYWwuY29tL29hdXRoMi9zcGdsb2JhbCIsImF1ZCI6ImFwaTovL3NwZ2xvYmFsIiwiaWF0IjoxNzI1NTQzOTIzLCJleHAiOjE3MjU1NDc1MjMsImNpZCI6IjBvYTFvMnc1bTV4ckFaVEtnMWQ4IiwidWlkIjoiMDB1MW51bmZkMGF4OW93N1ExZDgiLCJzY3AiOlsiY2lxIiwib2ZmbGluZV9hY2Nlc3MiLCJwcm9maWxlIiwib3BlbmlkIl0sImF1dGhfdGltZSI6MTcyNTU0MzkyMSwic3ViIjoiUFJBVEhBTTAwMUBFLk5UVS5FRFUuU0ciLCJsYXN0TmFtZSI6IlBSQVRIQU0iLCJjb3VudHJ5IjoiTk9UX0ZPVU5EIiwiZmlyc3ROYW1lIjoiQUdBUldBTEEiLCJFbWFpbCI6IlBSQVRIQU0wMDFARS5OVFUuRURVLlNHIiwiU1BfU1NPX0FQUFMiOlsiU0MiLCJDUyIsIk1LVFBMIiwiQ0lRIiwiTUkiXSwiY29tcGFueSI6W10sIkZlZDIiOltdLCJGZWQxIjpbIjExOTk1NzA4NTZAY2lxIiwiNzE3MzQ5MTM4QGxlZ2FjeWNpcSJdLCJUZW1wbGF0ZUlkIjoiTlRVU0FNTEBudHUuZWR1LnNnIn0.PysjDZia2rvSeubSXKG_y8qbsSr8eGXIRgXCMmgGqePYX2TcUv0QRWLoG_r-phHFIAShkvBrBtVaE2b4pa7piZt_RuIwuLQ29ow-M2VEWNNxBdRoEcJ_Kxzmzb15zQtH52u3oAUVfSi5HCZI9JX2sKZpd76LZPIGywAqgpxVjgobrqXDH50aMufM1Yl0q9tSlyz6rQbVe7zbNvndml7cS_dPKTmSQ84oPgZtmX86RWGrpmQSxf_rDbUqQV_KLH8R7QAwuuV9BMlbaDvz0NuuHG1iUXZimHrCCw1Nftn6J9eGHZ4qMWgMQ0wNbXC_OeEhQ-r9dxwbxga_uXhT5dD17A; SP_SSO_AT_COOKIE_EXPIRE=20240905144023; userLoggedIn=dlyu1akwt5qce5ilcssa3la4|9/5/2024 10:05:27 AM|717349138; loginSearchCookie=fsbpDITlMl3HsuPShqgZo5lFuxCwGx7WtYeCu6/jrRZxofAdZ0XCUgNxOEiZDUB8; CIQState==; CIQ_ARQ_List=|; ASP.NET_SessionId=dlyu1akwt5qce5ilcssa3la4; __utma=21616681.59662645.1723549356.1725343368.1725543934.21; __utmb=21616681; __utmz=21616681.1725543934.21.2.utmccn=(referral)|utmcsr=loginfs.ntu.edu.sg|utmcct=/|utmcmd=referral; _hp2_id.544738949=%7B%22userId%22%3A%227241258315538576%22%2C%22pageviewId%22%3A%224655787586267329%22%2C%22sessionId%22%3A%228088072065249296%22%2C%22identity%22%3A%22717349138%22%2C%22trackerVersion%22%3A%224.0%22%2C%22identityField%22%3Anull%2C%22isIdentified%22%3A1%7D; _hp2_ses_props.544738949=%7B%22r%22%3A%22https%3A%2F%2Floginfs.ntu.edu.sg%2F%22%2C%22ts%22%3A1725543934480%2C%22d%22%3A%22www.capitaliq.com%22%2C%22h%22%3A%22%2FCIQDotNet%2Fmy%2Fdashboard.aspx%22%7D; _dd_s=rum=1&id=6db2f468-2b6f-407a-a798-072e7619c0ed&created=1725543930660&expire=1725544854450; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Sep+05+2024+19%3A15%3A54+GMT%2B0530+(India+Standard+Time)&version=202310.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0a1ffdca-c6e1-47d6-9c35-bb4c45014f32&interactionCount=3&landingPath=NotLandingPage&groups=C0003%3A1%2CC0002%3A1%2CC0001%3A1&AwaitingReconsent=false&geolocation=IN%3BAS"""
    capiq = CapIQEarningsTranscript(cookie_str)
    data = capiq.get_transcripts(since=date.today() - timedelta(days=1))

    logger.debug("Getting estimates")
    for transcript in data:
        # only extract for NASDAQ and NYSE
        logger.debug(f"Getting estimates for {transcript['ticker']}")
        if transcript['exchange']=="NYSE" or "Nasdaq" in transcript['exchange']:
            symbol = transcript['ticker']
            revenue_estimate,eps_estimate = get_estimates(symbol)
            transcript['revenue_estimate'] = revenue_estimate
            transcript['eps_estimate'] = eps_estimate
        else:
            transcript['revenue_estimate'] = {}
            transcript['eps_estimate'] = {}

    with open(f"data/capiq_transcripts_{date.today()}.json","w") as f:
        json.dump(data,f)


    # seeking = SeekingAlpha()
    # data = seeking.get_transcripts()
    # with open(f"data/seeking_alpha_transcripts_{date.today()}.json","w") as f:
    #     json.dump(data,f)