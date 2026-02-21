import logging
import httpx
from typing import Dict, List


logger = logging.getLogger(__name__)
IGNORED_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__"}
IGNORED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".exe", ".zip", ".lock"}

# File extensions to fetch contents for in advanced mode
KEY_FILE_PATTERNS = (
    "package.json", "pyproject.toml", "requirements.txt", "Cargo.toml",
    "go.mod", "build.gradle", "pom.xml", "Gemfile", "composer.json",
    "Makefile", "Dockerfile", ".gitignore", "setup.py", "tsconfig.json"
)


async def fetch_file_contents(owner: str, repo: str, file_paths: List[str]) -> Dict[str, str]:
    """Fetch raw contents of specific files from GitHub."""
    logger.info("Fetching contents for %d files...", len(file_paths))
    contents = {}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for path in file_paths:
            try:
                # GitHub raw content URL
                url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{path}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    content = response.text
                    # Limit individual file size to 2000 chars to prevent token overflow
                    contents[path] = content[:2000]
                    if len(content) > 2000:
                        logger.debug("File %s truncated from %d to 2000 chars", path, len(content))
                else:
                    logger.debug("Could not fetch %s (status: %d)", path, response.status_code)
            except Exception as e:
                logger.debug("Error fetching %s: %s", path, str(e))
    
    logger.info("Successfully fetched %d file contents", len(contents))
    return contents


async def build_repository_context(repo_data: dict, advanced: bool = False) -> str:
    logger.info("Building context for %s/%s", repo_data['owner'], repo_data['repo'])
    tree = repo_data["tree"].get("tree", [])
    readme = repo_data["readme"]

    selected_files = []

    for item in tree:
        path = item["path"]

        if any(part in IGNORED_DIRS for part in path.split("/")):
            continue

        if any(path.endswith(ext) for ext in IGNORED_EXTENSIONS):
            continue

        if path.lower().startswith("readme"):
            selected_files.append(path)
        elif path.endswith(("package.json", "pyproject.toml", "requirements.txt")):
            selected_files.append(path)
        elif path.count("/") <= 1:
            selected_files.append(path)

        if len(selected_files) >= 15:
            break

    logger.info("Selected %d files for context", len(selected_files))
    logger.debug("Selected files: %s", selected_files)
    
    readme_length = len(readme)
    readme_truncated = readme[:8000]
    if readme_length > 8000:
        logger.debug("README truncated from %d to 8000 chars", readme_length)
    
    # Build base context
    context_parts = [
        f"Repository: {repo_data['owner']}/{repo_data['repo']}",
        "",
        "README:",
        readme_truncated,
        "",
        "Selected files:",
        str(selected_files)
    ]
    
    # In advanced mode, fetch and include file contents
    if advanced:
        logger.info("Advanced mode: fetching file contents...")
        # Only fetch contents for key config/setup files to avoid token overflow
        key_files = [f for f in selected_files if any(f.endswith(pattern) for pattern in KEY_FILE_PATTERNS)]
        
        if key_files:
            file_contents = await fetch_file_contents(repo_data['owner'], repo_data['repo'], key_files)
            
            if file_contents:
                context_parts.append("")
                context_parts.append("File Contents:")
                for file_path, content in file_contents.items():
                    context_parts.append(f"\n--- {file_path} ---")
                    context_parts.append(content)
                    context_parts.append("--- end ---")
    
    context = "\n".join(context_parts)
    
    # Increased limit for advanced mode
    max_length = 40000 if advanced else 20000
    final_context = context[:max_length]
    
    if len(context) > max_length:
        logger.debug("Context truncated from %d to %d chars", len(context), max_length)
    
    logger.info("Context built: %d chars, %d files%s", 
                len(final_context), len(selected_files),
                " (with file contents)" if advanced else "")
    return final_context
