# Dolphin MCP

A flexible Python library and CLI tool for interacting with Model Context Protocol (MCP) servers using any LLM model.

![image](https://github.com/user-attachments/assets/d0ee1159-2a8f-454d-8fba-cf692f425af9)

## Overview

Dolphin MCP is both a Python library and a command-line tool that allows you to query and interact with MCP servers through natural language. It connects to any number of configured MCP servers, makes their tools available to language models (OpenAI, Anthropic, Ollama, LMStudio), and provides a conversational interface for accessing and manipulating data from these servers.

The project demonstrates how to:
- Connect to multiple MCP servers simultaneously
- List and call tools provided by these servers
- Use function calling capabilities to interact with external data sources
- Process and present results in a user-friendly way
- Create a reusable Python library with a clean API
- Build a command-line interface on top of the library

## Features

- **Multiple Provider Support**: Works with OpenAI, Anthropic, Ollama, and LMStudio models
- **Reasoning Token Access**: Extract reasoning tokens from reasoning models (e.g., o1-mini) in both streaming and non-streaming modes
- **Multi-Step Reasoning**: Advanced reasoning system with planning, code execution, and systematic problem solving
- **Modular Architecture**: Clean separation of concerns with provider-specific modules
- **Dual Interface**: Use as a Python library or command-line tool
- **MCP Server Integration**: Connect to any number of MCP servers simultaneously
- **Tool Discovery**: Automatically discover and use tools provided by MCP servers
- **Flexible Configuration**: Configure models and servers through JSON configuration
- **Environment Variable Support**: Securely store API keys in environment variables
- **Comprehensive Documentation**: Detailed usage examples and API documentation
- **Installable Package**: Easy installation via pip with `dolphin-mcp-cli` command

## Prerequisites

Before installing Dolphin MCP, ensure you have the following prerequisites installed:

1. **Python 3.10+**
2. **SQLite** - A lightweight database used by the demo
3. **uv/uvx** - A fast Python package installer and resolver

### Setting up Prerequisites

#### Windows

1. **Python 3.10+**:
   - Download and install from [python.org](https://www.python.org/downloads/windows/)
   - Ensure you check "Add Python to PATH" during installation

2. **SQLite**:
   - Download the precompiled binaries from [SQLite website](https://www.sqlite.org/download.html)
   - Choose the "Precompiled Binaries for Windows" section and download the sqlite-tools zip file
   - Extract the files to a folder (e.g., `C:\sqlite`)
   - Add this folder to your PATH:
     - Open Control Panel > System > Advanced System Settings > Environment Variables
     - Edit the PATH variable and add the path to your SQLite folder
     - Verify installation by opening Command Prompt and typing `sqlite3 --version`

3. **uv/uvx**:
   - Open PowerShell as Administrator and run:
     ```
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
   - Restart your terminal and verify installation with `uv --version`

#### macOS

1. **Python 3.10+**:
   - Install using Homebrew:
     ```
     brew install python
     ```

2. **SQLite**:
   - SQLite comes pre-installed on macOS, but you can update it using Homebrew:
     ```
     brew install sqlite
     ```
   - Verify installation with `sqlite3 --version`

3. **uv/uvx**:
   - Install using Homebrew:
     ```
     brew install uv
     ```
   - Or use the official installer:
     ```
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   - Verify installation with `uv --version`

#### Linux (Ubuntu/Debian)

1. **Python 3.10+**:
   ```
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **SQLite**:
   ```
   sudo apt update
   sudo apt install sqlite3
   ```
   - Verify installation with `sqlite3 --version`

3. **uv/uvx**:
   ```
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   - Verify installation with `uv --version`

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install dolphin-mcp
```

This will install both the library and the `dolphin-mcp-cli` command-line tool.

### Option 2: Install from Source

1. Clone this repository:
   ```bash
   git clone https://github.com/cognitivecomputations/dolphin-mcp.git
   cd dolphin-mcp
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

3. Set up your environment variables by copying the example file and adding your OpenAI API key:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your OpenAI API key.

4. (Optional) Set up the demo dolphin database:
   ```bash
   python setup_db.py
   ```
   This creates a sample SQLite database with dolphin information that you can use to test the system.

## Configuration

The project uses two main configuration files:

1. `.env` - Contains OpenAI API configuration:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o
   # OPENAI_BASE_URL=https://api.openai.com/v1  # Uncomment and modify if using a custom base url
   ```

2. `mcp_config.json` - Defines MCP servers to connect to:

   **Local Process Servers (stdio transport):**
   ```json
   {
     "mcpServers": {
       "filesystem": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-filesystem", "./"],
         "transport": "stdio"
       },
       "sqlite": {
         "command": "uvx",
         "args": ["mcp-server-sqlite", "--db-path", "~/.dolphin/dolphin.db"],
         "env": {
           "ENV_VAR": "value"
         }
       }
     }
   }
   ```

   **SSE (Server-Sent Events) Servers:**
   ```json
   {
     "mcpServers": {
       "atlassian": {
         "url": "https://mcp.atlassian.com/v1/sse",
         "transport": "sse",
         "headers": {
           "Authorization": "Bearer your_token_here",
           "User-Agent": "dolphin-mcp/0.1.3"
         },
         "disabled": false
       },
       "example-sse": {
         "url": "https://api.example.com/mcp/sse",
         "transport": "sse"
       }
     }
   }
   ```

   **Configuration Options:**
   - `command` + `args`: For local process servers (stdio transport)
   - `url` + `transport: "sse"`: For SSE-based servers
   - `headers`: Optional HTTP headers for SSE servers
   - `env`: Environment variables for local process servers
   - `disabled`: Set to `true` to skip a server
   - `transport`: Explicitly specify "stdio" or "sse" (auto-detected if omitted)

   You can add as many MCP servers as you need, and the client will connect to all of them and make their tools available.

## Usage

### Using the CLI Command

Run the CLI command with your query as an argument:

```bash
dolphin-mcp-cli "Your query here"
```

### Command-line Options

```
Usage: dolphin-mcp-cli [--model <name>] [--quiet] [--interactive | -i] [--config <file>] [--mcp-config <file>] [--log-messages <file>] [--debug] ['your question']

Options:
  --model <name>         Specify the model to use (e.g., gpt-4o, dolphin, qwen2.5-7b)
  --quiet                Suppress intermediate output (except errors)
  --interactive, -i      Enable interactive chat mode. If selected, 'your question' argument is optional for the first turn.
  --config <file>        Specify a custom config file for LLM providers (default: config.yml)
  --mcp-config <file>    Specify a custom config file for MCP servers (default: examples/sqlite-mcp.json)
  --log-messages <file>  Log all LLM interactions to a JSONL file
  --debug                Enable debug logging (Note: `cli.py` sets DEBUG level by default currently)
  --help, -h             Show this help message
```

### Interactive Chat Mode

To start `dolphin-mcp-cli` in interactive mode, use the `--interactive` or `-i` flag:

```bash
dolphin-mcp-cli --interactive
# or
dolphin-mcp-cli -i
```

You can also provide an initial question:

```bash
dolphin-mcp-cli -i "What dolphin species are endangered?"
```

In interactive mode, you can have a continuous conversation with the configured model. The chat will maintain context from previous turns. Type `exit` or `quit` to end the session.

### Using the Library Programmatically

You can also use Dolphin MCP as a library in your Python code:

```python
import asyncio
from dolphin_mcp import run_interaction

async def main():
    result = await run_interaction(
        user_query="What dolphin species are endangered?",
        model_name="gpt-4o",  # Optional, will use default from config if not specified
        config_path="mcp_config.json",  # Optional, defaults to mcp_config.json
        quiet_mode=False  # Optional, defaults to False
    )
    print(result)

# Run the async function
asyncio.run(main())
```

### Using the Original Script (Legacy)

You can still run the original script directly:

```bash
python dolphin_mcp.py "Your query here"
```

The tool will:
1. Connect to all configured MCP servers
2. List available tools from each server
3. Call the language model API with your query and the available tools
4. Execute any tool calls requested by the model
5. Return the results in a conversational format

## Example Queries

Examples will depend on the MCP servers you have configured. With the demo dolphin database:

```bash
dolphin-mcp-cli --mcp-config examples/sqlite-mcp.json --model gpt-4o "What dolphin species are endangered?"
```

Or with your own custom MCP servers:

```bash
dolphin-mcp-cli "Query relevant to your configured servers"
```

You can also specify a model to use:

```bash
dolphin-mcp-cli --model gpt-4o "What are the evolutionary relationships between dolphin species?"
```

To use the LMStudio provider:

```bash
dolphin-mcp-cli --model qwen2.5-7b "What are the evolutionary relationships between dolphin species?"
```

For quieter output (suppressing intermediate results):

```bash
dolphin-mcp-cli --quiet "List all dolphin species in the Atlantic Ocean"
```

For more detailed examples and use cases, please refer to the [examples README](./examples/README.md).

## Multi-Step Reasoning

Dolphin MCP includes an advanced multi-step reasoning system that can plan, execute code, and systematically solve complex problems. For detailed information about using the reasoning capabilities, see [REASONING.md](./REASONING.md).

Quick example:
```python
from dolphin_mcp.client import run_interaction
from dolphin_mcp.reasoning import ReasoningConfig

result = await run_interaction(
    user_query="Analyze the fibonacci sequence and find patterns",
    reasoning_config=ReasoningConfig(enable_planning=True),
    use_reasoning=True,
    guidelines="Show your work step by step"
)
```

## Reasoning Token Access

Dolphin MCP supports extracting reasoning tokens from reasoning models like OpenAI's o1-mini. When using reasoning models, you can access both the final response and the reasoning process:

```python
from dolphin_mcp.client import run_interaction

# Configure for reasoning model
model_cfg = {
    "provider": "openai",
    "model": "o1-mini",
    "is_reasoning": True,
    "reasoning_effort": "medium"
}

# Non-streaming: Access reasoning tokens
result = await generate_with_openai(conversation, model_cfg, functions, stream=False)
reasoning_process = result.get('reasoning', '')  # The model's reasoning process
final_answer = result['assistant_text']          # The final response

# Streaming: Get reasoning tokens as they're generated
async for chunk in generate_with_openai(conversation, model_cfg, functions, stream=True):
    if chunk.get('reasoning'):
        print(f"Reasoning: {chunk['reasoning']}")
    if chunk.get('assistant_text'):
        print(f"Content: {chunk['assistant_text']}")
```

See `demo_reasoning_tokens.py` for complete examples.

## Demo Database

If you run `setup_db.py`, it will create a sample SQLite database with information about dolphin species. This is provided as a demonstration of how the system works with a simple MCP server. The database includes:

- Information about various dolphin species
- Evolutionary relationships between species
- Conservation status and physical characteristics

This is just one example of what you can do with the Dolphin MCP client. You can connect it to any MCP server that provides tools for accessing different types of data or services.

## Requirements

- Python 3.10+
- OpenAI API key (or other supported provider API keys)

### Core Dependencies
- openai
- mcp[cli]
- python-dotenv
- anthropic
- ollama
- lmstudio
- jsonschema

### Development Dependencies
- pytest
- pytest-asyncio
- pytest-mock
- uv

### Demo Dependencies
- mcp-server-sqlite

All dependencies are automatically installed when you install the package using pip.

## How It Works

### Package Structure

The package is organized into several modules:

- `dolphin_mcp/` - Main package directory
  - `__init__.py` - Package initialization and exports
  - `client.py` - Core MCPClient implementation and run_interaction function
  - `cli.py` - Command-line interface
  - `utils.py` - Utility functions for configuration and argument parsing
  - `providers/` - Provider-specific implementations
    - `openai.py` - OpenAI API integration
    - `anthropic.py` - Anthropic API integration
    - `ollama.py` - Ollama API integration
    - `lmstudio.py` - LMStudio SDK integration

### Execution Flow

1. The CLI parses command-line arguments and calls the library's `run_interaction` function.
2. The library loads configuration from `mcp_config.json` and connects to each configured MCP server.
3. It retrieves the list of available tools from each server and formats them for the language model's API.
4. The user's query is sent to the selected language model (OpenAI, Anthropic, Ollama, or LMStudio) along with the available tools.
5. If the model decides to call a tool, the library routes the call to the appropriate server and returns the result.
6. This process continues until the model has all the information it needs to provide a final response.

This modular architecture allows for great flexibility - you can add any MCP server that provides tools for accessing different data sources or services, and the client will automatically make those tools available to the language model. The provider-specific modules also make it easy to add support for additional language model providers in the future.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license information here]
