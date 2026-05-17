import os
import anthropic

# Initialize Anthropic client
client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


async def generate_report(product_name: str, sentiment_data: dict) -> dict:
    """
    Calls Claude API to generate a buyer-centric insight report
    based on the aggregated sentiment data.

    Returns:
    {
      "buy_if": "...",
      "avoid_if": "...",
      "verdict": "..."
    }
    """

    # Build a prompt with all the sentiment context
    pros = ", ".join(sentiment_data.get("top_pros", []))
    cons = ", ".join(sentiment_data.get("top_cons", []))
    overall = sentiment_data.get("overall_label", "Mixed")
    total = sentiment_data.get("total_reviews", 0)

    prompt = f"""
You are a product review analyst helping online buyers make informed decisions.

Based on the following aggregated review data for the product "{product_name}", generate a short, clear, buyer-friendly insight report.

REVIEW DATA:
- Total reviews analyzed: {total}
- Overall sentiment: {overall}
- Top positive keywords (what buyers liked): {pros if pros else "N/A"}
- Top negative keywords (common complaints): {cons if cons else "N/A"}

Generate exactly 3 outputs in this format (no markdown, no extra text):

BUY_IF: [One sentence describing the ideal buyer - who will love this product]
AVOID_IF: [One sentence describing who should NOT buy this product]
VERDICT: [2-3 sentences. An honest, balanced summary a first-time buyer would appreciate. Mention the key strength and the key weakness.]

Keep the language simple, direct, and helpful. No fluff.
"""

    try:
        message = await client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text.strip()
        return _parse_report(response_text)

    except Exception as e:
        print(f"[AI Report] Claude API error: {e}")
        # Graceful fallback if API call fails
        return _fallback_report(product_name, sentiment_data)


def _parse_report(text: str) -> dict:
    """
    Parses Claude's response into structured fields.
    Expected format:
      BUY_IF: ...
      AVOID_IF: ...
      VERDICT: ...
    """
    result = {"buy_if": "", "avoid_if": "", "verdict": ""}

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("BUY_IF:"):
            result["buy_if"] = line.replace("BUY_IF:", "").strip()
        elif line.startswith("AVOID_IF:"):
            result["avoid_if"] = line.replace("AVOID_IF:", "").strip()
        elif line.startswith("VERDICT:"):
            result["verdict"] = line.replace("VERDICT:", "").strip()

    # If parsing fails, return raw text as verdict
    if not result["verdict"]:
        result["verdict"] = text

    return result


def _fallback_report(product_name: str, sentiment_data: dict) -> dict:
    overall = sentiment_data.get("overall_label", "Mixed")
    pros = sentiment_data.get("top_pros", [])
    cons = sentiment_data.get("top_cons", [])
    total = sentiment_data.get("total_reviews", 0)

    # Build meaningful sentences from top keywords
    pros_str = ", ".join(pros[:3]).lower() if pros else "strong performance"
    cons_str = ", ".join(cons[:3]).lower() if cons else "some limitations"

    buy_if = f"You prioritize {pros_str} and want a reliable everyday option."
    avoid_if = f"You are sensitive to issues around {cons_str}."
    verdict = (
        f"Based on {total} reviews across multiple sources, {product_name} shows "
        f"{overall} sentiment. "
        f"Buyers consistently highlight {pros_str} as standout strengths. "
        f"However, some users report concerns about {cons_str}. "
        f"Overall a solid choice for the right buyer."
    )

    return {"buy_if": buy_if, "avoid_if": avoid_if, "verdict": verdict}