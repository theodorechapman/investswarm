multi-agent system powered by [Dedalus Labs](https://dedaluslabs.ai) that analyzes stocks from three different perspectives in parallel, then synthesizes the research through a debate judged by a final LLM.

Overview
1. Financial Analysis Agent - Analyzes financial statements, ratios, profitability, cash flow, and balance sheet strength
2. Market & Product Analysis Agent - Evaluates market position, competitive landscape, product strength, and economic moat
3. Sentiment Analysis Agent - Assesses news sentiment, analyst ratings, social media, and insider activity
4. Judge Agent - Synthesizes all research, identifies agreements/conflicts, and provides a final investment verdict

Prerequisites
- Python 3.8 or higher
- Dedalus API key (get one at [dedaluslabs.ai](https://dedaluslabs.ai))

Use:
- python main.py TSLA                    # analyze Tesla stock
- python main.py AAPL -o results.json    # analyze Apple and save to file
- python main.py MSFT --show-research    # show detailed research from all agents
- python main.py NVDA -q                 # only show verdict

Financial Analysis Agent
- Model: GPT-5
- MCP Server: Brave Search
- Focus: Balance sheets, income statements, cash flow, profitability, debt levels

Market & Product Analysis Agent
- Model: GPT-5
- MCP Servers: Brave Search, Exa (semantic search)
- Focus: Market size, competitive landscape, product differentiation, economic moat

Sentiment Analysis Agent
- Model: GPT-5
- MCP Servers: Brave Search, Exa
- **Focus**: News sentiment, analyst ratings, social media, insider activity

Judge Agent
- Models: GPT-5 to Claude Sonnet handoff
- Process: Synthesizes research, identifies conflicts, weighs evidence, provides verdict
- Output: BUY/HOLD/SELL recommendation with confidence level & reasoning

Acknowledgments
- Built with [Dedalus Labs](https://dedaluslabs.ai) SDK
- Powered by OpenAI GPT-5 and Anthropic Claude
- MCP servers by Windsor and Joerup
