import pandas as pd
from hmmlearn import hmm

class MarkovModel:
    def __init__(self,data:pd.DataFrame) -> None:
        self.data = data
