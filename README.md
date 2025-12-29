---
title: GAIA Agent
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 6.2.0
app_file: app.py
pinned: false
python_version: '3.12'
license: apache-2.0
# built-in oauth flow
hf_oauth: true
---


# GAIA Agent 

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Hugging Face Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Space-yellow)](https://huggingface.co/spaces)

A robust, enterprise-grade generic assistant designed to solve complex multi-step reasoning tasks from the **GAIA benchmark**. Built on **LlamaIndex Workflows**, this agent combines structured reasoning, comprehensive tool use, and type-safe configuration to deliver high-accuracy results.

## Key Capabilities

*   **Structured Reasoning**: Uses Pydantic models to enforce strict output formats, eliminating parsing errors.
*   **Resilient Workflow**: Implements retry logic, error handling, and self-correction mechanisms for API failures.
*   **Advanced Tooling**: Equipped with 12 specialized tools for research, mathematics, coding, and file processing.
*   **Observability**: Integrated specialized logging with `loguru` for clear, color-coded execution traces and debugging.

## Tool Suite

The agent has access to a diverse set of tools to handle varied tasks:

| Category | Tools | Description |
| :--- | :--- | :--- |
| **Knowledge** | Wikipedia, arXiv, Weather | Retrieves factual and scientific information. |
| **Web** | DuckDuckGo Search, News | Accesses real-time information and current events. |
| **Analysis** | Code Execution, Data Analysis | Safely runs Python code for math and data processing (pandas, numpy). |
| **Math** | Calculator, Symbolic Solver | Handles complex calculations and algebraic equations. |
| **Files** | Read & Download | Processes PDF, Excel, Word, and other document formats. |

## Quickstart

### Prerequisites

*   Python 3.12+
*   `uv` for dependency management (recommended)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://huggingface.co/spaces/your-username/gaia-agent
    cd gaia-agent
    ```

2.  **Install dependencies**
    ```bash
    uv sync
    ```

3.  **Configure Environment**
    Create a `.env` file with your API keys:
    ```bash
    HF_TOKEN=your_token_here
    OPENAI_API_KEY=your_key_here  # Optional, for enhanced performance
    ```

4.  **Run the Application**
    ```bash
    uv run app.py
    ```

## Project Structure

*   `agent.py`: Core logic for the ReAct agent.
*   `workflow.py`: LlamaIndex event-driven workflow definition.
*   `tools/`: Directory containing all tool implementations.
*   `config/`: Type-safe configuration using Pydantic Settings.
*   `prompts/`: centralized prompt management.

## Evaluation

Test the agent's performance on GAIA benchmark questions:

```bash
# Run a single random test question
uv run test_agent.py

# Run a specific batch
uv run test_agent.py --batch 5
```