# Obsidian Daily Notes CLI

A powerful CLI tool for managing your daily Obsidian notes with AI-powered knowledge extraction and LessWrong integration.

## Features

- **AI-Powered Knowledge Extraction**: Automatically extracts important insights, events, and learnings from your daily notes and organizes them into a knowledge repository
- **LessWrong Integration**: Fetches top posts from LessWrong and adds AI-generated summaries to your daily notes
- **Model Agnostic**: Use any LLM provider (Claude, GPT, local models via Ollama, etc.) - easily swap models without code changes
- **Automated Daily Workflow**: Designed to run once per day (via cron) to keep your knowledge base up-to-date

## Prerequisites

- Python 3.8 or higher
- An Obsidian vault with a daily notes folder
- API key for your chosen AI provider (Anthropic, OpenAI, etc.) OR a local model setup (Ollama)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd notes-fixer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install as a package:
```bash
pip install -e .
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Configure your `.env` file with your settings:
```env
# AI Model (defaults to Claude Sonnet 4)
AI_MODEL=claude-sonnet-4-20250514
AI_API_KEY=your_api_key_here

# Obsidian Configuration
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
DAILY_NOTES_FOLDER=Daily Notes
KNOWLEDGE_REPO_FOLDER=Knowledge Base
LOOKBACK_DAYS=1
LESSWRONG_POST_COUNT=5
```

See the [AI Model Configuration](#ai-model-configuration) section for all supported models.

## Usage

### Run Everything (Recommended for Daily Use)

Process recent notes and add LessWrong posts in one command:

```bash
notes-fixer run
```

Or if you didn't install the package:

```bash
python -m notes_fixer run
```

### Extract Knowledge Only

Only extract knowledge from recent daily notes:

```bash
notes-fixer extract-knowledge
```

### LessWrong Posts Only

Only fetch and add LessWrong posts to today's note:

```bash
notes-fixer lesswrong
```

## Setting Up Daily Automation

To run this tool automatically once per day, set up a cron job:

1. Open your crontab:
```bash
crontab -e
```

2. Add a line to run the tool daily (example: every day at 9 AM):
```bash
0 9 * * * cd /path/to/notes-fixer && /usr/bin/python3 -m notes_fixer run >> /tmp/notes-fixer.log 2>&1
```

Or if you installed the package:
```bash
0 9 * * * cd /path/to/notes-fixer && /usr/bin/notes-fixer run >> /tmp/notes-fixer.log 2>&1
```

Make sure to:
- Replace `/path/to/notes-fixer` with the actual path
- Replace `/usr/bin/python3` with your Python path (find it with `which python3`)
- Ensure your `.env` file is properly configured

## How It Works

### Knowledge Extraction

1. Reads daily notes from the specified lookback period (default: 1 day)
2. Uses your configured AI model to analyze each note and extract:
   - Important ideas
   - Notable events
   - Key learnings
   - Project updates
   - People mentions
   - Useful resources
3. Saves extracted items to categorized folders in your Knowledge Base:
   - `Knowledge Base/Ideas/`
   - `Knowledge Base/Events/`
   - `Knowledge Base/Learnings/`
   - `Knowledge Base/Projects/`
   - `Knowledge Base/People/`
   - `Knowledge Base/Resources/`

### LessWrong Integration

1. Fetches top recent posts from LessWrong using their GraphQL API
2. Generates concise summaries of each post using your configured AI model
3. Adds summaries to a "Daily News" section in today's daily note
4. Includes links, authors, and scores for each post

## Folder Structure

```
notes-fixer/
├── notes_fixer/
│   ├── __init__.py        # Package initialization
│   ├── __main__.py        # Main CLI entry point
│   ├── config.py          # Configuration loader
│   ├── types.py           # Data models and types
│   ├── notes_reader.py    # Daily notes reader and file operations
│   ├── ai_processor.py    # AI-powered knowledge extraction
│   └── lesswrong.py       # LessWrong API integration
├── .env                   # Your configuration (create from .env.example)
├── .env.example           # Configuration template
├── requirements.txt       # Python dependencies
├── setup.py               # Package setup
└── README.md
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_MODEL` | AI model to use (see AI Model Configuration below) | `claude-sonnet-4-20250514` |
| `AI_API_KEY` | API key for cloud providers (not needed for local models) | (required for cloud) |
| `ANTHROPIC_API_KEY` | Legacy: Anthropic API key (use `AI_API_KEY` instead) | - |
| `OBSIDIAN_VAULT_PATH` | Absolute path to your Obsidian vault | (required) |
| `DAILY_NOTES_FOLDER` | Folder containing daily notes | `Daily Notes` |
| `KNOWLEDGE_REPO_FOLDER` | Folder for knowledge repository | `Knowledge Base` |
| `LOOKBACK_DAYS` | Number of days to look back for new notes | `1` |
| `LESSWRONG_POST_COUNT` | Number of LessWrong posts to fetch | `5` |

## AI Model Configuration

This tool uses [LiteLLM](https://github.com/BerriAI/litellm) to provide a unified interface for multiple AI providers. You can easily swap between different models by changing the `AI_MODEL` environment variable.

### Supported Providers

**Anthropic (Claude)**
```env
AI_MODEL=claude-sonnet-4-20250514
AI_API_KEY=your_anthropic_api_key
```

Other Claude models:
- `claude-3-5-sonnet-20241022`
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

**OpenAI (GPT)**
```env
AI_MODEL=gpt-4o
AI_API_KEY=your_openai_api_key
```

Other GPT models:
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`

**Local Models (Ollama)**

No API key required! Just install [Ollama](https://ollama.ai/) and run a model:

```bash
ollama pull llama3
# or: ollama pull mistral, ollama pull codellama, etc.
```

Then configure:
```env
AI_MODEL=ollama/llama3
# No AI_API_KEY needed for local models!
```

**Other Providers**

LiteLLM supports 100+ LLM providers including:
- Google (Gemini): `gemini/gemini-pro`
- Cohere: `cohere/command-r-plus`
- AWS Bedrock: `bedrock/anthropic.claude-v2`
- Azure OpenAI: `azure/<deployment-name>`
- And many more...

See the [LiteLLM docs](https://docs.litellm.ai/docs/providers) for the complete list.

### Why Model Agnostic?

- **Cost optimization**: Easily switch to cheaper models for less critical tasks
- **Privacy**: Use local models (Ollama) to keep your notes completely private
- **Experimentation**: Try different models to see which works best for your use case
- **Future-proof**: New models supported automatically through LiteLLM updates

## Development

Run the tool directly without installation:

```bash
python -m notes_fixer run
```

Install in editable mode for development:

```bash
pip install -e .
```

Run tests (if you add them):

```bash
python -m pytest
```

## Troubleshooting

**Error: ANTHROPIC_API_KEY environment variable is required**
- Make sure you've created a `.env` file and added your API key

**Error: OBSIDIAN_VAULT_PATH environment variable is required**
- Set the correct path to your Obsidian vault in `.env`

**No notes found**
- Check that your daily notes folder path is correct
- Ensure your daily notes are `.md` files
- Verify the `LOOKBACK_DAYS` setting

**LessWrong posts not loading**
- Check your internet connection
- The LessWrong API may be temporarily unavailable

## License

MIT

## Contributing

Pull requests are welcome! Please feel free to submit issues for bugs or feature requests.
