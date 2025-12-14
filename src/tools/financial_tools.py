"""Financial analysis tools."""

from typing import Dict, Any


def calculate_financial_ratios(
    revenue: float,
    net_income: float,
    total_assets: float,
    total_debt: float,
    equity: float,
    shares_outstanding: float,
) -> Dict[str, Any]:
    try:
        ratios = {}

        # Profitability ratios
        if revenue > 0:
            ratios["profit_margin"] = (net_income / revenue) * 100
        else:
            ratios["profit_margin"] = 0

        if equity > 0:
            ratios["roe"] = (net_income / equity) * 100  # Return on Equity
        else:
            ratios["roe"] = 0

        if total_assets > 0:
            ratios["roa"] = (net_income / total_assets) * 100  # Return on Assets
        else:
            ratios["roa"] = 0

        # Leverage ratios
        if equity > 0:
            ratios["debt_to_equity"] = total_debt / equity
        else:
            ratios["debt_to_equity"] = float('inf') if total_debt > 0 else 0

        if total_assets > 0:
            ratios["debt_ratio"] = total_debt / total_assets
        else:
            ratios["debt_ratio"] = 0

        # Per-share metrics
        if shares_outstanding > 0:
            ratios["eps"] = net_income / shares_outstanding  # EPS
            ratios["book_value_per_share"] = equity / shares_outstanding
        else:
            ratios["eps"] = 0
            ratios["book_value_per_share"] = 0

        return ratios

    except Exception as e:
        return {"error": f"Error calculating ratios: {str(e)}"}


def calculate_valuation_metrics(
    market_cap: float,
    revenue: float,
    net_income: float,
    ebitda: float,
    total_debt: float,
    cash: float,
) -> Dict[str, Any]:
    try:
        metrics = {}

        # Enterprise Value
        enterprise_value = market_cap + total_debt - cash
        metrics["enterprise_value"] = enterprise_value

        # Valuation multiples
        if net_income > 0:
            metrics["pe_ratio"] = market_cap / net_income
        else:
            metrics["pe_ratio"] = None

        if revenue > 0:
            metrics["price_to_sales"] = market_cap / revenue
            if enterprise_value > 0:
                metrics["ev_to_sales"] = enterprise_value / revenue
        else:
            metrics["price_to_sales"] = None
            metrics["ev_to_sales"] = None

        if ebitda > 0 and enterprise_value > 0:
            metrics["ev_to_ebitda"] = enterprise_value / ebitda
        else:
            metrics["ev_to_ebitda"] = None

        return metrics

    except Exception as e:
        return {"error": f"Error calculating valuation metrics: {str(e)}"}


def analyze_growth_trends(
    revenue_history: list,
    net_income_history: list,
    periods: int = 3
) -> Dict[str, Any]:
    try:
        trends = {}

        # Revenue growth
        if len(revenue_history) >= 2:
            recent_revenue = revenue_history[-1]
            old_revenue = revenue_history[-min(periods + 1, len(revenue_history))]

            if old_revenue > 0:
                trends["revenue_growth_rate"] = (
                    (recent_revenue - old_revenue) / old_revenue
                ) * 100
            else:
                trends["revenue_growth_rate"] = 0

            if len(revenue_history) >= periods + 1:
                years = periods
                trends["revenue_cagr"] = (
                    ((recent_revenue / old_revenue) ** (1 / years) - 1) * 100
                )

        # Net income growth
        if len(net_income_history) >= 2:
            recent_income = net_income_history[-1]
            old_income = net_income_history[-min(periods + 1, len(net_income_history))]

            if old_income > 0:
                trends["income_growth_rate"] = (
                    (recent_income - old_income) / old_income
                ) * 100
            else:
                trends["income_growth_rate"] = 0

        return trends

    except Exception as e:
        return {"error": f"Error analyzing growth trends: {str(e)}"}
