# The intra-bars features: when you are working with 4H timeframe data for example, you do not know what happens into them: the price was always close to the highest price, there was a spike in the data… To integrate that, I take the 1-minute data and I compute many things over each 4 hours: Hurst exponent, the aspect of the curve, volatility,
import pandas as pd
class IntraBarFeature:
    def __init__(self, data: pd.DataFrame,windows:list) -> None:
        self.data = data
    
    def hurst_exponent(self):
        pass
    
    def curve_aspect(self):
        pass
    
    def volatility(self):
        pass
    