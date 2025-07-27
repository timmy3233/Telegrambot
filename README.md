# Telegram Bot

A Python-based Telegram chatbot with basic command handling and automated message responses.

## Features

- **Command Handling**: Responds to `/start`, `/help`, and `/echo` commands
- **Text Message Processing**: Handles regular text messages with intelligent responses
- **Error Handling**: Comprehensive error handling and logging
- **Rate Limiting**: Basic rate limiting to prevent spam
- **Modular Design**: Easy to extend with new commands and features
- **Environment Configuration**: Uses environment variables for secure configuration

## Setup

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy your bot token

### 2. Configure Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
