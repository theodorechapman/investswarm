import asyncio
from typing import Dict, Any, List
from datetime import datetime

from .agents import FinancialAgent, MarketAgent, SentimentAgent, JudgeAgent
from .utils.logger import logger


class InvestSwarm:
    def __init__(self):
        self.financial_agent = FinancialAgent()
        self.market_agent = MarketAgent()
        self.sentiment_agent = SentimentAgent()
        self.judge_agent = JudgeAgent()

    async def analyze_stock(self, stock_ticker: str, verbose: bool = True) -> Dict[str, Any]:
        start_time = datetime.now()
        stock_ticker = stock_ticker.upper()

        if verbose:
            logger.info(f"\n{'=' * 80}")
            logger.info(f"InvestSwarm Analysis: {stock_ticker}")
            logger.info(f"{'=' * 80}\n")
            logger.info("Starting parallel research with 3 specialized agents...\n")

        # Phase 1: Run research agents in parallel
        try:
            research_results = await asyncio.gather(
                self._run_financial_analysis(stock_ticker, verbose),
                self._run_market_analysis(stock_ticker, verbose),
                self._run_sentiment_analysis(stock_ticker, verbose),
                return_exceptions=True,
            )

            keys_in_order = [
                ("financial", "Financial Analysis Agent"),
                ("market", "Market & Product Analysis Agent"),
                ("sentiment", "Sentiment Analysis Agent"),
            ]

            results_map: Dict[str, Dict[str, Any]] = {}
            for (key, pretty), result in zip(keys_in_order, research_results):
                if isinstance(result, Exception):
                    logger.error(f"Error in {key} agent: {str(result)}")
                    results_map[key] = {
                        "agent": key,
                        "agent_name": pretty,
                        "analysis": f"Error: {str(result)}",
                        "status": "error",
                    }
                else:
                    results_map[key] = result

        except Exception as e:
            logger.error(f"Critical error during research phase: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "stock_ticker": stock_ticker,
            }

        if verbose:
            logger.info("\n" + "=" * 80)
            logger.info("Research phase complete. Starting judge agent...")
            logger.info("=" * 80 + "\n")

        ordered_results: List[Dict[str, Any]] = [
            results_map["financial"],
            results_map["market"],
            results_map["sentiment"],
        ]

        try:
            verdict_result = await self.judge_agent.judge(ordered_results, stock_ticker)
            if verbose:
                status = "✓" if verdict_result.get("status") == "success" else "✗"
                logger.info(f"Judge Agent complete {status}\n")
        except Exception as e:
            logger.error(f"Error in judge agent: {str(e)}")
            verdict_result = {
                "agent": "judge",
                "agent_name": "Judge & Verdict Agent",
                "verdict": f"Error during judgment: {str(e)}",
                "status": "error",
                "stock_ticker": stock_ticker,
            }

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        if verbose:
            logger.info("\n" + "=" * 80)
            logger.info(f"Analysis complete in {duration:.2f} seconds")
            logger.info("=" * 80 + "\n")

        # Compile final output
        return {
            "status": "success",
            "stock_ticker": stock_ticker,
            "timestamp": start_time.isoformat(),
            "duration_seconds": duration,
            "research": {
                "financial": results_map["financial"],
                "market": results_map["market"],
                "sentiment": results_map["sentiment"],
            },
            "verdict": verdict_result,
        }

    async def _run_financial_analysis(self, stock_ticker: str, verbose: bool) -> Dict[str, Any]:
        if verbose:
            logger.info("[1/3] Financial Analysis Agent starting...")
        result = await self.financial_agent.analyze(stock_ticker)
        if verbose:
            status = "O" if result["status"] == "success" else "X"
            logger.info(f"[1/3] Financial Analysis Agent complete {status}\n")
        return result

    async def _run_market_analysis(self, stock_ticker: str, verbose: bool) -> Dict[str, Any]:
        if verbose:
            logger.info("[2/3] Market & Product Analysis Agent starting...")
        result = await self.market_agent.analyze(stock_ticker)
        if verbose:
            status = "O" if result["status"] == "success" else "X"
            logger.info(f"[2/3] Market & Product Analysis Agent complete {status}\n")
        return result

    async def _run_sentiment_analysis(self, stock_ticker: str, verbose: bool) -> Dict[str, Any]:
        if verbose:
            logger.info("[3/3] Sentiment Analysis Agent starting...")
        result = await self.sentiment_agent.analyze(stock_ticker)
        if verbose:
            status = "O" if result["status"] == "success" else "X"
            logger.info(f"[3/3] Sentiment Analysis Agent complete {status}\n")
        return result


async def analyze_stock(stock_ticker: str, verbose: bool = True) -> Dict[str, Any]:
    swarm = InvestSwarm()
    return await swarm.analyze_stock(stock_ticker, verbose)
