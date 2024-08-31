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
- - https://www.marketpsych.com/home
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


