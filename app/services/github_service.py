import logging
import httpx
from typing import Dict


logger = logging.getLogger(__name__)
GITHUB_API = "https://api.github.com"


def parse_github_url(url: str) -> tuple[str, str]:
    parts = url.rstrip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")
    return parts[-2], parts[-1]


async def fetch_repository(url: str) -> Dict:
    owner, repo = parse_github_url(url)
    logger.info("Fetching repository: %s/%s", owner, repo)
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        logger.debug("Fetching repository metadata...")
        repo_resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}",
            headers=headers
        )
        if repo_resp.status_code != 200:
            logger.error("Repository not found: %s/%s (status: %d)", owner, repo, repo_resp.status_code)
            raise ValueError("Repository not found or inaccessible")
        logger.debug("Repository metadata fetched successfully")

        # Get README with raw content
        logger.debug("Fetching README...")
        readme_headers = {**headers, "Accept": "application/vnd.github.raw"}
        readme_resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/readme",
            headers=readme_headers
        )
        readme_status = "found" if readme_resp.status_code == 200 else "not found"
        logger.debug("README %s", readme_status)

        # Get file tree
        logger.debug("Fetching file tree...")
        tree_resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1",
            headers=headers
        )
        tree_data = tree_resp.json()
        file_count = len(tree_data.get("tree", []))
        logger.info("Fetched repository with %d files", file_count)

    return {
        "metadata": repo_resp.json(),
        "readme": readme_resp.text if readme_resp.status_code == 200 else "",
        "tree": tree_data,
        "owner": owner,
        "repo": repo,
    }
