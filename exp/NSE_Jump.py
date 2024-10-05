import pandas as pd
from glob import glob
from tqdm import tqdm

def read_data():
    data = []
    for file in tqdm(glob("data/fyers/*.json")):
        data.append(pd.read_json(file).set_index)
    return pd.concat(data)

def main():
    data = read_data()
    print(data.head())

    data.to_csv("data/fyers_data.csv")

if __name__ == "__main__":
    main()

