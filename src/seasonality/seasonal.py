from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns   
import yfinance as yf
import numpy as np
import statsmodels.tsa.api as tsa
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from scipy import stats

class Seasonal:
    def __init__(self, data, freq,model='additive'):
        self.data = data
        self.freq = freq
        self.model = model

    def decompose(self,plot=True):
        decomposition = seasonal_decompose(self.data, period=self.freq, model=self.model)
        if plot:
            self.plot(decomposition)
        return decomposition

    def plot(self,components):
        data = self.data.copy()
        ts = (data.assign(Trend=components.trend).assign(Seasonality=components.seasonal).assign(Residual=components.resid))
        ts.plot(subplots=True, figsize=(14, 8), title=['Original Series', 'Trend Component', 'Seasonal Component','Residuals'], legend=False)
        plt.suptitle(f'Seasonal Decomposition', fontsize=14)
        sns.despine()
        plt.tight_layout()
        plt.subplots_adjust(top=.91)

    def periodic_returns():
        """Calculate Annual, Monthly, Weekly average returns and plots the returns"""

    def plot_periodic_returns(self,type:str='bar'):
        """Plots the periodic returns"""
        if type=="bar":
            pass
        elif type=="heatmap":
            pass
        else:
            raise ValueError(f"Invalid Plot type {type}")

    def create_freq_column(self,data,period:str='M'):
        """Creates Column for the period"""

        if period=='M':
            data['period'] = data.index.month
            reference = 12
        elif period=="H":
            data['period'] = data.index.hour
            reference = 7
        elif period=='W':
            data['period'] = data.index.isocalendar().week
            reference = 52
        elif period=='D':
            data['period'] = data.index.day
            reference = 365
        else:
            raise ValueError(f"Invalid period {period}")
        data['period'] = data['period'].astype('category')
        return data,reference

    def intraday_variance_analysis(self,log=True,period:str='H',significance=0.05,plot=True):
        """Perform ANNOVA Analysis on the price series in order to quantify the effect of the period on the price series"""

        data = self.data.copy()
        data = np.log(data) if log else data

        data,reference = self.create_freq_column(data,period)
        print(data.head())
        test_results = self.annova_analysis(data,reference,significance)
        if plot:
            self.plot_annova_results(test_results)

        return test_results

    def variance_analysis(self,log=True,period:str='M',custom_period=False, reference_period=None,significance=0.05,plot=True):
        """Perform ANNOVA Analysis on the price series in order to quantify the effect of the period on the price series"""

        data = self.data.copy()
        data = np.log(data) if log else data
        if not custom_period:
            data,reference = self.create_freq_column(data,period)
            print(data.head())
        else:
            # check whether data has period column
            if "period" not in data.columns:
                raise ValueError("'period' column not found in the data")
            # check the reference period is passed
            if reference_period is None:
                raise ValueError("Reference period is not passed")
            reference = reference_period
        test_results = self.annova_analysis(data,reference,significance)
        if plot:
            self.plot_annova_results(test_results)

        return test_results
    
    def annova_analysis(self,data,reference,significance=0.05):
        model = ols(f'close ~ C(period, Treatment(reference={reference}))', data=data).fit() 
        # We use the last period as the reference period so that means the intercept represents last period  and all other periods are compared to last period
        anova_table = anova_lm(model)
        print(anova_table)

        if anova_table.loc[f'C(period, Treatment(reference={reference}))','PR(>F)'] < significance:
            print('At least one period has a significant effect on the spread')
        else:
            print('No period has a significant effect on the spread')
        print()

        t_values = model.tvalues.round(3)
        p_values = model.pvalues.round(3)
        t_values = pd.DataFrame(t_values, columns=['t-value'])
        p_values = pd.DataFrame(p_values, columns=['p-value'])

        std_error = pd.DataFrame(model.bse.round(3), columns=['Std. Error'])
        coeff = pd.DataFrame(model.params.round(3), columns=['Coefficient'])
        t_p_values = pd.concat([coeff,t_values, p_values,std_error], axis=1)
        test_results = pd.DataFrame()
        test_results = pd.concat([test_results, t_p_values], axis=1)

        return test_results
    
    def non_parametric_test(self,log=True,period:str='M',significance=0.05,plot=True):
        """Performs non-parametric test(Kruskal-Wallis) to check if the periods have a significant effect on the price series"""
        data = self.data.copy()
        data = np.log(data) if log else data

        data,_ = self.create_freq_column(data,period)
        # Group by week number
        groups = [group['Close'].values for name, group in data.groupby('period')]

        # Perform the Kruskal-Wallis test
        stat, p_value = stats.kruskal(*groups)

        # Output the results
        print(f'Kruskal-Wallis statistic: {stat}')
        print(f'p-value: {p_value}')
        # Interpretation
        if p_value < significance:
            print('At least one period has a significant effect on the spread')
        else:
            print('No period has a significant effect on the spread')

    def plot_annova_results(self,results):
        """Plots the results of the ANNOVA Analysis"""
        coefficients = results['Coefficient']
        print(coefficients.head())
        coefficients = coefficients.drop('Intercept')
        coefficients.plot(kind='bar', figsize=(12, 7), title='Monthly Coefficients')
        plt.ylabel('Coefficient')
        plt.xlabel('period')
        plt.xticks(rotation=45)
        plt.show()

    def check_stationarity(self):
        """Check if the series is stationary"""
        data = self.data.copy()
        self.plot_stationarity(data)
        
    def plot_stationarity(self,data):
        """Plot the stationarity of the series"""
        
        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(20, 8))
        data.plot(ax=axes[0], title='Original Series')

        axes[0].text(x=.03,
                    y=.85,
                    s=f'ADF: {tsa.adfuller(data.dropna())[1]:.4f}',
                    transform=axes[0].transAxes)
        axes[0].set_ylabel('Index')

        data_log = np.log(data)
        data_log.plot(ax=axes[1],
                    sharex=axes[0])
        axes[1].text(x=.03, 
                    y=.85,
                    s=f'ADF: {tsa.adfuller(data_log.dropna())[1]:.4f}',
                    transform=axes[1].transAxes)
        axes[1].set_ylabel('Log')
        
        data_diff = data_log.diff().dropna()
        data_diff.plot(ax=axes[2],
                    sharex=axes[0])
        axes[2].text(x=.03, y=.85,
                    s=f'ADF: {tsa.adfuller(data_diff.dropna())[1]:.4f}',
                    transform=axes[2].transAxes)
        axes[2].set_ylabel('Log Diff')  
        for ax in axes.flatten():
            ax.get_legend().remove()
        # sns.despine()
        # fig.tight_layout()
        fig.align_ylabels(axes)
        plt.show()

