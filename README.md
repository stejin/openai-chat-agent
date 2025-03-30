# OpenAI Chat Agent

A Python-based chat agent that leverages OpenAI's API to create conversational AI experiences.

## Project Description

This application provides a simple yet powerful interface to OpenAI's chat models. It handles API communication, rate limiting, error handling, and conversation management, allowing you to focus on building great conversational experiences.

## Installation

### Prerequisites
- Python 3.7 or higher
- Git
- OpenAI API key

### Steps

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd Agent
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Setup

### Environment Configuration

1. Create a `.env` file in the project root (or copy the example)
   ```bash
   cp .env.example .env
   ```

2. Add your OpenAI API key to the `.env` file
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Project Structure
```
Agent/
├── .env                # Environment variables (not in version control)
├── .gitignore          # Git ignore file
├── requirements.txt    # Project dependencies
├── README.md           # This file
└── src/                # Source code
    ├── __init__.py
    ├── main.py         # Main entry point
    ├── config.py       # Configuration and API setup
    └── utils.py        # Utility functions
```

## Usage

### Basic Usage

Run the chat agent from the command line:

```bash
python -m src.main
```

### Code Examples

#### Creating a Chat Agent Instance

```python
from src.main import ChatAgent

# Initialize the chat agent
agent = ChatAgent()

# Send a message and get a response
response = agent.send_message("Tell me a joke about programming")
print(response)
```

#### Custom Configuration

```python
from src.main import ChatAgent

# Initialize with custom parameters
agent = ChatAgent(
    model="gpt-4",
    temperature=0.7,
    max_tokens=500
)

# Start a conversation
response = agent.send_message("Explain quantum computing in simple terms")
print(response)

# Continue the conversation
follow_up = agent.send_message("What are its practical applications?")
print(follow_up)
```

## Features

- **Seamless OpenAI API Integration**: Connect to OpenAI's powerful language models with minimal setup
- **Conversation Management**: Maintains conversation context for natural back-and-forth interactions
- **Rate Limiting**: Smart handling of API rate limits with exponential backoff
- **Error Handling**: Robust error handling for API errors, network issues, and invalid inputs
- **Easy Configuration**: Simple setup through environment variables and configuration options
- **Command Line Interface**: Test conversations directly from the command line

## Error Handling

The Chat Agent implements various error handling mechanisms:

- **API Authentication**: Verifies the API key is present and valid
- **Rate Limiting**: Automatically retries with exponential backoff when rate limited
- **Network Errors**: Handles timeouts and connection issues with graceful degradation
- **Input Validation**: Validates inputs before sending to the API
- **Logging**: Comprehensive logging for debugging and monitoring

### Common Error Solutions

- **API Key Issues**: Ensure your API key is correctly set in the `.env` file
- **Rate Limiting**: If you're hitting rate limits frequently, consider implementing caching or increasing backoff parameters
- **Network Problems**: Check your internet connection and firewall settings
- **Model Errors**: Verify that you're using a valid model name and that your prompt adheres to OpenAI's guidelines

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

