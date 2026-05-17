import json
import os
from typing import Optional

# Path to the sample reviews dataset
DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/sample_reviews.json")


def load_reviews(product_name: str, product_url: Optional[str] = None) -> list[dict]:
    """
    Loads reviews for a given product from available sources.

    Priority order:
    1. [Future] Live scraping if URL is provided
    2. [Future] Reddit API live fetch
    3. Sample/offline dataset (current implementation)

    Returns a list of review dicts:
      { "source": str, "rating": int, "text": str }
    """

    # --- Try offline dataset first (always works, no API key needed) ---
    offline_reviews = _load_from_dataset(product_name)

    if offline_reviews:
        print(f"[DataLoader] Found {len(offline_reviews)} reviews in offline dataset for: '{product_name}'")
        return offline_reviews

    # --- Placeholder: future live sources ---
    # live_reviews = scrape_amazon(product_url)
    # reddit_reviews = fetch_reddit(product_name)
    # return live_reviews + reddit_reviews

    print(f"[DataLoader] No reviews found for: '{product_name}'")
    return []


def _load_from_dataset(product_name: str) -> list[dict]:
    """
    Loads reviews from the local sample_reviews.json file.
    Does a fuzzy match on product name (case-insensitive, partial match).
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("[DataLoader] ERROR: sample_reviews.json not found.")
        return []

    products = data.get("products", {})
    query = product_name.lower().strip()

    # Try exact match first
    if query in products:
        return products[query]["reviews"]

    # Try partial match (e.g., "sony headphones" matches "sony wh-1000xm5")
    for key in products:
        # Check if any word from the query appears in the key
        query_words = query.split()
        if any(word in key for word in query_words if len(word) > 3):
            print(f"[DataLoader] Fuzzy matched '{query}' → '{key}'")
            return products[key]["reviews"]

    return []
