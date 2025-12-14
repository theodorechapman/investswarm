"""Sentiment Analysis Agent."""
from ..utils.json_utils import parse_model_json
from dataclasses import dataclass
import asyncio
import json
from typing import Dict, Any

from dedalus_labs import AsyncDedalus, DedalusRunner
from ..config import config
from ..tools import score_sentiment, analyze_news_sentiment


class SentimentAgent:

    def __init__(self):
        self.name = "Sentiment Analysis Agent"
        self.model = config.sentiment_model
        self.mcp_servers = [config.brave_search_mcp, config.exa_mcp]
        self.tools = [score_sentiment, analyze_news_sentiment]

    async def analyze(self, stock_ticker: str) -> Dict[str, Any]:
        @dataclass
        class Subtask:
            name: str
            instruction: str
            timeout_s: int = 200

        subtasks = [
            Subtask("news_30d", "Aggregate last 30 days of news tone, key headlines, and trend direction; compute an overall news score."),
            Subtask("analyst", "Summarize recent analyst ratings/changes and price targets; compute a consensus tilt."),
            Subtask("social_retail", "Summarize social/retail chatter and velocity; indicate bullish/bearish/neutral with rationale."),
            Subtask("insiders", "Summarize recent insider transactions and governance signals; indicate alignment or concern."),
            Subtask("derivatives", "Summarize options/short-interest (put/call, SI %) and what it implies about positioning."),
            Subtask("catalysts", "List near-term catalysts (earnings, product, regulatory) and expected sentiment impact."),
        ]

        MICRO_PROMPT = """You are a sentiment analysis expert for {ticker}.
Task: {instruction}
Return STRICT JSON:
{{
  "summary": "≤120 words",
  "metrics": [{{"name": "string", "value": "string"}}],
  "strengths": ["string", ...],
  "weaknesses": ["string", ...],
  "stance": "BULLISH|BEARISH|NEUTRAL",
  "confidence": 0-10
}}
Only JSON. No prose outside the JSON.
"""

        async def run_subtask(runner, subtask: Subtask):
            prompt = MICRO_PROMPT.format(ticker=stock_ticker, instruction=subtask.instruction)
            try:
                result = await asyncio.wait_for(
                    runner.run(
                        input=prompt,
                        model=self.model,
                        tools=self.tools,
                        mcp_servers=self.mcp_servers,
                        stream=False,
                    ),
                    timeout=subtask.timeout_s,
                )
                return parse_model_json(result.final_output)
            except Exception as e:
                return {
                    "summary": f"{subtask.name} failed: {e}",
                    "metrics": [],
                    "strengths": [],
                    "weaknesses": [],
                    "stance": "NEUTRAL",
                    "confidence": 0,
                }

        client = AsyncDedalus()
        runner = DedalusRunner(client)
        micro_results = await asyncio.gather(*[run_subtask(runner, s) for s in subtasks])

        # reduce
        reduce_prompt = f"""You are the sentiment judge synthesizing multiple partial analyses of {stock_ticker}.
Input JSON list below. Summarize overlaps/conflicts and output final structured JSON:
{{
  "overall_summary": "≤150 words",
  "news_headlines": ["≤5 bullets"],
  "analyst_consensus": "BUY|HOLD|SELL|MIXED|UNKNOWN",
  "overall_stance": "BULLISH|BEARISH|NEUTRAL",
  "confidence": 0-10,
  "key_risks": ["≤5 bullets"],
  "upcoming_catalysts": ["≤5 bullets"]
}}
Input:
{json.dumps(micro_results, ensure_ascii=False)}
Return only JSON.
"""

        try:
            reduce_result = await runner.run(
                input=reduce_prompt,
                model=self.model, 
                stream=False,
            )
            final_json = parse_model_json(reduce_result.final_output)
            status = "success"
        except Exception as e:
            final_json = {"error": str(e), "partials": micro_results}
            status = "partial"

        return {
            "agent": "sentiment",
            "agent_name": self.name,
            "analysis": final_json,
            "status": status,
        }
