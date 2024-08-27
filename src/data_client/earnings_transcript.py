import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import time
# motley fool
# https://www.kaggle.com/datasets/tpotterer/motley-fool-scraped-earnings-call-transcripts?select=motley-fool-data.pkl ()


class EarningsTranscriptScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def get_transcripts(self):
        raise NotImplementedError


class MotleyFoolEarningsTranscript(EarningsTranscriptScraper):
    def __init__(self):
        super().__init__()
    
    def get_transcripts(self,pages:int=5,sleep_count:int=20):
        """Transcripts from Motley Fool each page has most recent 20 transcripts"""
        url = "https://www.fool.com/earnings-call-transcripts"
        
        params = {
            "page": "1"
        }
        metas= []
        print("Extracting Meta Data of Transcripts")
        for page in tqdm(range(1,pages+1)):
            params["page"] = str(page)
            response = requests.get(url,params=params,headers=self.headers)            
            metas.extend(self.extract_meta_data(response.text))
        count = 0   
        for i in range(len(metas)):
            with tqdm(total=1,desc=f"Extracting {metas[i]['Company']} Transcript Body") as pbar:
                transcript = self.get_transcript_data(metas[i]['url_transcript'])
                pbar.update(1)
                metas[i]['body'] = transcript
            count += 1
            if count % sleep_count == 0:
                print(f"Sleeping for 30 seconds")
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
        return self.extract_transcript(soup)

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
    
if __name__ == "__main__":
    # Example usage
    scraper = MotleyFoolEarningsTranscript()
    transcripts = scraper.get_transcripts(pages=1)

    with open("data/fool_transcripts.json","w") as f:
        json.dump(transcripts,f)
