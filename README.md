# GitHub Repository Summarizer

A FastAPI service that analyzes GitHub repositories and generates summaries using OpenAI's GPT models. Given a repository URL, it fetches contents and produces a summary including technology stack and project structure.

## Quick Start

**Prerequisites:** Python 3.10+, OpenAI API key

```bash
# Clone and setup
git clone <your-repo-url> && cd git-repo-summarizer
uv venv && source .venv/bin/activate && uv sync

# Configure
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your_key_here

# Run
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`

## API

**POST /summarize** - Summarize a repository

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/psf/requests",
    "advanced": false
  }'
```

**Parameters:**

- `github_url` (required): GitHub repository URL
- `advanced` (optional, default false): Fetch actual file contents for deeper analysis

**Response:**

```json
{
    "summary": "Description of the project...",
    "technologies": ["Python", "urllib3"],
    "structure": "Project layout description..."
}
```

**API Docs:** [Swagger UI](http://localhost:8000/docs) | [ReDoc](http://localhost:8000/redoc)

## How It Works

- **Smart file filtering:** Ignores build artifacts (`node_modules/`, `dist/`, etc.) and binary files
- **Prioritizes key files:** README, package/config files, main entry points (max 15 files)
- **Dual modes:**
    - _Basic (default):_ Uses file names only (~5K tokens)
    - _Advanced:_ Includes file contents for config files (~10K tokens, more accurate)
- **Uses GPT-4o-mini by default** (configurable in `.env`)

## Configuration

| Variable         | Required | Default     | Description         |
| ---------------- | -------- | ----------- | ------------------- |
| `OPENAI_API_KEY` | Yes      | —           | Your OpenAI API key |
| `OPENAI_MODEL`   | No       | gpt-4o-mini | OpenAI model to use |

## Development

```bash
uv run pytest          # Run tests
uv run black app/      # Format code
uv run mypy app/       # Type checking
```

## License

MIT
