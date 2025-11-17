"""Tool-specific prompts and instructions."""

WEB_SEARCH_PROMPT = """Use web search to find current, up-to-date information.

Best for:
- Current events and news
- Recent developments
- Real-time data
- Information not in training data

Query formulation tips:
- Be specific and concise
- Include key terms
- Use quotes for exact phrases
- Add year for recent info"""

WIKIPEDIA_PROMPT = """Use Wikipedia search for established factual information.

Best for:
- Historical facts
- Biographies
- Definitions
- General knowledge
- Well-documented topics

Search tips:
- Use the main topic name
- Try variations if not found
- Check disambiguation pages
- Verify information is current"""

ARXIV_PROMPT = """Use arXiv search for academic research and scientific papers.

Best for:
- Research findings
- Scientific discoveries
- Technical information
- Academic papers

Search tips:
- Use technical terms
- Include author names if known
- Specify research area
- Check publication dates"""

WEATHER_PROMPT = """Use weather tool for current weather conditions.

Provides:
- Current temperature
- Weather conditions
- Humidity, wind speed
- Forecasts

Location format:
- City name: "New York"
- City, Country: "London, UK"
- Coordinates: "40.7128,-74.0060" """

FILE_OPERATIONS_PROMPT = """Use file operations for questions with associated files.

Process:
1. Use download_file with task_id to get the file
2. Use read_file with the file path to read content
3. Analyze the content
4. Extract the answer

Supported formats:
- Text files (.txt, .md, .csv, .json)
- PDFs (.pdf)
- Excel (.xlsx, .xls)
- Images (.jpg, .png) - basic info only"""

CODE_EXECUTION_PROMPT = """Use code execution for complex calculations or data processing.

Best for:
- Mathematical calculations
- Data analysis
- Algorithm implementation
- Complex logic

Code guidelines:
- Use numpy for numerical operations
- Use sympy for symbolic math
- Use pandas for data manipulation
- Store result in 'result' variable
- Keep code simple and focused"""

CALCULATOR_PROMPT = """Use calculator for mathematical expressions.

Best for:
- Arithmetic operations
- Algebraic expressions
- Mathematical formulas
- Symbolic math

Supports:
- Basic operations: +, -, *, /, **
- Functions: sin, cos, tan, log, exp
- Constants: pi, e
- Variables and symbols"""

IMAGE_ANALYSIS_PROMPT = """Use image analysis for image-related questions.

Provides:
- Image dimensions
- File format
- Color information
- Basic statistics

Note: This tool only provides basic information.
For detailed image understanding, consider using
a multimodal LLM with vision capabilities."""

