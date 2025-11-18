# Obsidian Daily Notes CLI

A powerful CLI tool for managing your daily Obsidian notes with AI-powered knowledge extraction and LessWrong integration.

## Features

- **AI-Powered Knowledge Extraction**: Automatically extracts important insights, events, and learnings from your daily notes and organizes them into a knowledge repository
- **LessWrong Integration**: Fetches top posts from LessWrong and adds AI-generated summaries to your daily notes
- **Automated Daily Workflow**: Designed to run once per day (via cron) to keep your knowledge base up-to-date

## Prerequisites

- Python 3.8 or higher
- An Obsidian vault with a daily notes folder
- Anthropic API key (for Claude AI)

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
ANTHROPIC_API_KEY=your_api_key_here
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
DAILY_NOTES_FOLDER=Daily Notes
KNOWLEDGE_REPO_FOLDER=Knowledge Base
LOOKBACK_DAYS=1
LESSWRONG_POST_COUNT=5
```

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
2. Uses Claude AI to analyze each note and extract:
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
2. Generates concise summaries of each post using Claude AI
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
| `ANTHROPIC_API_KEY` | Your Anthropic API key | (required) |
| `OBSIDIAN_VAULT_PATH` | Absolute path to your Obsidian vault | (required) |
| `DAILY_NOTES_FOLDER` | Folder containing daily notes | `Daily Notes` |
| `KNOWLEDGE_REPO_FOLDER` | Folder for knowledge repository | `Knowledge Base` |
| `LOOKBACK_DAYS` | Number of days to look back for new notes | `1` |
| `LESSWRONG_POST_COUNT` | Number of LessWrong posts to fetch | `5` |

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
