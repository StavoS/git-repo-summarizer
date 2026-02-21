# LLM Prompts

This directory contains the prompt templates used for GitHub repository summarization.

## Files

- **system_prompt.md**: The system message that defines the LLM's role and output format
- **user_prompt.md**: The user message template that includes the repository context

## Customization

You can modify these prompts to change how the LLM analyzes repositories:

- Edit `system_prompt.md` to change the LLM's role or output requirements
- Edit `user_prompt.md` to change how the repository context is presented

**Note**: The prompts are loaded once at application startup. After modifying them, restart the server for changes to take effect.

## Template Variables

In `user_prompt.md`, the following variable is available:

- `{context}`: The repository context (README, file tree, metadata)
