import os
import json
import logging
from pathlib import Path
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


logger = logging.getLogger(__name__)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Default to gpt-4o-mini

# Load prompts from markdown files at startup
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
SYSTEM_PROMPT = (PROMPTS_DIR / "system_prompt.md").read_text().strip()
USER_PROMPT_TEMPLATE = (PROMPTS_DIR / "user_prompt.md").read_text().strip()
logger.info("Prompts loaded from: %s", PROMPTS_DIR)
logger.info("LLM model configured: %s", OPENAI_MODEL)


async def generate_summary(context: str) -> Dict:
    """
    Generate a summary of a GitHub repository using OpenAI's GPT model.
    
    Args:
        context:  information including README, file tree, and metadata
        Repository
    Returns:
        Dictionary with keys: summary, technologies, structure
        
    Raises:
        ValueError: If OpenAI API key is not configured
        Exception: If LLM call fails or response is invalid
    """
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not configured")
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    logger.info("Initializing LLM (%s)...", OPENAI_MODEL)
    # Initialize the LLM with JSON mode for structured output
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=0.3,
        timeout=60,
        api_key=OPENAI_API_KEY,
        model_kwargs={"response_format": {"type": "json_object"}}
    )
    
    # Construct the prompt using pre-loaded templates
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    user_content = USER_PROMPT_TEMPLATE.format(context=context)
    human_message = HumanMessage(content=user_content)
    
    context_length = len(context)
    logger.info("Sending request to OpenAI (context: %d chars)...", context_length)
    
    try:
        # Make the LLM call
        response = await llm.ainvoke([system_message, human_message])
        logger.info("LLM response received")
        
        # Parse the JSON response
        logger.debug("Parsing LLM response...")
        result = json.loads(response.content)
        
        # Validate required fields are present
        required_fields = ["summary", "technologies", "structure"]
        for field in required_fields:
            if field not in result:
                logger.error("Missing field '%s' in LLM response", field)
                raise ValueError(f"Missing required field in LLM response: {field}")
        
        # Ensure technologies is a list
        if not isinstance(result["technologies"], list):
            result["technologies"] = [result["technologies"]]
        
        tech_count = len(result["technologies"])
        logger.info("Summary generated: %d technologies identified", tech_count)
        logger.debug("Technologies: %s", result["technologies"])
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error("Failed to parse LLM response as JSON: %s", str(e))
        raise Exception(f"Failed to parse LLM response as JSON: {str(e)}")
    except Exception as e:
        logger.error("LLM API call failed: %s", str(e))
        raise Exception(f"LLM API call failed: {str(e)}")
