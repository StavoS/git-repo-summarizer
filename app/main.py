import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file FIRST, before other imports
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routes import summarize

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="GitHub Repo Summarizer",
    description="Analyze and summarize GitHub repositories using LLM",
    version="1.0.0"
)

logger.info("GitHub Repo Summarizer started")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if the service is running and properly configured."""
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    logger.info("Health check requested - OpenAI configured: %s", openai_configured)
    
    return JSONResponse(content={
        "status": "healthy",
        "openai_configured": openai_configured,
        "message": "Service is running" if openai_configured else "OPENAI_API_KEY not configured"
    })

app.include_router(summarize.router)
