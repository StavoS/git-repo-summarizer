import logging
from fastapi import APIRouter, HTTPException
from app.schemas.summarize import SummarizeRequest, SummarizeResponse
from app.services.github_service import fetch_repository
from app.services.repo_processor import build_repository_context
from app.services.llm_service import generate_summary

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_repo(request: SummarizeRequest):
    logger.info("Summarize request received for: %s", request.github_url)
    
    try:
        logger.info("Fetching repository data from GitHub... (advanced=%s)", request.advanced)
        repo_data = await fetch_repository(str(request.github_url))
        
        logger.info("Building repository context...")
        context = await build_repository_context(repo_data, advanced=request.advanced)
        
        logger.info("Generating summary with LLM...")
        result = await generate_summary(context)
        
        logger.info("Summary generated successfully for %s", request.github_url)
        return SummarizeResponse(**result)

    except ValueError as e:
        logger.error("Validation error: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to summarize repository")
