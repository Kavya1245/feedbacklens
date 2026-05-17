from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Import route modules
from routes.analyze import router as analyze_router

# -------------------------------------------------
# App Initialization
# -------------------------------------------------
app = FastAPI(
    title="Product Customer Feedback Synthesizer",
    description="AI-powered tool to aggregate and synthesize customer reviews into buyer-friendly insights.",
    version="1.0.0",
)

# -------------------------------------------------
# CORS — allow frontend (React/HTML) to call backend
# -------------------------------------------------
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Register Routers
# -------------------------------------------------
app.include_router(analyze_router, prefix="/api", tags=["Analysis"])


# -------------------------------------------------
# Health Check Endpoint
# -------------------------------------------------
@app.get("/health", tags=["Health"])
def health_check():
    """
    Simple health check endpoint.
    Use this to verify the backend is running correctly.
    """
    return {
        "status": "ok",
        "message": "Product Feedback Synthesizer API is running!",
        "version": "1.0.0",
    }


# -------------------------------------------------
# Root
# -------------------------------------------------
@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the Product Customer Feedback Synthesizer API",
        "docs": "/docs",
        "health": "/health",
    }
