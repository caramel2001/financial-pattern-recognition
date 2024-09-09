import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import time
from datetime import datetime,timedelta,date
import pandas as pd
from loguru import logger
from tqdm import tqdm
import pytz
import time
import browser_cookie3

# motley fool
# https://www.kaggle.com/datasets/tpotterer/motley-fool-scraped-earnings-call-transcripts?select=motley-fool-data.pkl ()


class EarningsTranscriptScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def get_transcripts(self):
        raise NotImplementedError

# motley only covers selected list of stocks
class MotleyFoolEarningsTranscript(EarningsTranscriptScraper):
    def __init__(self):
        super().__init__()
    
    def get_transcripts(self,pages:int=5,sleep_count:int=20,date:datetime=None):
        """Transcripts from Motley Fool each page has most recent 20 transcripts"""
        url = "https://www.fool.com/earnings-call-transcripts"
        
        params = {
            "page": "1"
        }
        metas= []
        logger.debug("Extracting Meta Data of Transcripts")
        for page in tqdm(range(1,pages+1)):
            params["page"] = str(page)
            response = requests.get(url,params=params,headers=self.headers)            
            metas.extend(self.extract_meta_data(response.text))
        count = 0   

        for i in range(len(metas)):
            if date is not None:
                if datetime.strptime(metas[i]['Transcript date'],"%b %d, %Y").date() < date.date():
                    logger.debug(f"Reached date {datetime.strptime(metas[i]['Transcript date'],'%b %d, %Y').date()} stopping extraction")
                    break
            with tqdm(total=1,desc=f"Extracting {metas[i]['Company']} Transcript Body") as pbar:
                transcript,exchange = self.get_transcript_data(metas[i]['url_transcript'])
                pbar.update(1)
                metas[i]['exchange'] = exchange
                metas[i]['body'] = transcript
            count += 1
            if count % sleep_count == 0:
                logger.debug(f"Sleeping for 30 seconds")
                time.sleep(30)
        return metas      

    def extract_meta_data(self,html_content:str):
        soup = BeautifulSoup(html_content, 'html.parser')
        soup = soup.find("div",attrs={'class':'page'})
        transcript_data = []
        transcripts = soup.find_all('div', recursive=False)  # Find all first-level divs within the parent div
        for transcript in transcripts:
            full_company_info = transcript.find('h5').text
            company_name = full_company_info.split('(')[0].strip()
            ticker_symbol = full_company_info.split('(')[1].split(')')[0].strip()
            quarter_year_info = transcript.find('h5').text.split('(')[1].strip(')').split(' ')
            quarter = quarter_year_info[1].split('Q')[1]
            year = quarter_year_info[2]
            period = transcript.find('div').text.split('period ending ')[1]
            url_transcript = "https://www.fool.com" + transcript.find('a')['href']
            date = transcript.find_all('div')[1].text.split("by")[0].strip()

            transcript_info = {
                "Company": company_name,
                "Ticker": ticker_symbol,
                "Transcript date": date,
                "Earning Call Period": period.strip(),
                "url_transcript": url_transcript,
                "quarter": "Q" + quarter,
                "year": year
            }
            transcript_data.append(transcript_info)

        return transcript_data         

    def get_transcript_data(self,url:str):
        response = requests.get(url,headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to load page: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')
        exchange = self.extract_exchange(soup)
        return self.extract_transcript(soup),exchange

    def extract_exchange(self,soup):
        # extract JSON
        script = soup.find('script',attrs={'type':'application/ld+json'})
        json_data = json.loads(script.string)
        return json_data['about'][0]['tickerSymbol'].split(' ')[0].strip()

    def extract_transcript(self,soup):        
        transcript_body = soup.find('div', class_='article-body')
        json_list = []
        # Section variables
        statement_number = 1
        speaker = ""
        role = ""
        affiliation = ""
        # Iterate through paragraphs
        for element in transcript_body.find_all(['p']):
            if element.find('strong') == None:
                # Extract text content
                text_content = element.get_text(strip=True)
                if speaker=="":
                    continue
                if len(json_list)>0 and speaker == json_list[-1]["speaker"]:
                    # Append the text content to the current speaker's statement
                    json_list[-1]["text"] += " " + text_content
                else:
                    #Create a new JSON object for this statement
                    json_list.append({
                        "statement_num": statement_number,
                        "statement_type": "P",
                        "speaker": speaker,
                        "role": role,
                        "affiliation": affiliation,
                        "text": text_content
                    })
                    statement_number += 1
            else:
                element = element.find('strong')
                # It's a speaker's name
                speaker = element.get_text(strip=True)
                
                # Check if there's an associated role
                next_sibling = element.find_next_sibling('em')
                if next_sibling:
                    role = next_sibling.get_text(strip=True)
                else:
                    role = ""
                # check got affiliation
                if "--" in role:
                    affiliation = role.split("--")[0]
                    role = role.split("--")[1]
                else:
                    affiliation = ""

        return json_list
    
    def get_transcript(self,url:str):
        response = requests.get(url,headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to load page: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')
        return self.extract_transcript(soup)

class SeekingAlpha(EarningsTranscriptScraper):
    def __init__(self):
        super().__init__()
        self.articles_url = "https://seekingalpha.com/api/v3/articles"
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def process_response(self,response):
        df = pd.json_normalize(response.json()['data'])[['id', 'type', 'attributes.publishOn','attributes.title', 'relationships.primaryTickers.data','relationships.otherTags.data','links.self']]
        df['links.self'] = df['links.self'].apply(lambda x: "https://seekingalpha.com" + x)
        tickers = pd.json_normalize(response.json()['included']).set_index('id')
        df['ticker'] = df['relationships.primaryTickers.data'].apply(lambda x: tickers.loc[x[0]['id']]['attributes.name'])
        return df

    def get_json_data(self,soup):
        script = soup.find_all('script')[4]
        text = script.text.split("window.SSR_DATA = ")[1]
        # remove all text from "content" to "innerMarketing"
        text_2 = text.split('"content"')[1]
        # remove all text after the last "}"
        text_2 = text_2[:-1].split("innerMarketing")[1]

        json_data = json.loads(text.split('"content"')[0] + '"innerMarketing' + text_2)
        return json_data
    
    def parse_transcript(self,soup):
        script = soup.find_all('script')[4]
        text = script.text.split("window.SSR_DATA = ")[1]
        text_2 = text.split('"content":')[1]
        text_2 = text_2[:-1].split("innerMarketing")[0]
        soup = BeautifulSoup(text_2.encode().decode('unicode_escape'), 'html.parser')
        transcript = []
        statement_num = 1
        # Define a helper function to handle participants
        def extract_participants(p):
            p = p.find_next_sibling("p")
            participants_dict = {}
            text_content = p.get_text(separator="\n")
            lines = text_content.split('\n')
            for line in lines:
                if " - " in line:
                    name, position = line.split(" - ", 1)
                    participants_dict[name.strip()] = position.strip()
            return participants_dict
        text = ""
        skip_next = False
        current_speaker = None
        first_speaker = True
        for p in soup.find_all("p")[1:]:
            if skip_next:
                skip_next = False
                continue
            # Extract Company Participants
            if "Company Participants" in p.text:
                company_participants = extract_participants(p)
                skip_next = True
                continue
            # Extract Conference Call Participants
            if "Conference Call Participants" in p.text:
                conference_call_participants = extract_participants(p)
                skip_next = True
                continue
            # Extract main transcript body
            speaker_tag = p.find("strong")
            if (speaker_tag) :
                if not first_speaker:
                    transcript.append({
                        "statement_num": statement_num,
                        "speaker": current_speaker,
                        "role": role,
                        "affiliation": affiliation,
                        "text": text
                    })
                    statement_num += 1
                    text = ""
                current_speaker = speaker_tag.text.strip()
                role = company_participants.get(current_speaker, None) 
                affiliation = conference_call_participants.get(current_speaker, None)
            else:
                text += p.text + "\n"
                first_speaker = False
            transcript.append({
                        "statement_num": statement_num,
                        "speaker": current_speaker,
                        "role": role,
                        "affiliation": affiliation,
                        "text": text
                    })
        return transcript

    def get_transcript_body(self,url:str):
        response = requests.get(url,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        json_data = self.get_json_data(soup)
        transcript = self.parse_transcript(soup)
        return transcript,json_data


    def get_transcripts(self,since:datetime = datetime.today() - timedelta(days=1),until = datetime.today()):
        logger.debug(f"Extracting Transcripts since {since}")
        params = {
            "filter[category]": "earnings::earnings-call-transcripts",
            "filter[since]": str(int(since.timestamp())),
            "filter[until]": str(int(until.timestamp())),
            "include": "primaryTickers",
            "isMounting": "False",
            "page[size]": "50",
            "page[number]": "1"
        }
        logger.debug(params)
        response = requests.get(self.articles_url,headers=self.headers,params=params)
        results = response.json()['meta']['page']['total']
        if results == 0:
            logger.debug(f"No transcripts found within the date range {since} - {until}")
            return []
        print(response.json())
        pages = response.json()['meta']['page']['totalPages']
        logger.debug(f"Total Pages: {pages}")
        df = self.process_response(response)
        for page in tqdm(range(1, pages+1)):
            params['page[number'] = str(page)
            response = requests.get(self.articles_url, params=params, headers=self.headers)
            temp = self.process_response(response)
            df = pd.concat([df, temp], ignore_index=True)

        logger.debug(f"Extracting {len(df)} transcripts body")
        transcripts = []
        for url in tqdm(df['links.self']):
            transcript,json_data = self.get_transcript_body(url)
            transcripts.append(transcript)
        # get exchange
        exchanges=[]
        for ticker in tqdm(df['ticker']):
            for include in json_data['article']['response']['included']:
                if include.get('name',"") == ticker:
                    exchanges.append(include['exchange'])
                    break
        df['exchange'] = exchanges
        df['transcripts'] = transcripts
        return df.to_dict(orient='records')

class CapIQEarningsTranscript(EarningsTranscriptScraper):
    def __init__(self,cookie_str=None):
        super().__init__()
        if cookie_str == None:
            cookie_present = False
            # get cookies using browser_cookie3
            cj = browser_cookie3.chrome()
            for cookie in cj:
                if "capitaliq" in cookie.domain:
                    cookie_present = True
                    self.cookie_dict = cj
            if not cookie_present:
                raise Exception("Cookie not found in Chrome. Please login to Capital IQ and try again or provide the cookie string")
        else:
            self.cookie_dict = self.get_cookie_dict(cookie_str)

    def get_cookie_dict(self,cookie_str):
        cookies_dict = dict(item.split("=", 1) for item in cookie_str.split("; "))
        return cookies_dict

    def parse_transcript(self,soup:BeautifulSoup):
        # speaker positions
        # check if the transcript is still streaming
        if soup.find("span",attrs={'class':'headerTitle'}).text == "Streaming Transcripts":
            return ["Streaming"]

        start_pres= False
        speaker = ""
        text=""
        body=[]
        tab = soup.find("table",attrs={'class':'cTblListBody'})
        for p_tag in tab.find('tr',attrs={'id':'ctl01__bodyRow'}).find_all('p'):
        
            if 'Presentation' in p_tag.text and p_tag.attrs.get("style","") == 'font-weight:bold;':
                start_pres = True
                speaker = p_tag.text.split('Presentation')[1]
                continue
            if not start_pres:
                continue
            #print(p_tag.attrs.get("style",""))
            if p_tag.attrs.get("style","") == 'font-weight:bold;': # if new speaker
                body.append(
                    {
                        'speaker':speaker,
                        'text':text
                    }
                )
                speaker = p_tag.text
                text=""
                continue
            else:
                text+=p_tag.text + "\n"
        body.append(
            {
                'speaker':speaker,
                'text':text
            }
        )
        return body

    def parse_row(self,row):
        streaming = row.find("a",attrs={"title":"Launch Streaming Viewer"})
        streaming  = True if streaming else False
        row = row.findAll('td')
        
        if row[3].text.strip() != "Earnings Call":
            return {
                "date": None,
                "link": None,
                "company_name": None,
                "quarter": None,
                "ticker": None,
                "exchange": None,
                "streaming" : False,
            }
        date = row[1].text.strip()
        link = "https://www.capitaliq.com" + row[2].find('a').attrs['href']
        call_details = row[2].text.strip().split(",")
        company_name = call_details[0]
        #print(call_details)
        quarter = call_details[1]
        # call_details[3] = 2024Company: BluMetric Environmental Inc. (TSXV:BLM)
        ticker = call_details[-1].strip().split("(")[-1].split(")")[0]
        #print(ticker)
        exchange = ticker.split(":")[0]
        ticker = ticker.split(":")[1]
        return {
            "date": date,
            "link": link,
            "company_name": company_name,
            "quarter": quarter,
            "ticker": ticker,
            "exchange": exchange,
            "streaming" : streaming,
        }      

    def get_transcripts_body(self,transcript_urls:list,sleep_count:int=20):
        transcripts = [""]*len(transcript_urls)
        count = 0
        for url in tqdm(transcript_urls):
            logger.debug(url)
            response = requests.get(url,headers=self.headers,cookies=self.cookie_dict)
            soup = BeautifulSoup(response.content, 'html.parser')
            body = self.parse_transcript(soup)
            transcripts[count] = body
            count += 1
            if count % sleep_count == 0:
                logger.debug(f"Sleeping for 30 seconds")
                time.sleep(30)
        return transcripts

    def get_transcripts(self,since:datetime = date.today() - timedelta(days=1)):
        logger.debug(f"Extracting Transcripts since {since}")
        response = requests.get("https://www.capitaliq.com/CIQDotNet/Transcripts/Summary.aspx",headers=self.headers,cookies=self.cookie_dict)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find_all('table',attrs={'class':'cTblListBody'})[0] 
        data = list(map(self.parse_row,table.findAll('tr')[1:-1]))
        data = pd.json_normalize(data).dropna(subset=['link'])
        # if streaming then drop
        data = data[data['streaming'] == False]
        data['date'] = pd.to_datetime(data['date'])
        if data['date'].dt.date.min() < since:
            data = data[data['date'].dt.date >=since]
            if len(data) == 0:
                logger.debug(f"No transcripts found within the date range {since}")
                return []
            # else extract the transcripts
            transcripts = self.get_transcripts_body(data['link'].tolist())
            data['transcripts'] = transcripts
            # turn the datetime to string
            data['date'] = data['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            return data.to_dict(orient='records')
        form_data = form_data = {
            "__EVENTTARGET": "_transcriptsGrid$_dataGrid",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE":  "",
        }
        page = 2
        while True:
            logger.debug(f"Extracting page {page}")
            view_state = soup.find('input',attrs={'id':'__VIEWSTATE'}).attrs['value']
            form_data['__VIEWSTATE'] = view_state
            form_data['__EVENTARGUMENT'] = f"Page${page}"
            response = requests.post("https://www.capitaliq.com/CIQDotNet/Transcripts/Summary.aspx",headers=self.headers,cookies=self.cookie_dict,data=form_data)
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find_all('table',attrs={'class':'cTblListBody'})[0] 
            temp = list(map(self.parse_row,table.findAll('tr')[1:-1]))
            temp = pd.json_normalize(temp).dropna(subset=['link'])
            # if streaming then drop
            temp = temp[temp['streaming'] == False]
            temp['date'] = pd.to_datetime(temp['date'])
            if len(temp) == 0:
                page+=1
                continue
            if temp['date'].dt.date.min() < since:
                temp = temp[temp['date'].dt.date > since]
                data = pd.concat([data,temp])
                break
            data = pd.concat([data,temp])
            page+=1
        logger.debug(f"Extracting {len(data)} transcripts")
        transcripts = self.get_transcripts_body(data['link'].tolist())
        data['transcripts'] = transcripts
        # turn the datetime to string
        data['date'] = data['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        return data.to_dict(orient='records')
            
    def extract_meta_data(self):
        pass

if __name__ == "__main__":
    # Example usage
    # scraper = MotleyFoolEarningsTranscript()
    # # get yesterdays date
    # date = datetime.now() - timedelta(days=1)
    # transcripts = scraper.get_transcripts(pages=1,date=date)

    # with open(f"data/fool_transcripts_{date.date()}.json","w") as f:
    #     json.dump(transcripts,f)

    # get Capiq
    # cookie_str = """BIGipServercapitaliq-ssl=!T9TIhG5cvHbGAJw12585szMCRwMLn5ljdMQfIiya1kI1RIztsmfiwK0L5LZxdDIt2cYytzYEdq3RXv8=; machineIdCookie=783713664; X-User-CountryCode=IN; BIGipServerQTS-PRD-WEB-IDM-8080-PL=1872391319.36895.0000; _ga=GA1.2.1756279722.1723549018; _bl_uid=FglItz3Cs4scqvp2FstesLU0daXO; uoid=1199570856; __utmc=21616681; liveagent_oref=https://www.capitaliq.com/CIQDotNet/my/dashboard.aspx; liveagent_sid=e2044f8e-cc0e-42d1-925c-19d69ac760b1; liveagent_vc=2; liveagent_ptid=e2044f8e-cc0e-42d1-925c-19d69ac760b1; OptanonAlertBoxClosed=2024-08-13T12:16:07.661Z; BIGipServerQTS-PROD-APP-RB-8080-PL=3475225610.36895.0000; CIQState==; fileDownloaded=true; __utmz=21616681.1724913358.10.5.utmccn=(referral)|utmcsr=loginfs.ntu.edu.sg|utmcct=/|utmcmd=referral; _gid=GA1.2.1628993856.1725083429; _ga_D3TQ6N52TE=GS1.2.1725083429.13.0.1725083429.60.0.0; ASP.NET_SessionId=1hq0j2h2yf0uzfzgdfadb14y; SP_SSO_OKTA_RT_COOKIE=el9Zuu8OI70Dhm17uLk9K9GMV06qEUwrW11yQRdVL0k; SP_SSO_OKTA_SESS_EXPIRE=20240831235032; SP_SSO_OKTA_EXPIRE=20240831064532; SP_SSO_OKTA_COOKIE=eyJraWQiOiJPLVlDdlpGSzlIekd3N3o5QjR5YTc2M3ViS1RjeU9mMW52clRRa0w4V0I0IiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULmlvaTFmODM5Q1lQeDdLUHRGWDhzRmpneG5Fc2w5SjZ6V2xVOUh4VVluM0kub2Fycng1Ymc3MlVwbWppb3cxZDYiLCJpc3MiOiJodHRwczovL3NlY3VyZS5zaWduaW4uc3BnbG9iYWwuY29tL29hdXRoMi9zcGdsb2JhbCIsImF1ZCI6ImFwaTovL3NwZ2xvYmFsIiwiaWF0IjoxNzI1MDgzNDMyLCJleHAiOjE3MjUwODcwMzIsImNpZCI6IjBvYTFvMnc1bTV4ckFaVEtnMWQ4IiwidWlkIjoiMDB1MW51bmZkMGF4OW93N1ExZDgiLCJzY3AiOlsiY2lxIiwib3BlbmlkIiwib2ZmbGluZV9hY2Nlc3MiLCJwcm9maWxlIl0sImF1dGhfdGltZSI6MTcyNDkxMzM0Mywic3ViIjoiUFJBVEhBTTAwMUBFLk5UVS5FRFUuU0ciLCJsYXN0TmFtZSI6IlBSQVRIQU0iLCJjb3VudHJ5IjoiTk9UX0ZPVU5EIiwiZmlyc3ROYW1lIjoiQUdBUldBTEEiLCJFbWFpbCI6IlBSQVRIQU0wMDFARS5OVFUuRURVLlNHIiwiU1BfU1NPX0FQUFMiOlsiU0MiLCJDUyIsIk1LVFBMIiwiQ0lRIiwiTUkiXSwiY29tcGFueSI6W10sIkZlZDIiOltdLCJGZWQxIjpbIjExOTk1NzA4NTZAY2lxIiwiNzE3MzQ5MTM4QGxlZ2FjeWNpcSJdLCJUZW1wbGF0ZUlkIjoiTlRVU0FNTEBudHUuZWR1LnNnIn0.UzM28l6hxR0-IFqFHc0x8PUu_KM1ujoMciFQ4eMW8wZCJ64OJNaMNq51cUpT4tfhPJUMqfMcX6N8yHvRBmLvGQuk0DYcxWjiA2xJVWGA3d9DGmtJ0muEPSxZ4kMjciD_lpQpwxf2qfhlDR-NTzBFJ1Yb2q9rf5HAtHpCdOPh2YfOznbv7-1j7_ahFVutrHXfBQD6dcrfejcQLmsQRiUm5ybT-WsYYnp_Per-yb-BfGPgelvgSufJE6oX7PkWsdedZaQN49STG1TpTEqMYUbVisYFou3oHbWR4DImwTpuvjukd6sJ0mX9ep7pD_d6Qog8zHymlGuQhKYTkz9hmhIDoA; SP_SSO_JWT_COOKIE=el9Zuu8OI70Dhm17uLk9K9GMV06qEUwrW11yQRdVL0k; SP_SSO_SESS_EXPIRE=20240831235032; SP_SSO_AT_COOKIE=eyJraWQiOiJPLVlDdlpGSzlIekd3N3o5QjR5YTc2M3ViS1RjeU9mMW52clRRa0w4V0I0IiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULmlvaTFmODM5Q1lQeDdLUHRGWDhzRmpneG5Fc2w5SjZ6V2xVOUh4VVluM0kub2Fycng1Ymc3MlVwbWppb3cxZDYiLCJpc3MiOiJodHRwczovL3NlY3VyZS5zaWduaW4uc3BnbG9iYWwuY29tL29hdXRoMi9zcGdsb2JhbCIsImF1ZCI6ImFwaTovL3NwZ2xvYmFsIiwiaWF0IjoxNzI1MDgzNDMyLCJleHAiOjE3MjUwODcwMzIsImNpZCI6IjBvYTFvMnc1bTV4ckFaVEtnMWQ4IiwidWlkIjoiMDB1MW51bmZkMGF4OW93N1ExZDgiLCJzY3AiOlsiY2lxIiwib3BlbmlkIiwib2ZmbGluZV9hY2Nlc3MiLCJwcm9maWxlIl0sImF1dGhfdGltZSI6MTcyNDkxMzM0Mywic3ViIjoiUFJBVEhBTTAwMUBFLk5UVS5FRFUuU0ciLCJsYXN0TmFtZSI6IlBSQVRIQU0iLCJjb3VudHJ5IjoiTk9UX0ZPVU5EIiwiZmlyc3ROYW1lIjoiQUdBUldBTEEiLCJFbWFpbCI6IlBSQVRIQU0wMDFARS5OVFUuRURVLlNHIiwiU1BfU1NPX0FQUFMiOlsiU0MiLCJDUyIsIk1LVFBMIiwiQ0lRIiwiTUkiXSwiY29tcGFueSI6W10sIkZlZDIiOltdLCJGZWQxIjpbIjExOTk1NzA4NTZAY2lxIiwiNzE3MzQ5MTM4QGxlZ2FjeWNpcSJdLCJUZW1wbGF0ZUlkIjoiTlRVU0FNTEBudHUuZWR1LnNnIn0.UzM28l6hxR0-IFqFHc0x8PUu_KM1ujoMciFQ4eMW8wZCJ64OJNaMNq51cUpT4tfhPJUMqfMcX6N8yHvRBmLvGQuk0DYcxWjiA2xJVWGA3d9DGmtJ0muEPSxZ4kMjciD_lpQpwxf2qfhlDR-NTzBFJ1Yb2q9rf5HAtHpCdOPh2YfOznbv7-1j7_ahFVutrHXfBQD6dcrfejcQLmsQRiUm5ybT-WsYYnp_Per-yb-BfGPgelvgSufJE6oX7PkWsdedZaQN49STG1TpTEqMYUbVisYFou3oHbWR4DImwTpuvjukd6sJ0mX9ep7pD_d6Qog8zHymlGuQhKYTkz9hmhIDoA; SP_SSO_AT_COOKIE_EXPIRE=20240831064532; loginSearchCookie=fsbpDITlMl3HsuPShqgZo9EY7kPtG8ZCxGnVtdU9cQ/5ZCF2Te4FjXMSchR+KUBK; CIQ_ARQ_List=|; ASP.NET_SessionId=1hq0j2h2yf0uzfzgdfadb14y; __utma=21616681.59662645.1723549356.1724921949.1725083444.12; __utmb=21616681; _hp2_ses_props.544738949=%7B%22r%22%3A%22https%3A%2F%2Fwww.capitaliq.com%2Fciqdotnet%2FLogin-okta.aspx%22%2C%22ts%22%3A1725083444550%2C%22d%22%3A%22www.capitaliq.com%22%2C%22h%22%3A%22%2FCIQDotNet%2Fmy%2Fdashboard.aspx%22%7D; userLoggedIn=1hq0j2h2yf0uzfzgdfadb14y|8/31/2024 1:53:10 AM|717349138; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Aug+31+2024+11%3A23%3A21+GMT%2B0530+(India+Standard+Time)&version=202310.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0a1ffdca-c6e1-47d6-9c35-bb4c45014f32&interactionCount=2&landingPath=NotLandingPage&groups=C0003%3A1%2CC0002%3A1%2CC0001%3A1&AwaitingReconsent=false&geolocation=IN%3BAS; _hp2_id.544738949=%7B%22userId%22%3A%227241258315538576%22%2C%22pageviewId%22%3A%223626678047026804%22%2C%22sessionId%22%3A%222952513201168708%22%2C%22identity%22%3A%22717349138%22%2C%22trackerVersion%22%3A%224.0%22%2C%22identityField%22%3Anull%2C%22isIdentified%22%3A1%7D; _dd_s=rum=1&id=0b9d424c-3664-4121-acc5-849b9cbb3a3c&created=1725083436983&expire=1725084517700"""

    # capiq = CapIQEarningsTranscript(cookie_str)
    # data = capiq.get_transcripts()
    # with open(f"data/capiq_transcripts_{date.today()}.json","w") as f:
    #     json.dump(data,f)

    # get seeking alpha
    seeking = SeekingAlpha()
    data = seeking.get_transcripts()
    print(data)
    # get AMZN transcript
    # url = "https://www.fool.com/earnings/call-transcripts/2024/08/01/amazoncom-amzn-q2-2024-earnings-call-transcript/"
    # scraper = MotleyFoolEarningsTranscript()
    # transcript = scraper.get_transcript(url=url)
    # with open("data/amzn_transcript.json","w") as f:
    #     json.dump(transcript,f)
