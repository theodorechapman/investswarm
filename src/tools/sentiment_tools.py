"""Sentiment analysis tools"""

import re
from typing import Dict, Any


def score_sentiment(text: str) -> Dict[str, Any]:
    # Score sentiment of text from -1 (very negative) to 1 (very positive)
    if not text:
        return {
            "score": 0.0,
            "classification": "neutral",
            "confidence": 0.0
        }

    text_lower = text.lower()

    # Positive keywords
    positive_keywords = [
        "bullish", "buy", "strong", "growth", "profit", "gain", "upgrade",
        "outperform", "positive", "beat", "exceeded", "success", "innovation",
        "leader", "advantage", "opportunity", "momentum", "rally", "surge",
        "breakthrough", "excellent", "impressive", "confident", "optimistic"
    ]

    # Negative keywords
    negative_keywords = [
        "bearish", "sell", "weak", "decline", "loss", "downgrade", "miss",
        "underperform", "negative", "failed", "concern", "risk", "threat",
        "challenge", "competition", "decline", "drop", "fall", "plunge",
        "disappointing", "worry", "caution", "pessimistic", "struggle"
    ]

    # Count occurrences
    positive_count = sum(
        len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
        for word in positive_keywords
    )
    negative_count = sum(
        len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
        for word in negative_keywords
    )

    total_sentiment_words = positive_count + negative_count

    # Calculate score
    if total_sentiment_words == 0:
        score = 0.0
        confidence = 0.0
    else:
        score = (positive_count - negative_count) / total_sentiment_words
        confidence = min(total_sentiment_words / 10, 1.0) 

    # Classify
    if score > 0.2:
        classification = "bullish"
    elif score < -0.2:
        classification = "bearish"
    else:
        classification = "neutral"

    return {
        "score": round(score, 2),
        "classification": classification,
        "confidence": round(confidence, 2),
        "positive_mentions": positive_count,
        "negative_mentions": negative_count
    }


def analyze_news_sentiment(articles: list) -> Dict[str, Any]:
    if not articles:
        return {
            "overall_score": 0.0,
            "overall_classification": "neutral",
            "article_count": 0
        }

    sentiments = [score_sentiment(article) for article in articles]

    avg_score = sum(s["score"] for s in sentiments) / len(sentiments)
    avg_confidence = sum(s["confidence"] for s in sentiments) / len(sentiments)

    # Count classifications
    bullish = sum(1 for s in sentiments if s["classification"] == "bullish")
    bearish = sum(1 for s in sentiments if s["classification"] == "bearish")
    neutral = sum(1 for s in sentiments if s["classification"] == "neutral")

    if avg_score > 0.2:
        overall_classification = "bullish"
    elif avg_score < -0.2:
        overall_classification = "bearish"
    else:
        overall_classification = "neutral"

    return {
        "overall_score": round(avg_score, 2),
        "overall_classification": overall_classification,
        "confidence": round(avg_confidence, 2),
        "article_count": len(articles),
        "bullish_articles": bullish,
        "bearish_articles": bearish,
        "neutral_articles": neutral
    }