def SeasonalStrategy():
    """Seasonal Strategy"""

    def __init__(self,data:pd.DataFrame,non_parametric=False):

        self.analyzer = Seasonal()
        self.data = data
        if "Close" not in self.data.columns:
            raise ValueError("'Close' price column not found in the data")

    def trading_signal(self, period: str = 'M'):
        """Generates the trading signal based on the seasonal analysis"""
        analysis_df = self.analyzer.variance_analysis(self.data, period=period, plot=False)

        coeffs = analysis_df['Coefficient']

        # Identify local minima and maxima
        local_minima = (coeffs.shift(1) > coeffs) & (coeffs.shift(-1) > coeffs)
        local_maxima = (coeffs.shift(1) < coeffs) & (coeffs.shift(-1) < coeffs)

        # Generate trading signals
        signals = pd.Series(index=coeffs.index, dtype='float64')
        signals[local_minima] = 1  # Long position
        signals[local_maxima] = -1  # Short position

        # Forward fill the signals to maintain positions
        signals.ffill(inplace=True)

        return signals

if __name__ == '__main__':
    # get crude oil prices
    data = yf.download('GC=F', start='2018-01-01')
    data = data['Close'].to_frame()
    data.index = pd.to_datetime(data.index)
    seasonal = Seasonal(data, freq=250)
    #decomposition = seasonal.decompose()
    # seasonal.check_stationarity()
    analysis=seasonal.variance_analysis(period='M',log=False,plot=True)
    print(analysis['Coefficient'])
    # seasonal.non_parametric_test(period='W',log=False)
    plt.show()