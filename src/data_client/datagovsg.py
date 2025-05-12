from typing import Literal
import requests
import pandas as pd
import zipfile
import io
from loguru import logger

class DataGovSG:
    def __init__(self):
        self.base_url = "https://data.gov.sg/api/action/datastore_search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.session = requests.Session()

    # deprecated as data only available  until 2017
    # def get_car_makes(self):
    #     # annual car make
    #     dataset_id = "d_2fcb043ef09016ae757bc396cd8f5027"
    #     params = {
    #         "resource_id": dataset_id,
    #         "limit": 1000,
    #         "offset": 0,
    #     }
    #     response = self.session.get(self.base_url, params=params, headers=self.headers)
    #     data = response.json()
    #     total = data["result"]["total"]
    #     df = pd.json_normalize(data["result"]["records"])
    #     logger.info(f"Total records: {total}")
    #     if total > 1000:
    #         logger.warning("More than 1000 records, may take longer to process")
    #         for i in range(1000, total, 1000):
    #             params["offset"] = i
    #             response = self.session.get(self.base_url, params=params, headers=self.headers)
    #             data = response.json()
    #             df = pd.json_normalize(data["result"]["records"])
    #             df = pd.concat([df, df], ignore_index=True)

    #     return df

    def get_car_makes(self,frequency:Literal["A","M"]="A"):
        if frequency not in ["A","M"]:
            raise ValueError("Frequency must be 'A' for annual or 'Q' for quarterly")
        if frequency == "A":
            # URL of the ZIP file
            url = "https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle%20Population/Annual%20Car%20Population%20by%20Make.zip"
        elif frequency == "M":
            # URL of the ZIP file
            url = "https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle%20Registration/Monthly%20New%20Registration%20of%20Cars%20by%20Make.zip"

        

        # Send GET request to download the ZIP file
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Open the ZIP file from memory
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # List all files in the ZIP archive
            logger.info("Files in the zip:", z.namelist())

            # Extract the first CSV file (you can adjust the filename if needed)
            for file_name in z.namelist():
                if file_name.endswith(".csv"):
                    with z.open(file_name) as f:
                        df = pd.read_csv(f)
                        break

        return df
