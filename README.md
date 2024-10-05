# Financial Market Pattern Recognition

## Setup
Ensure you have poetry installed [Poetry Docs](https://python-poetry.org/docs/).
```
poetry install # install the environment
```

## Example
```
poetry run python -m  exp.get_transcript # extract earning transcripts from Motley Fool and CapIQ for Analysis

poetry run python -m exp.openai_transcript # extract analysis using OpenAI API and pydantic to ensure structured output. Sentiment and Explanation. Need to optimize the prompt based on some hsitorical data and metrics.

poetry run python -m exp.screener  # get screened stocks from SeekingAlpha
```



## Reading

- A Multimodal Foundation Agent for Financial Trading: Tool-Augmented, Diversified, and Generalist
- Pairs trading with a mean-reverting jump-diffusion model on high-frequency data
- Stock Market Prediction Using Hidden Markov Models
- Stock Market Trend Analysis Using Hidden Markov Model and Long Short Term Memory
- Hidden Markov Models Applied To Intraday Momentum Trading With Side Information
- FactorVAE: A Probabilistic Dynamic Factor Model Based on Variational Autoencoder for Predicting Cross-Sectional Stock Returns
- Evaluation of Dynamic Cointegration-Based Pairs Trading Strategy in the Cryptocurrency Market
- Copula-Based Trading of Cointegrated Cryptocurrency Pairs
- TRADING STRATEGIES WITH COPULAS
- Deep neural networks, gradient-boosted trees, random forests: Statistical arbitrage on the S&P 500
- Financial Machine Learning
- Financial Statement Analysis with Large Language Models
- Fast Portfolio Diversification
- Deep Reinforcement Learning Approach for Trading Automation in The Stock Market
- Pattern Recognition in Financial Data Using Association Rule
- Efficient Analysis of Pattern and Association Rule Mining Approaches
- Pattern recognition using hidden Markov modelsin financial time series
- Slow Momentum with Fast Reversion: A Trading Strategy Using Deep Learning and Changepoint Detection
- FEW-SHOT LEARNING PATTERNS IN FINANCIAL TIME-SERIES FOR TREND-FOLLOWING STRATEGIES
- Trading with the Momentum Transformer: An Intelligent and Interpretable Architecture

## Data Sources

**Please help find any data source you guys are able to find for any kind of financial data useful.** 

Data Sources currently Supporting:
- CapIQ : NTU loging and Cookie Extraction based scraping. Curenlty only extracting Earnings Transcript Data
- SeekingAlpha : Screener and Earnings Transcript(US)
- Screener.in : Indian Market Fundamentals Data(Last 10 years)
- Fyers API : For Indian Market Minute and second interval data Data
- US Fundamentals data from 2010 to 2020 : https://www.kaggle.com/datasets/finnhub/reported-financials
- Coinbase for Crypto Price data

**Data Source Needed**
- Good free soruce to get US market real time fundamentals. Not sure if Yahoo Finance is reliable, AlphaVantage got Free API but limited API calls
,https://finnhub.io/docs/api/financials-reported
- https://www.macrotrends.net/stocks/charts/NVDA/nvidia/cash-flow-statement
- https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=TEN&type=10-Q&dateb=&owner=exclude&count=100
- https://discountingcashflows.com/documentation/financial-api-guide/#sec-filings
## TODO

- Markov Models
- https://www.marketpsych.com/home
- Company Financial Analyszer using OpenAI
- Make a diversifier
- Research on good Order Execution algorithm such that if we want to open a position in a company next day or within a week, we are able to execute the order optimally without adding losses to our position due daily volatility
- OpenFE

## LLM Based Analyst
- https://github.com/Athe-kunal/finance_llm_data/tree/main
- QUANTITATIVE EQUITY INVESTING FRANK J. FABOZZI, SERGIO M. FOCARDI, PETTER N. KOLM Techniques and Strategies

## Existing SEC Analyzers

- https://www.edmundsec.com/
- https://www.publicview.ai/
- https://financialinsights.ai/


## Ideas

### Chan Strats
- Buy on Gap Model for Nifty Index, NIFTYBANK INDEX, MIDCAP INDEX
- Short on Gap Model for Indexes
- Kalman Filter Mean Reversion Strategy

### Analysis on the Next trading day of the Stock that realeased their earnings or any fillings post market or pre market

- Track 10K,10Q,8K etc
   - 10K - An annual report that includes audited financial statements for a company. It includes the company's income statement, balance sheet, statement of cash flows, and statement of stockholders' equity. 
   - 10Q -  A quarterly report that includes unaudited financial statements for a company. It's filed three times a year, and is useful for stakeholders who want to - see a company's short-term changes. 
   - Annual report - A report that contains financial data, charts, illustrations, photos, and a letter from the CEO. It's geared toward shareholders. 
   - Proxy statement - A statement that allows shareholders to cast their votes using a designated person, called a proxy. 
   - Analytical report - A report that uses analytical evidence and predictive analytics technologies to generate accurate forecasts. 
   - Client report - A report that details a business's relationship with each client and their work activities. It helps the business make management decisions. 
   - 8-K - A form that's filed in the period between 10-Q filings, or in case of a significant event, such as a CEO departing or bankruptcy. 
   - Form 144 - is a document filed with the SEC by someone who intends to sell restricted or control securities, such as when an affiliate sells shares.  Valid for 90 days, and can help predict future sales. Form 144 must be filed if the investor plans to sell more than 5,000 shares or $50,000 of total stock within a three-month period.
   - Form 4 - Insiders, or those related to insiders, must file Form 4 when they actually sell the restricted stock. Form 4 is filed within two business days of the transaction. 

- Perform Intraday time series analysis on the next trading day. The assumption is the stocks which show rapid change in the market sentiments due to the reuslts from the fillings might showcase similar patterns of trading. Check whether there is any significant implications of the Report to volatility of stock price post the report release and also is there any difference based on the market sentiment of the stock.


### Momentum Based Portfolio:

- High Momentum Stock Focus: We focus on high-quality, high momentum stocks that are more likely to generate higher returns.

- Selection Process: We select 10 standout stocks from the top 500 companies based on a comprehensive evaluation of the company's fundamentals, industry position, and growth potential.

- Use of AI Technology: AI and machine learning algorithms help us identify market trends, anticipate market shifts, and adjust our portfolio strategy.

- Risk Optimization: We balance the potential for high returns with the associated risks, using sophisticated risk management strategies and techniques.

- Diversification: Even though our portfolio is concentrated, we practice diversification among our chosen 10 stocks to spread the risk - Portfolio remains well-rounded and not overly reliant on any single stock or sector.

- Systematic De-Allocation: In high-risk market scenarios, we systematically de-allocate our investments to mitigate risk exposure.



### Michael Burry's Value Stocks Screener:

To develop a stock-picking strategy based on Michael Burry's approach outlined in the write-up, you can break it down into actionable steps:

#### 1. **Understand the Investment Philosophy**
   - **Value Investing Focus:** Base stock picking on the principle of value investing, ensuring a "margin of safety" to protect against permanent capital loss.
   - **Focus on Out-of-Favor Stocks:** Look for stocks that are currently unpopular or ignored by the market but have potential for recovery.

#### 2. **Screen for Potential Investments**
   - **Use Stock Screeners:** Utilize tools like MSN MoneyCentral's Stock Screener or other screening platforms.
   - **Criteria for Screening:**
     - **Enterprise Value/EBITDA Ratio:** Focus on companies with low enterprise value-to-EBITDA ratios, but allow flexibility based on industry and economic cycle.
     - **Free Cash Flow:** Focus on companies with strong free cash flow (cash generated after operational expenses).
     - **Debt Levels:** Look for companies with minimal debt to avoid financial risk.
   - **Ignore Price-Earnings Ratios (P/E):** Burry deems P/E ratios as less meaningful.
   - **Avoid ROE (Return on Equity):** Be cautious with ROE, as it may be deceptive due to leverage.

#### 3. **Deep Dive Research**
   - **Analyze Enterprise Value:** Calculate enterprise value (EV) as market capitalization + debt - cash to assess the company's total valuation.
   - **Adjust for Off-Balance-Sheet Items:** Account for potential liabilities or assets that aren't immediately apparent on the company's balance sheet.
   - **Focus on True Free Cash Flow:** Evaluate the true free cash flow of the company to understand its capacity to generate cash.

#### 4. **Evaluate the Industry and Economic Cycle**
   - **Look at Industry Trends:** Seek out-of-favor industries with stocks that have been "thrown out with the bathwater."
   - **Best of Breed:** Focus on high-quality companies within struggling industries that may be significantly undervalued.

#### 5. **Calculate Margin of Safety**
   - **Determine Intrinsic Value:** Use your research to establish a realistic, adjusted book value and intrinsic value of the company.
   - **Buy at a Discount:** Purchase the stock only when there’s a sufficient discount (margin of safety) to protect against downside risk.

#### 6. **Portfolio Management**
   - **Diversify Across Cap Sizes and Sectors:** No restrictions on cap size (large, mid, small), sector (tech or non-tech), or industry, but only invest if clear value is identified.
   - **Ignore General Market Trends:** Don't worry about the overall level of the market; focus purely on the value of individual stocks.
   - **Watch for Catalysts (Optional):** Specific catalysts for price movement aren’t necessary, but they can provide additional comfort for potential upside.

#### 7. **Execute and Monitor the Strategy**
   - **Regularly Screen and Evaluate:** Continually use stock screening tools and fundamental analysis to discover new opportunities.
   - **Reassess Investment Thesis:** Reevaluate positions periodically to ensure they still offer value and have potential for recovery.

By following these steps, you can replicate the fundamental value-investing strategy Michael Burry uses, with a focus on free cash flow, enterprise value, and an industry-agnostic approach.