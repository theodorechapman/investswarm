

from dataclasses import dataclass
import asyncio, json
from typing import List, Dict, Any

from dedalus_labs import AsyncDedalus, DedalusRunner
from ..config import config
from ..utils.json_utils import parse_model_json


class JudgeAgent:

    def __init__(self):
        self.name = "Judge & Verdict Agent"
        self.model = "openai/gpt-5"
        self.mcp_servers: List[str] = []
        self.tools: List[Any] = []

    async def judge(self, research_results: List[Dict[str, Any]], stock_ticker: str) -> Dict[str, Any]:
        """
        Batched judging:
          1) Parallel micro-judgments (summaries, agreements/conflicts, weighing, risks/opps)
          2) Reduce to final BUY/HOLD/SELL verdict JSON
        """
        client = AsyncDedalus()
        runner = DedalusRunner(client)

        compact_inputs = []
        for r in research_results:
            compact_inputs.append({
                "agent": r.get("agent"),
                "agent_name": r.get("agent_name"),
                "status": r.get("status"),
                "analysis": r.get("analysis"),  
            })
        inputs_json = json.dumps(compact_inputs, ensure_ascii=False)

        @dataclass
        class Subtask:
            name: str
            instruction: str
            timeout_s: int = 120  

        subtasks = [
            Subtask(
                "summarize_financial",
                "Summarize the Financial agent’s core arguments, stance, and confidence (≤120 words)."
            ),
            Subtask(
                "summarize_market",
                "Summarize the Market & Product agent’s core arguments, stance, and confidence (≤120 words)."
            ),
            Subtask(
                "summarize_sentiment",
                "Summarize the Sentiment agent’s core arguments, stance, and confidence (≤120 words)."
            ),
            Subtask(
                "agreements_conflicts",
                "Identify agreements and conflicts across the three agents. Be precise and cite which agents agree/disagree."
            ),
            Subtask(
                "weigh_evidence",
                "Weigh the evidence across fundamentals, market position, and sentiment. Prioritize quantitative/verified points."
            ),
            Subtask(
                "risks_opportunities",
                "List top risks (≤5) and top opportunities (≤5) that are most decision-relevant."
            ),
        ]

        MICRO_PROMPT = """You are the investment judge for {ticker}.
You will receive a JSON array of agent analyses:
{inputs}

Task: {instruction}

Return STRICT JSON ONLY:
{{
  "summary": "≤120 words",
  "bullets": ["string", ...],
  "stance_hint": "BULLISH|BEARISH|NEUTRAL|MIXED|UNKNOWN",
  "confidence_hint": 0-10
}}
No prose outside JSON. No code fences.
"""

        async def run_subtask(subtask: Subtask):
            prompt = MICRO_PROMPT.format(ticker=stock_ticker, inputs=inputs_json, instruction=subtask.instruction)
            try:
                result = await asyncio.wait_for(
                    runner.run(
                        input=prompt,
                        model=self.model,   # keep simple; no tools/MCPs
                        stream=False
                    ),
                    timeout=subtask.timeout_s
                )
                return parse_model_json(result.final_output)
            except Exception as e:
                return {
                    "summary": f"{subtask.name} failed: {e}",
                    "bullets": [],
                    "stance_hint": "UNKNOWN",
                    "confidence_hint": 0
                }

        micro_results = await asyncio.gather(*[run_subtask(s) for s in subtasks])

        # Reduce
        reduce_prompt = f"""You are a senior portfolio manager. Synthesize the following micro-judgments for {stock_ticker}:

Micro-judgments JSON:
{json.dumps(micro_results, ensure_ascii=False)}

Produce FINAL VERDICT in STRICT JSON ONLY with this schema:
{{
  "recommendation": "BUY|HOLD|SELL",
  "conviction": 1-10,
  "timeframe": "SHORT|MEDIUM|LONG|N/A",
  "price_target": "string|N/A",
  "key_reasoning": ["3-5 bullets"],
  "main_risks": ["≤5 bullets"],
  "monitoring": ["≤5 bullets"]
}}
Guidelines:
- Be decisive but honest about uncertainty. Defer to BUY or SELL more often then HOLD.
- Use micro-judgments’ stance/confidence hints to calibrate.
- If upstream inputs were partial/missing, reflect that with lower conviction.
- No prose outside JSON. No code fences.
"""

        try:
            reduce_result = await runner.run(
                input=reduce_prompt,
                model=self.model, 
                stream=False
            )
            final_json = parse_model_json(reduce_result.final_output)
            status = "success"
        except Exception as e:
            final_json = {"error": str(e), "partials": micro_results}
            status = "partial"

        return {
            "agent": "judge",
            "agent_name": self.name,
            "verdict": final_json,
            "status": status,
            "stock_ticker": stock_ticker
        }
