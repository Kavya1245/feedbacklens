# 🛍️ Product Customer Feedback Synthesizer

> AI-powered tool to aggregate customer reviews from multiple sources and generate buyer-friendly insights.

Built for **Vibeathon 2.0** — Task #3

---

## 🚀 Quick Start

### Backend Setup

```bash
cd backend

# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 4. Run the server
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000
API Docs at: http://localhost:8000/docs
Health check: http://localhost:8000/health

---

### Frontend Setup (coming in Step 5)

```bash
cd frontend
npm install
npm run dev
```

---

## 📁 Project Structure

```
feedback-synthesizer/
├── backend/
│   ├── main.py                  ← FastAPI entry point
│   ├── routes/
│   │   └── analyze.py           ← POST /api/analyze
│   ├── services/
│   │   ├── data_loader.py       ← loads reviews (offline + future live)
│   │   ├── sentiment.py         ← VADER sentiment analysis
│   │   └── ai_report.py        ← Claude AI report generation
│   ├── data/
│   │   └── sample_reviews.json  ← offline sample dataset
│   ├── .env.example
│   └── requirements.txt
├── frontend/                    ← (Step 5)
├── .gitignore
└── README.md
```

---

## 🔌 API Reference

### `GET /health`
Returns server status.

### `POST /api/analyze`
**Request:**
```json
{
  "product_name": "Sony WH-1000XM5",
  "product_url": "https://amazon.in/...",   // optional
  "filter_type": "all"                       // all | recent | budget | quality
}
```

**Response:**
```json
{
  "product": "Sony WH-1000XM5",
  "overall_sentiment": "Positive (72%)",
  "sentiment_score": { "positive": 72, "neutral": 15, "negative": 13 },
  "top_pros": ["Sound", "Comfortable", "Battery"],
  "top_cons": ["Fragile", "Expensive", "Connectivity"],
  "buy_if": "You prioritize sound quality and ANC for daily commute.",
  "avoid_if": "You need durable headphones for workouts or rough use.",
  "verdict": "A premium choice for audiophiles...",
  "source_summary": [
    { "source": "Amazon", "sentiment": "Mostly Positive", "review_count": 5 }
  ],
  "total_reviews": 14
}
```

---

## 🧱 Build Steps

- [x] Step 1 — FastAPI backend setup + health endpoint
- [ ] Step 2 — Sentiment analysis + keyword extraction
- [ ] Step 3 — AI report generation (Claude API)
- [ ] Step 4 — Reddit live data source
- [ ] Step 5 — React frontend
- [ ] Step 6 — Connect frontend ↔ backend
- [ ] Step 7 — Deployment (Render + Vercel)

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key from console.anthropic.com |
| `REDDIT_CLIENT_ID` | Reddit app client ID |
| `REDDIT_CLIENT_SECRET` | Reddit app secret |
| `FRONTEND_URL` | Frontend origin for CORS |
