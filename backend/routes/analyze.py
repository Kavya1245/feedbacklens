from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.data_loader import load_reviews
from services.sentiment import analyze_sentiment
from services.ai_report import generate_report

router = APIRouter()


# -------------------------------------------------
# Request Model — what the frontend sends
# -------------------------------------------------
class AnalyzeRequest(BaseModel):
    product_name: str
    product_url: Optional[str] = None
    filter_type: Optional[str] = "all"   # "all" | "recent" | "budget" | "quality"


# -------------------------------------------------
# Response Model — what the backend returns
# -------------------------------------------------
class SourceSummary(BaseModel):
    source: str
    sentiment: str
    review_count: int


class AnalyzeResponse(BaseModel):
    product: str
    overall_sentiment: str
    sentiment_score: dict           # { positive: %, neutral: %, negative: % }
    top_pros: list[str]
    top_cons: list[str]
    buy_if: str
    avoid_if: str
    verdict: str
    source_summary: list[SourceSummary]
    total_reviews: int


# -------------------------------------------------
# POST /api/analyze
# -------------------------------------------------
@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_product(request: AnalyzeRequest):
    """
    Main endpoint: accepts a product name, fetches reviews,
    runs sentiment analysis, and returns AI-generated buyer insights.
    """

    product_name = request.product_name.strip()

    if not product_name:
        raise HTTPException(status_code=400, detail="Product name cannot be empty.")

    # Step 1: Load reviews from available sources
    reviews = load_reviews(product_name, request.product_url)

    if not reviews:
        raise HTTPException(
            status_code=404,
            detail=f"No reviews found for '{product_name}'. Try a different product name."
        )

    # Step 2: Run sentiment analysis + extract keywords
    sentiment_data = analyze_sentiment(reviews)

    # Step 3: Generate AI buyer report
    report = await generate_report(product_name, sentiment_data)

    # Step 4: Build per-source summary
    source_summary = []
    for source, data in sentiment_data["by_source"].items():
        pos = data["positive"]
        neg = data["negative"]
        if pos >= 60:
            label = "Mostly Positive"
        elif neg >= 50:
            label = "Mostly Negative"
        else:
            label = "Mixed"
        source_summary.append(SourceSummary(
            source=source,
            sentiment=label,
            review_count=data["count"]
        ))

    # Step 5: Build and return final response
    return AnalyzeResponse(
        product=product_name,
        overall_sentiment=sentiment_data["overall_label"],
        sentiment_score=sentiment_data["overall_score"],
        top_pros=sentiment_data["top_pros"],
        top_cons=sentiment_data["top_cons"],
        buy_if=report["buy_if"],
        avoid_if=report["avoid_if"],
        verdict=report["verdict"],
        source_summary=source_summary,
        total_reviews=sentiment_data["total_reviews"],
    )
