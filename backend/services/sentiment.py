from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
import re

STOPWORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with","by",
    "from","into","about","after","before","through","during","without","within",
    "i","my","me","we","you","your","he","she","they","them","his","her","our",
    "its","this","that","these","those","it","is","are","was","were","be","been",
    "being","have","has","had","do","does","did","will","would","could","should",
    "may","might","get","got","gets","make","makes","made","come","comes","came",
    "take","takes","took","feel","feels","felt","look","looks","seem","seems",
    "keep","keeps","want","wants","need","needs","work","works","give","gives",
    "find","found","know","think","said","says","going","start","used","using",
    "love","like","hate","very","just","also","not","no","so","even","than",
    "more","much","too","some","any","all","few","can","only","most","many",
    "each","such","over","well","still","same","never","always","really",
    "actually","especially","easily","highly","simply","totally","already",
    "every","ever","other","another","both","whole","little","quite","rather",
    "almost","good","great","best","nice","product","item","thing","stuff",
    "overall","experience","purchase","bought","buying","review","recommend",
    "worth","price","money","value","happy","satisfied","disappointed",
    "received","arrived","delivery","order","ordered","there","here","when",
    "what","where","which","while","though","because","since","until","unless",
    "although","however","therefore","then","now","back","down","long","high",
    "old","new","first","last","next","right","left","far","use","also","even",
    "phone", "camera", "performance", "light", "screen", "device", "model",
    "version", "feature", "features", "option", "options", "issue", "issues",
    "problem", "problems", "quality", "level", "levels", "point", "points",
}

# Meaningful bigrams to extract (two-word phrases)
MEANINGFUL_BIGRAMS = [
    "noise cancellation", "noise cancelling", "battery life", "sound quality",
    "build quality", "call quality", "charging speed", "fast charging",
    "display quality", "camera quality", "low light", "heating issue",
    "bluetooth connectivity", "audio quality", "comfort level", "ear cups",
    "active noise", "touch controls", "voice assistant", "water resistant",
    "price range", "long lasting", "easy setup", "customer service",
]

analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(reviews: list[dict]) -> dict:
    if not reviews:
        return {}

    total = len(reviews)
    pos_count = neu_count = neg_count = 0
    positive_words = []
    negative_words = []
    by_source: dict[str, dict] = {}

    for review in reviews:
        text = review.get("text", "")
        source = review.get("source", "Unknown")
        scores = analyzer.polarity_scores(text)
        compound = scores["compound"]

        if compound >= 0.05:
            sentiment = "positive"
            pos_count += 1
            positive_words.extend(_extract_keywords(text))
            positive_words.extend(_extract_bigrams(text))
        elif compound <= -0.05:
            sentiment = "negative"
            neg_count += 1
            negative_words.extend(_extract_keywords(text))
            negative_words.extend(_extract_bigrams(text))
        else:
            sentiment = "neutral"
            neu_count += 1

        if source not in by_source:
            by_source[source] = {"positive": 0, "negative": 0, "neutral": 0, "count": 0}
        by_source[source][sentiment] += 1
        by_source[source]["count"] += 1

    pos_pct = round((pos_count / total) * 100)
    neu_pct = round((neu_count / total) * 100)
    neg_pct = round((neg_count / total) * 100)

    for source, data in by_source.items():
        count = data["count"]
        data["positive"] = round((data["positive"] / count) * 100)
        data["negative"] = round((data["negative"] / count) * 100)
        data["neutral"]  = round((data["neutral"]  / count) * 100)

    if pos_pct >= 60:
        label = f"Positive ({pos_pct}%)"
    elif neg_pct >= 50:
        label = f"Negative ({neg_pct}%)"
    else:
        label = f"Mixed ({pos_pct}% positive)"

    top_pros = _top_phrases(positive_words, top_n=5)
    top_cons = _top_phrases(negative_words, top_n=5)

    return {
        "overall_label": label,
        "overall_score": {"positive": pos_pct, "neutral": neu_pct, "negative": neg_pct},
        "top_pros": top_pros,
        "top_cons": top_cons,
        "total_reviews": total,
        "by_source": by_source,
        "raw_positive_words": positive_words,
        "raw_negative_words": negative_words,
    }


def _extract_keywords(text: str) -> list[str]:
    words = re.findall(r"\b[a-zA-Z]{5,}\b", text.lower())
    return [w for w in words if w not in STOPWORDS]


def _extract_bigrams(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for bigram in MEANINGFUL_BIGRAMS:
        if bigram in text_lower:
            found.append(bigram)
    return found


def _top_phrases(words: list[str], top_n: int = 5) -> list[str]:
    if not words:
        return []
    counter = Counter(words)
    return [w.title() for w, _ in counter.most_common(top_n)]