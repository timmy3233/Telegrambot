# Telegram AI Tattoo Consultant Bot

## Overview

This is a Python-based Telegram chatbot application that serves as an AI-powered tattoo consultant. The bot uses OpenAI's GPT-3.5-turbo model to provide professional tattoo advice in Russian, covering aspects like style, placement, care, and other important tattoo considerations. Built using the `python-telegram-bot` library with modern async/await patterns.

## User Preferences

Preferred communication style: Simple, everyday language.
Bot language: Russian
Specialization: Tattoo consultation and advice

## System Architecture

### Backend Architecture
- **Language**: Python 3
- **Framework**: python-telegram-bot library for Telegram Bot API integration
- **Architecture Pattern**: Modular design with separation of concerns
- **Entry Point**: `main.py` serves as the application bootstrap
- **Package Structure**: Organized into a `bot` package with specialized modules

### Core Components
- **AI Integration**: OpenAI GPT-3.5-turbo model integration for intelligent tattoo consultation
- **Command Handlers**: Process Telegram bot commands (`/start`)
- **Message Handlers**: Handle text messages and generate AI-powered responses
- **Configuration Management**: Environment-based configuration system
- **Error Handling**: Comprehensive error handling and logging
- **Async Architecture**: Modern async/await pattern for better performance

## Key Components

### 1. Application Bootstrap (`main.py`)
- Initializes the Telegram bot application
- Registers command and message handlers
- Configures logging system
- Starts the bot with polling mechanism

### 2. Command Module (`bot/commands.py`)
- Handles `/start` command with welcome messages
- Provides `/help` command with usage instructions
- Implements `/echo` command for message repetition
- Uses Markdown parsing for rich text formatting

### 3. Message Handler (`bot/handlers.py`)
- Processes regular text messages
- Implements rate limiting using in-memory storage
- Provides automated responses based on message content
- Maintains user interaction history

### 4. Configuration System (`bot/config.py`)
- Environment variable management
- Bot behavior configuration
- Rate limiting parameters
- Message templates and responses
- Configuration validation

## Data Flow

1. **Message Reception**: Telegram sends updates to the bot via polling
2. **Handler Routing**: Application routes messages to appropriate handlers
3. **Rate Limiting**: System checks user rate limits before processing
4. **Command Processing**: Commands are parsed and executed
5. **Response Generation**: Bot generates appropriate responses
6. **Message Delivery**: Responses are sent back to users via Telegram API

## External Dependencies

### Core Dependencies
- **python-telegram-bot**: Official Telegram Bot API wrapper
- **Standard Library**: Uses `logging`, `os`, `time`, `collections` for core functionality

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Required bot token from BotFather
- `LOG_LEVEL`: Logging verbosity configuration
- `RATE_LIMIT_MESSAGES`: Maximum messages per time window
- `RATE_LIMIT_WINDOW`: Rate limiting time window in seconds
- `DEFAULT_RESPONSE_ENABLED`: Enable/disable automated responses
- `WELCOME_MESSAGE`: Customizable welcome message
- `HELP_MESSAGE`: Customizable help text

## Deployment Strategy

### Local Development
- Environment variables managed via `.env` file
- Direct Python execution for testing and development
- Polling-based message retrieval for simplicity

### Production Considerations
- Environment variables should be set via system configuration
- Logging configured for production monitoring
- Rate limiting parameters tuned for expected load
- Error handling ensures graceful degradation

### Scalability Notes
- Current rate limiting uses in-memory storage (single instance)
- For multi-instance deployment, external rate limiting solution needed
- Bot state is stateless, making horizontal scaling feasible
- Webhook mode could be implemented for better performance

## Architecture Decisions

### 1. Modular Design
- **Problem**: Need for maintainable and extensible codebase
- **Solution**: Separated concerns into dedicated modules
- **Benefits**: Easy to add new commands, clear code organization
- **Trade-offs**: Slightly more complex initial setup

### 2. Environment-Based Configuration
- **Problem**: Need for flexible configuration without code changes
- **Solution**: Environment variables with sensible defaults
- **Benefits**: Secure token management, deployment flexibility
- **Trade-offs**: Configuration scattered across environment

### 3. In-Memory Rate Limiting
- **Problem**: Need to prevent spam and abuse
- **Solution**: Simple in-memory user tracking with time windows
- **Benefits**: Fast, no external dependencies
- **Trade-offs**: Not persistent, single-instance limitation

### 4. Polling vs Webhooks
- **Problem**: Need reliable message delivery mechanism
- **Solution**: Chose polling for simplicity
- **Benefits**: Easier setup, works behind firewalls
- **Trade-offs**: Higher latency, more resource intensive