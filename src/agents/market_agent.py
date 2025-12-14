"""Market and Product Analysis Agent."""
from ..utils.json_utils import parse_model_json
from dataclasses import dataclass
import asyncio
import json
from typing import Dict, Any

from dedalus_labs import AsyncDedalus, DedalusRunner
from ..config import config


class MarketAgent:

    def __init__(self):
        self.name = "Market & Product Analysis Agent"
        self.model = config.market_model
        self.mcp_servers = [config.brave_search_mcp, config.exa_mcp]
        self.tools = []  

    async def analyze(self, stock_ticker: str) -> Dict[str, Any]:
        @dataclass
        class Subtask:
            name: str
            instruction: str
            timeout_s: int = 200

        subtasks = [
            Subtask("market_size", "Estimate TAM/SAM/SOM and market growth rate; include latest 2025 comps if available."),
            Subtask("competition", "Identify key competitors, relative shares, differentiators, and threat level."),
            Subtask("product", "Evaluate core products/services, roadmap/innovation cadence, and customer satisfaction signals."),
            Subtask("moat", "Assess moat (network effects, brand, IP, cost/switching/regulatory advantages); rate wide/narrow/none."),
            Subtask("growth_ops", "Outline growth vectors: geo expansion, new SKUs, partnerships, M&A; add near-term catalysts."),
            Subtask("risks", "Highlight principal market risks: saturation, disruption, regulatory, pricing pressure."),
        ]

        MICRO_PROMPT = """You are a market and product analysis expert analyzing {ticker}.
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

        # Reduce
        reduce_prompt = f"""You are the market judge synthesizing multiple partial analyses of {stock_ticker}.
Input JSON list below. Summarize overlaps/conflicts and output final structured JSON:
{{
  "overall_summary": "≤150 words",
  "key_strengths": ["≤5 bullets"],
  "key_weaknesses": ["≤5 bullets"],
  "moat": "WIDE|NARROW|NONE|UNCERTAIN",
  "overall_stance": "BULLISH|BEARISH|NEUTRAL",
  "confidence": 0-10
}}
Input:
{json.dumps(micro_results, ensure_ascii=False)}
Return only JSON.
"""

        try:
            reduce_result = await runner.run(
                input=reduce_prompt,
                model="openai/gpt-5",
                stream=False
            )
            final_json = parse_model_json(reduce_result.final_output)
            status = "success"
        except Exception as e:
            final_json = {"error": str(e), "partials": micro_results}
            status = "partial"

        return {
            "agent": "market",
            "agent_name": self.name,
            "analysis": final_json,
            "status": status,
        }
