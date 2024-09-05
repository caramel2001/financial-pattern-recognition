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

- 
-

## TODO

- Markov Models
- https://www.marketpsych.com/home
- Company Financial Analyszer using OpenAI
- Make a diversifier


## Existing SEC Analyzers

- https://www.edmundsec.com/
- https://www.publicview.ai/
- https://financialinsights.ai/


## Ideas

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