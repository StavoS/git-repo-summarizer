# GitHub Repository Summarizer

A FastAPI service that analyzes GitHub repositories and generates human-readable summaries using Large Language Models (LLMs). Given a GitHub repository URL, the service fetches the repository contents, processes the most relevant files, and uses OpenAI's GPT models to generate a comprehensive summary including technology stack and project structure.

## Features

- 🔍 Analyzes public GitHub repositories
- 🤖 Uses OpenAI GPT-4o-mini for intelligent summarization
- 📊 Extracts technology stack and project structure
- ⚡ Fast API built with FastAPI
- 🎯 Smart context building to stay within LLM token limits

## Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation & Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd git-repo-summarizer
```

### 2. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Create virtual environment and install dependencies

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Optional:** You can also customize the LLM model:

```env
OPENAI_MODEL=gpt-4o  # Default is gpt-4o-mini if not specified
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{
    "status": "healthy",
    "openai_configured": true,
    "message": "Service is running"
}
```

### Summarize a Repository

**Endpoint:** `POST /summarize`

**Basic Request:**

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/psf/requests"
  }'
```

**Advanced Request (with file contents):**

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/psf/requests",
    "advanced": true
  }'
```

**Request Parameters:**

| Parameter    | Type    | Required | Description                                                                             |
| ------------ | ------- | -------- | --------------------------------------------------------------------------------------- |
| `github_url` | string  | Yes      | URL of the GitHub repository to analyze                                                 |
| `advanced`   | boolean | No       | Enable advanced mode to fetch actual file contents (default: `false`, uses more tokens) |

**Response:**

```json
{
    "summary": "Requests is a simple, yet elegant HTTP library for Python. It allows you to send HTTP/1.1 requests with ease, handling many complexities like connection pooling, cookies, and authentication automatically.",
    "technologies": ["Python", "urllib3", "certifi", "charset-normalizer"],
    "structure": "The project follows a standard Python package layout with the main source code in src/requests/, comprehensive tests in tests/, and documentation in docs/. Configuration files are at the root level."
}
```

**Advanced Mode:**

When `advanced: true` is set, the service:

- Fetches actual contents of key configuration files (package.json, pyproject.toml, etc.)
- Includes up to 2,000 characters from each key file
- Provides more accurate technology detection and deeper insights
- Uses more tokens (context limit increased from 20K to 40K characters)

**Error Response:**

```json
{
    "status": "error",
    "message": "Repository not found or inaccessible"
}
```

## API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Model Choice

This project uses **GPT-4o-mini** from OpenAI for the following reasons:

- **Cost-effective:** ~$0.15 per 1M input tokens vs $5 for GPT-4o
- **Sufficient quality:** Excellent for code understanding and summarization tasks
- **Faster response times:** Lower latency compared to larger models
- **Good token limits:** 128K context window is more than enough for our use case

The model can be changed in [`app/services/llm_service.py`](app/services/llm_service.py) if needed.

## Repository Processing Approach

The service implements a smart strategy to handle repositories of any size while staying within LLM token limits:

### File Filtering Strategy

**Ignored directories:**

- `node_modules/`, `.git/`, `dist/`, `build/`, `__pycache__/`
- Removes build artifacts and dependencies that don't contribute to understanding the project

**Ignored file extensions:**

- Binary files: `.png`, `.jpg`, `.jpeg`, `.gif`, `.exe`, `.zip`
- Lock files: `.lock`
- These files don't provide useful context for understanding the codebase

### File Prioritization

The service prioritizes files in this order:

1. **README files** (highest priority)
    - Truncated to 8,000 characters to prevent overwhelming the context
    - Usually contains the best high-level project description

2. **Package/dependency files**
    - `package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, etc.
    - Reveals the technology stack and dependencies

3. **Top-level files**
    - Files at the root or first level of directories
    - Configuration files, main entry points

4. **Limit to 15 files**
    - Prevents context overflow
    - Focuses on the most relevant files

### Context Management

**Basic Mode (default):**

- Sends only file **names** (not contents) to the LLM
- **Final context limit:** 20,000 characters (~5,000 tokens)
- **Safe for all models:** Well below the 128K token limit of GPT-4o-mini
- **Cost-effective:** Minimal token usage
- Relies primarily on README content for analysis

**Advanced Mode (`advanced: true`):**

- Fetches and includes **actual file contents** for key configuration files
- Fetches files matching: `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, `Dockerfile`, etc.
- Each file limited to 2,000 characters to prevent overflow
- **Final context limit:** 40,000 characters (~10,000 tokens)
- **More accurate:** Better technology detection and deeper insights
- **Higher cost:** Uses approximately 2x more tokens

This dual-mode approach balances speed and cost (basic) with accuracy (advanced), letting you choose based on your needs.

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── routes/
│   │   └── summarize.py             # /summarize endpoint
│   ├── schemas/
│   │   └── summarize.py             # Pydantic models for request/response
│   └── services/
│       ├── github_service.py        # GitHub API integration
│       ├── llm_service.py          # OpenAI/LangChain integration
│       └── repo_processor.py        # Repository context builder
├── .env.example                     # Environment variables template
├── .gitignore
├── pyproject.toml                   # Project dependencies
└── README.md
```

## Environment Variables

| Variable         | Required | Description                                                           |
| ---------------- | -------- | --------------------------------------------------------------------- |
| `OPENAI_API_KEY` | Yes      | Your OpenAI API key for LLM access                                    |
| `OPENAI_MODEL`   | No       | OpenAI model to use (default: `gpt-4o-mini`, options: `gpt-4o`, etc.) |

## Error Handling

The service handles various error scenarios:

- **Invalid GitHub URL:** Returns 400 Bad Request
- **Repository not found:** Returns 400 with descriptive message
- **Private repository:** Returns 400 (requires authentication)
- **OpenAI API errors:** Returns 500 with error details
- **Rate limiting:** GitHub returns appropriate error codes

## Rate Limits

### GitHub API

- 60 requests/hour (unauthenticated)

### OpenAI API

- Depends on your OpenAI account tier
- GPT-4o-mini is typically very generous

## Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Format code
uv run black app/

# Type checking
uv run mypy app/
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
