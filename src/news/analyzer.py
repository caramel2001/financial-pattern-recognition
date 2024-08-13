class NewsAnalyzer:
    def __init__(self):
        pass    
    
    def analyze(self, news: str) -> float:
        pass

    def get_sentiment():
        "Uses Pre-trained Transformer model to get the sentiment of the news"
        pass
    
    def get_company_details():
        "Get the details of the company from the news"
        pass
    


class RiskAnalyzer:
    def __init__(self):
        pass
    
    def analyze(self, news: str) -> float:
        return self._analyzer.polarity_scores(news)['compound']
    
    def get_risk():
        "Get the risk of the news"
        pass

class IPOAnalyzer:
    def __init__(self):
        pass
    
    def analyze(self, news: str) -> float:
        pass
    
    def get_ipo_details():
        "Get the IPO details from the news"
        pass