# AI CLI Assistant

A Python command-line tool that sends prompts to an AI model, displays responses, and saves conversations to dated JSON log files.

## Features

- Ask questions in the terminal
- Get responses from an AI model
- Save each conversation to a daily JSON log file
- Load previous logs safely
- Show the last 3 conversations at startup
- Search past prompts by keyword
- Handle missing or malformed log files safely
- Use environment variables for secure API key storage

## Tech Used

- Python
- OpenAI API
- python-dotenv
- JSON file handling

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-cli-assistant.git
cd ai-cli-assistant