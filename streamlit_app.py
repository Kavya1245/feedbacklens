import streamlit as st
import json
import os
import re
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import anthropic

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FeedbackLens — AI Product Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

/* Global */
html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: #0a0a0f; color: #f0f0f8; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 900px; }

/* Hero */
.hero-tag {
    display: inline-block;
    background: #1a1a2e;
    border: 1px solid #e8ff47;
    border-radius: 100px;
    padding: 4px 14px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #e8ff47;
    margin-bottom: 16px;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.1;
    color: #f0f0f8;
    margin-bottom: 10px;
}
.hero-title span { color: #e8ff47; font-style: italic; }
.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    color: #6b6b88;
    margin-bottom: 32px;
}

/* Cards */
.card {
    background: #13131c;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 16px;
}
.card-accent-green { border-top: 3px solid #47ff8a; }
.card-accent-red   { border-top: 3px solid #ff5f5f; }
.card-accent-yellow{ border-top: 3px solid #e8ff47; }

/* Section labels */
.section-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #6b6b88;
    margin-bottom: 14px;
}

/* Sentiment badge */
.badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 100px;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    font-weight: 600;
}
.badge-pos { background: rgba(71,255,138,0.12); color: #47ff8a; border: 1px solid rgba(71,255,138,0.25); }
.badge-neg { background: rgba(255,95,95,0.12);  color: #ff5f5f; border: 1px solid rgba(255,95,95,0.25); }
.badge-mix { background: rgba(255,201,71,0.12); color: #ffc947; border: 1px solid rgba(255,201,71,0.25); }

/* Tags */
.tag-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.tag-pro {
    background: rgba(71,255,138,0.1); color: #47ff8a;
    border: 1px solid rgba(71,255,138,0.2);
    border-radius: 100px; padding: 5px 14px;
    font-family: 'DM Mono', monospace; font-size: 12px;
}
.tag-con {
    background: rgba(255,95,95,0.1); color: #ff5f5f;
    border: 1px solid rgba(255,95,95,0.2);
    border-radius: 100px; padding: 5px 14px;
    font-family: 'DM Mono', monospace; font-size: 12px;
}

/* Buy/Avoid blocks */
.buy-block {
    background: rgba(71,255,138,0.06);
    border: 1px solid rgba(71,255,138,0.15);
    border-radius: 12px; padding: 18px 20px;
}
.avoid-block {
    background: rgba(255,95,95,0.06);
    border: 1px solid rgba(255,95,95,0.15);
    border-radius: 12px; padding: 18px 20px;
}
.buy-label   { color: #47ff8a; font-size: 10px; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 8px; }
.avoid-label { color: #ff5f5f; font-size: 10px; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 8px; }
.rec-text    { color: #f0f0f8; font-size: 14px; line-height: 1.6; }

/* Verdict */
.verdict-text {
    font-size: 1.1rem;
    line-height: 1.7;
    color: #d0d0e8;
    font-style: italic;
    border-left: 3px solid #e8ff47;
    padding-left: 18px;
    margin-top: 10px;
}

/* Source rows */
.source-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #0f0f18;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
}
.source-name { color: #f0f0f8; font-weight: 500; }
.source-count { color: #6b6b88; font-size: 11px; margin-left: 8px; }

/* Product header */
.product-title {
    font-size: 2rem;
    font-weight: 800;
    color: #f0f0f8;
    margin-bottom: 6px;
}
.product-meta {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: #6b6b88;
}

/* Divider */
.divider { border: none; border-top: 1px solid #1e1e2e; margin: 24px 0; }

/* Pill buttons row */
.pill-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px; }
.pill-btn {
    background: #13131c;
    border: 1px solid #1e1e2e;
    border-radius: 100px;
    padding: 6px 14px;
    font-size: 12px;
    color: #6b6b88;
    cursor: pointer;
    font-family: 'DM Mono', monospace;
}
.pill-btn:hover { border-color: #e8ff47; color: #e8ff47; }

/* Footer */
.footer {
    text-align: center;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #2a2a3e;
    margin-top: 60px;
    letter-spacing: 0.1em;
}
</style>
""", unsafe_allow_html=True)

# ── DATA ─────────────────────────────────────────────────────────────────────
REVIEWS_DATA = {
    "sony wh-1000xm5": [
        {"source": "Amazon", "rating": 5, "text": "Absolutely the best noise cancelling headphones I have ever used. The ANC is phenomenal and the sound quality is top notch. Battery lasts all day easily."},
        {"source": "Amazon", "rating": 4, "text": "Great sound quality, very comfortable for long hours. Worth every penny for an audiophile. Battery life is impressive."},
        {"source": "Amazon", "rating": 3, "text": "Good headphones but the hinge feels fragile. Sound quality is excellent though."},
        {"source": "Amazon", "rating": 2, "text": "Had connectivity issues with my laptop. Keeps dropping the Bluetooth connection every few minutes. Very frustrating experience."},
        {"source": "Amazon", "rating": 5, "text": "Perfect for long flights. The noise cancellation blocks out everything. Super comfortable even after 8 hours of continuous use."},
        {"source": "Flipkart", "rating": 5, "text": "Best headphones in this price range. Call quality is very clear. Noise cancellation is outstanding."},
        {"source": "Flipkart", "rating": 4, "text": "Sound quality is crisp and clear. Noise cancellation works brilliantly in office environments and busy cafes."},
        {"source": "Flipkart", "rating": 1, "text": "Very disappointed. Ear cups started peeling after 3 months. Poor build quality for such expensive headphones."},
        {"source": "Flipkart", "rating": 5, "text": "Excellent noise cancellation and battery life. Blocks out all traffic noise during daily commute perfectly."},
        {"source": "Reddit", "rating": 5, "text": "XM5 blew me away. Coming from Bose QC45, the active noise cancellation is on another level. Sound quality is outstanding."},
        {"source": "Reddit", "rating": 4, "text": "Great headphones overall. No IP rating so cannot use during workouts. For daily commute it is absolutely perfect."},
        {"source": "Reddit", "rating": 2, "text": "The companion app is buggy on Android. Keeps crashing and resetting EQ settings. Bluetooth connectivity drops sometimes."},
        {"source": "Reddit", "rating": 5, "text": "Battery life is incredible. Noise cancellation is the best I have ever tested on any headphones."},
        {"source": "Review Blog", "rating": 5, "text": "Top pick for premium headphones. Unmatched noise cancellation, 30-hour battery life, and lush sound quality make this the go-to for professionals and travelers."},
        {"source": "Review Blog", "rating": 5, "text": "After testing over 50 headphones, the XM5 remains our editor choice. Active noise cancellation technology is simply unmatched."},
    ],
    "samsung galaxy s24": [
        {"source": "Amazon", "rating": 5, "text": "Best Android phone I have ever used. Camera quality is incredible especially in low light photography. Battery life lasts a full day."},
        {"source": "Amazon", "rating": 4, "text": "Great performance, smooth display and fast charging. AI features are actually useful unlike gimmicks on other phones."},
        {"source": "Amazon", "rating": 3, "text": "Good phone but gets warm under load. Gaming for 30 minutes and it is noticeably hot to touch."},
        {"source": "Amazon", "rating": 2, "text": "Camera is oversharpened. Photos look artificial and heavily processed. Low light performance is disappointing."},
        {"source": "Amazon", "rating": 5, "text": "Display quality is stunning. The 120Hz refresh rate makes everything smooth. Camera system is versatile and powerful."},
        {"source": "Flipkart", "rating": 5, "text": "Flagship experience at its finest. One UI is smooth and blazing fast. Love the premium titanium frame build quality."},
        {"source": "Flipkart", "rating": 4, "text": "Very good all-rounder. Circle to Search feature is genuinely useful. Build quality feels extremely premium."},
        {"source": "Flipkart", "rating": 1, "text": "Heating issue is very real. Cannot play games for more than 20 minutes without the phone becoming uncomfortably hot."},
        {"source": "Flipkart", "rating": 3, "text": "Decent phone but Samsung bloatware is very annoying. Too many pre-installed apps that cannot be removed."},
        {"source": "Reddit", "rating": 5, "text": "Camera zoom capabilities are insane. Travel photography is a completely upgraded experience now with this phone."},
        {"source": "Reddit", "rating": 4, "text": "Camera quality especially in low light is genuinely impressive and competitive with much more expensive phones."},
        {"source": "Reddit", "rating": 2, "text": "Thermal throttling is a real problem during extended gaming. Processor slows down significantly to manage heat."},
        {"source": "Review Blog", "rating": 4, "text": "Samsung Galaxy S24 delivers on almost every front. AI features set it apart but heating under sustained load remains a notable concern."},
        {"source": "Review Blog", "rating": 5, "text": "Best Samsung phone in years. Improved camera system, cleaner software, and excellent display quality. Our top Android recommendation."},
    ],
    "instant pot duo 7-in-1": [
        {"source": "Amazon", "rating": 5, "text": "Changed my life completely. I cook meals in 20 minutes that used to take 2 hours. Pressure cooking is a game changer for busy families."},
        {"source": "Amazon", "rating": 5, "text": "Best kitchen appliance ever. Easy to clean, multiple cooking functions, and very reliable. Using it almost every day."},
        {"source": "Amazon", "rating": 4, "text": "Great product overall. Slight learning curve at first but cooking becomes incredibly fast and convenient."},
        {"source": "Amazon", "rating": 3, "text": "Decent but the rubber seal starts to smell after a few months. Need to clean it thoroughly to avoid odour between dishes."},
        {"source": "Amazon", "rating": 2, "text": "Lid locking mechanism broke after 6 months of regular use. Customer service was very slow to respond."},
        {"source": "Flipkart", "rating": 5, "text": "Must have for Indian cooking. Dal, biryani, and curries come out perfect every time. Saves so much time and gas."},
        {"source": "Flipkart", "rating": 4, "text": "Very good multi-cooker. Build quality is solid and the inner pot is easy to clean. Worth every rupee spent."},
        {"source": "Flipkart", "rating": 5, "text": "Excellent product. Pressure cooking cuts cooking time dramatically. Made rajma in 25 minutes. Outstanding performance."},
        {"source": "Reddit", "rating": 4, "text": "Solid appliance with great versatility. The saute function is underrated. Full replacement for a pot and slow cooker."},
        {"source": "Reddit", "rating": 5, "text": "Life changing kitchen tool. Chicken stock that used to take 8 hours now takes 90 minutes with incredible flavour."},
        {"source": "Review Blog", "rating": 5, "text": "Instant Pot Duo remains our top pick for home pressure cookers. Versatile, durable, and genuinely time-saving for busy home cooks."},
    ],
    "apple airpods pro 2": [
        {"source": "Amazon", "rating": 5, "text": "Incredible noise cancellation for such small earbuds. Sound quality is detailed and rich. Battery life with the case lasts me an entire week."},
        {"source": "Amazon", "rating": 4, "text": "Best earbuds I have ever owned. Transparency mode sounds completely natural. Comfortable fit for hours of continuous listening."},
        {"source": "Amazon", "rating": 3, "text": "Great sound quality but very expensive. The fit does not work perfectly for everyone. Ears get tired after 2 hours."},
        {"source": "Amazon", "rating": 2, "text": "One earbud stopped working after just 4 months. Unacceptable at this premium price point."},
        {"source": "Amazon", "rating": 5, "text": "Adaptive audio feature is brilliant. Seamless integration with iPhone and Mac is unmatched by any competitor."},
        {"source": "Flipkart", "rating": 5, "text": "Outstanding earbuds with premium build quality. Compact case charges wirelessly. Noise cancellation blocks out everything."},
        {"source": "Flipkart", "rating": 4, "text": "Excellent sound quality and comfortable fit. Touch controls are intuitive and responsive. Battery life is good for daily commuting."},
        {"source": "Flipkart", "rating": 2, "text": "Way too expensive for the battery life you get. Only 6 hours per charge is disappointing compared to competitors."},
        {"source": "Reddit", "rating": 5, "text": "Coming from original AirPods Pro the upgrade is massive. Noise cancellation improvement is dramatic. Absolutely worth it."},
        {"source": "Reddit", "rating": 4, "text": "Excellent earbuds but truly great only if you are in the Apple ecosystem. iPhone and Mac integration is seamless."},
        {"source": "Reddit", "rating": 3, "text": "Sound quality is very good but fit is hit or miss. The ear tips do not work perfectly for everyone."},
        {"source": "Review Blog", "rating": 5, "text": "AirPods Pro 2 set the standard for premium wireless earbuds. Best-in-class noise cancellation and seamless Apple integration."},
    ],
    "oneplus nord ce 3": [
        {"source": "Amazon", "rating": 4, "text": "Excellent value for money smartphone. Performance is smooth for daily tasks and camera produces sharp detailed photos in good lighting."},
        {"source": "Amazon", "rating": 5, "text": "Best budget phone in this price segment. Fast charging is incredibly quick and battery lasts comfortably through a full day of heavy usage."},
        {"source": "Amazon", "rating": 3, "text": "Good phone for the price but camera performance in low light is quite disappointing and produces noisy grainy images."},
        {"source": "Amazon", "rating": 2, "text": "Heating issues during gaming sessions. Phone gets uncomfortably warm after just 20 minutes of playing demanding games."},
        {"source": "Flipkart", "rating": 5, "text": "Outstanding value smartphone. Smooth performance, excellent fast charging, and clean OxygenOS software. Highly recommended."},
        {"source": "Flipkart", "rating": 4, "text": "Great mid-range phone with premium feel. Display is bright and vibrant. Battery life with 80W fast charging is a major advantage."},
        {"source": "Flipkart", "rating": 3, "text": "Decent phone overall but software updates have been slow and inconsistent. Needs better long-term software support."},
        {"source": "Reddit", "rating": 4, "text": "Solid budget option that punches well above its price. Fast charging from zero to full in under 30 minutes is genuinely impressive."},
        {"source": "Reddit", "rating": 3, "text": "Camera quality is inconsistent. Great shots in daylight but terrible low light performance makes it unsuitable for evening photography."},
        {"source": "Review Blog", "rating": 4, "text": "OnePlus Nord CE 3 delivers impressive performance for its competitive price. The 80W fast charging and smooth display make it one of the best value propositions in the mid-range segment."},
    ],
    "lg oled c3 tv": [
        {"source": "Amazon", "rating": 5, "text": "Most stunning picture quality I have ever seen on any television. The blacks are absolutely perfect and colors are incredibly vibrant. Gaming performance with low input lag is outstanding."},
        {"source": "Amazon", "rating": 5, "text": "Worth every penny. OLED display makes streaming content look cinematic. HDR content looks absolutely breathtaking."},
        {"source": "Amazon", "rating": 4, "text": "Excellent TV with stunning picture quality. Only concern is potential burn-in risk with static content over long time."},
        {"source": "Amazon", "rating": 3, "text": "Picture quality is amazing but the built-in speakers are quite disappointing and weak. You will definitely need a soundbar."},
        {"source": "Flipkart", "rating": 5, "text": "Best television I have ever owned. Picture quality during night scenes with deep blacks is absolutely unreal and stunning."},
        {"source": "Flipkart", "rating": 4, "text": "Outstanding display quality for both movies and gaming. WebOS interface is smooth and responsive."},
        {"source": "Flipkart", "rating": 2, "text": "Burn-in appeared on my unit after 8 months of normal use. This is a serious concern for the asking price."},
        {"source": "Reddit", "rating": 5, "text": "Gaming on this TV is a transformative experience. The 120Hz panel with 1ms response time and VRR support makes every game look incredible."},
        {"source": "Reddit", "rating": 4, "text": "Gorgeous picture quality that you cannot find in any LED TV. The perfect blacks make night scenes look completely cinematic."},
        {"source": "Reddit", "rating": 3, "text": "Great TV but burn-in risk is real and worth considering if you watch news or sports channels with static logos."},
        {"source": "Review Blog", "rating": 5, "text": "LG C3 OLED is our unanimous pick for the best TV of the year. Unrivaled picture quality, excellent gaming features, and refined smart TV platform."},
    ],
}

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
    "old","new","first","last","next","right","left","far","use","even",
    "phone","camera","performance","light","screen","device","model","version",
    "feature","features","option","options","issue","issues","problem","problems",
    "quality","level","levels","point","points","compared","comparing","simply",
    "definitely","absolutely","completely","incredibly","genuinely","honestly",
}

MEANINGFUL_BIGRAMS = [
    "noise cancellation","noise cancelling","battery life","sound quality",
    "build quality","call quality","charging speed","fast charging",
    "display quality","camera quality","low light","heating issue",
    "bluetooth connectivity","audio quality","active noise","touch controls",
    "water resistant","long lasting","easy setup","customer service",
    "pressure cooking","picture quality","input lag","burn-in risk",
    "refresh rate","slow cooker","meal prep","ear cups","transparency mode",
]

SAMPLE_PRODUCTS = [
    "Sony WH-1000XM5",
    "Samsung Galaxy S24",
    "Instant Pot Duo 7-in-1",
    "Apple AirPods Pro 2",
    "OnePlus Nord CE 3",
    "LG OLED C3 TV",
]

# ── NLP FUNCTIONS ─────────────────────────────────────────────────────────────
analyzer = SentimentIntensityAnalyzer()

def extract_keywords(text):
    words = re.findall(r"\b[a-zA-Z]{5,}\b", text.lower())
    return [w for w in words if w not in STOPWORDS]

def extract_bigrams(text):
    text_lower = text.lower()
    return [b for b in MEANINGFUL_BIGRAMS if b in text_lower]

def top_phrases(words, n=5):
    if not words:
        return []
    return [w.title() for w, _ in Counter(words).most_common(n)]

def load_reviews(product_name):
    key = product_name.lower().strip()
    if key in REVIEWS_DATA:
        return REVIEWS_DATA[key]
    # fuzzy match
    for k in REVIEWS_DATA:
        if any(w in k for w in key.split() if len(w) > 3):
            return REVIEWS_DATA[k]
    return []

def run_sentiment(reviews):
    total = len(reviews)
    pos_count = neu_count = neg_count = 0
    pos_words, neg_words = [], []
    by_source = {}

    for r in reviews:
        text = r["text"]
        source = r.get("source", "Unknown")
        score = analyzer.polarity_scores(text)["compound"]

        if score >= 0.05:
            label = "positive"; pos_count += 1
            pos_words += extract_keywords(text) + extract_bigrams(text)
        elif score <= -0.05:
            label = "negative"; neg_count += 1
            neg_words += extract_keywords(text) + extract_bigrams(text)
        else:
            label = "neutral"; neu_count += 1

        if source not in by_source:
            by_source[source] = {"positive":0,"negative":0,"neutral":0,"count":0}
        by_source[source][label] += 1
        by_source[source]["count"] += 1

    pos_pct = round(pos_count/total*100)
    neu_pct = round(neu_count/total*100)
    neg_pct = round(neg_count/total*100)

    for s, d in by_source.items():
        c = d["count"]
        d["positive"] = round(d["positive"]/c*100)
        d["negative"] = round(d["negative"]/c*100)
        d["neutral"]  = round(d["neutral"]/c*100)

    if pos_pct >= 60:   overall = f"Positive ({pos_pct}%)"
    elif neg_pct >= 50: overall = f"Negative ({neg_pct}%)"
    else:               overall = f"Mixed ({pos_pct}% positive)"

    return {
        "overall_label": overall,
        "overall_score": {"positive": pos_pct, "neutral": neu_pct, "negative": neg_pct},
        "top_pros": top_phrases(pos_words),
        "top_cons": top_phrases(neg_words),
        "total_reviews": total,
        "by_source": by_source,
    }

def generate_report(product_name, sentiment_data):
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    pros = ", ".join(sentiment_data["top_pros"][:3]).lower()
    cons = ", ".join(sentiment_data["top_cons"][:3]).lower()
    overall = sentiment_data["overall_label"]
    total = sentiment_data["total_reviews"]

    if api_key and api_key != "your_actual_key_here":
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a product review analyst helping online buyers make informed decisions.

Based on the following aggregated review data for the product "{product_name}", generate a short, clear, buyer-friendly insight report.

REVIEW DATA:
- Total reviews analyzed: {total}
- Overall sentiment: {overall}
- Top positive keywords (what buyers liked): {pros}
- Top negative keywords (common complaints): {cons}

Generate exactly 3 outputs in this format (no markdown, no extra text):

BUY_IF: [One sentence describing the ideal buyer - who will love this product]
AVOID_IF: [One sentence describing who should NOT buy this product]
VERDICT: [2-3 sentences. An honest, balanced summary a first-time buyer would appreciate.]"""

            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            text = message.content[0].text.strip()
            result = {"buy_if": "", "avoid_if": "", "verdict": ""}
            for line in text.split("\n"):
                line = line.strip()
                if line.startswith("BUY_IF:"):
                    result["buy_if"] = line.replace("BUY_IF:", "").strip()
                elif line.startswith("AVOID_IF:"):
                    result["avoid_if"] = line.replace("AVOID_IF:", "").strip()
                elif line.startswith("VERDICT:"):
                    result["verdict"] = line.replace("VERDICT:", "").strip()
            if result["verdict"]:
                return result
        except Exception as e:
            st.warning(f"AI report unavailable ({str(e)[:60]}). Showing smart fallback.")

    # Fallback
    pros_str = pros if pros else "strong overall performance"
    cons_str = cons if cons else "some limitations"
    return {
        "buy_if": f"You prioritize {pros_str} and want a reliable everyday option.",
        "avoid_if": f"You are sensitive to issues around {cons_str}.",
        "verdict": (
            f"Based on {total} reviews across multiple sources, {product_name} shows "
            f"{overall} sentiment. Buyers consistently highlight {pros_str} as standout strengths. "
            f"However, some users report concerns about {cons_str}. Overall a solid choice for the right buyer."
        ),
    }

def sentiment_badge(label):
    if "Positive" in label:
        return f'<span class="badge badge-pos">● {label}</span>'
    elif "Negative" in label:
        return f'<span class="badge badge-neg">● {label}</span>'
    else:
        return f'<span class="badge badge-mix">● {label}</span>'

def source_badge(pct_pos, pct_neg):
    if pct_pos >= 60:
        return '<span class="badge badge-pos" style="font-size:11px;padding:3px 10px;">Mostly Positive</span>'
    elif pct_neg >= 50:
        return '<span class="badge badge-neg" style="font-size:11px;padding:3px 10px;">Mostly Negative</span>'
    else:
        return '<span class="badge badge-mix" style="font-size:11px;padding:3px 10px;">Mixed</span>'

# ── UI ────────────────────────────────────────────────────────────────────────

# Hero
st.markdown("""
<div class="hero-tag">🔍 FeedbackLens · Vibeathon 2.0</div>
<div class="hero-title">What do <span>real buyers</span><br>actually think?</div>
<div class="hero-sub">// AI-synthesized insights from Amazon · Flipkart · Reddit · Review Blogs</div>
""", unsafe_allow_html=True)

# Search
col_input, col_btn = st.columns([5, 1])
with col_input:
    product_input = st.text_input(
        label="product",
        label_visibility="collapsed",
        placeholder="Enter a product name — e.g. Sony WH-1000XM5",
        key="product_input",
    )
with col_btn:
    analyze_clicked = st.button("ANALYZE →", use_container_width=True, type="primary")

# Quick pills
st.markdown('<div class="pill-row">' +
    "".join([f'<span class="pill-btn">▸ {p}</span>' for p in SAMPLE_PRODUCTS]) +
    '</div>', unsafe_allow_html=True)

# Quick select via selectbox (hidden label)
quick = st.selectbox(
    "Quick select a sample product:",
    ["— or pick a sample product below —"] + SAMPLE_PRODUCTS,
    key="quick_select",
)
if quick != "— or pick a sample product below —":
    product_input = quick

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── ANALYZE ──────────────────────────────────────────────────────────────────
if analyze_clicked or (quick != "— or pick a sample product below —"):
    product = product_input.strip()
    if not product:
        st.warning("Please enter a product name.")
    else:
        with st.spinner(f"Fetching and analyzing reviews for **{product}**..."):
            reviews = load_reviews(product)

        if not reviews:
            st.error(f"No reviews found for **{product}**. Try one of the sample products.")
        else:
            with st.spinner("Running sentiment analysis..."):
                sentiment = run_sentiment(reviews)

            with st.spinner("Generating buyer insights..."):
                report = generate_report(product, sentiment)

            s = sentiment["overall_score"]

            # ── Product Header ──
            st.markdown(f"""
            <div class="card" style="border-top: 3px solid #e8ff47;">
                <div class="product-title">{product}</div>
                <div class="product-meta">📊 {sentiment['total_reviews']} reviews analyzed &nbsp;·&nbsp; 🗂 Multi-source aggregation &nbsp;·&nbsp; {sentiment_badge(sentiment['overall_label'])}</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Sentiment Bar ──
            st.markdown('<div class="card"><div class="section-label">Sentiment Breakdown</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ Positive", f"{s['positive']}%")
            col2.metric("➖ Neutral", f"{s['neutral']}%")
            col3.metric("❌ Negative", f"{s['negative']}%")
            st.progress(s['positive'] / 100)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Pros & Cons ──
            col_pros, col_cons = st.columns(2)
            with col_pros:
                pros_tags = "".join([f'<span class="tag-pro">{p}</span>' for p in sentiment["top_pros"]])
                st.markdown(f"""
                <div class="card card-accent-green">
                    <div class="section-label">✦ What buyers love</div>
                    <div class="tag-row">{pros_tags}</div>
                </div>""", unsafe_allow_html=True)

            with col_cons:
                cons_tags = "".join([f'<span class="tag-con">{c}</span>' for c in sentiment["top_cons"]])
                st.markdown(f"""
                <div class="card card-accent-red">
                    <div class="section-label">✦ Common complaints</div>
                    <div class="tag-row">{cons_tags}</div>
                </div>""", unsafe_allow_html=True)

            # ── Buy / Avoid ──
            col_buy, col_avoid = st.columns(2)
            with col_buy:
                st.markdown(f"""
                <div class="buy-block">
                    <div class="buy-label">✓ Buy if</div>
                    <div class="rec-text">{report['buy_if']}</div>
                </div>""", unsafe_allow_html=True)
            with col_avoid:
                st.markdown(f"""
                <div class="avoid-block">
                    <div class="avoid-label">✗ Avoid if</div>
                    <div class="rec-text">{report['avoid_if']}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Verdict ──
            st.markdown(f"""
            <div class="card card-accent-yellow">
                <div class="section-label">Final Verdict</div>
                <div class="verdict-text">{report['verdict']}</div>
            </div>""", unsafe_allow_html=True)

            # ── Source Breakdown ──
            st.markdown('<div class="card"><div class="section-label">Source Breakdown</div>', unsafe_allow_html=True)
            for source, data in sentiment["by_source"].items():
                badge = source_badge(data["positive"], data["negative"])
                st.markdown(f"""
                <div class="source-row">
                    <span class="source-name">● {source} <span class="source-count">({data['count']} reviews)</span></span>
                    {badge}
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">FEEDBACKLENS · VIBEATHON 2.0 · AI-POWERED REVIEW INTELLIGENCE</div>', unsafe_allow_html=True)
