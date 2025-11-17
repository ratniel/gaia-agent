"""Tool-specific configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ToolConfig(BaseSettings):
    """Configuration for individual tools."""
    
    # Web Search
    web_search_max_results: int = Field(
        5,
        alias="TOOL_WEB_SEARCH_MAX_RESULTS",
        ge=1,
        le=20,
        description="Maximum web search results"
    )
    
    web_search_timeout: int = Field(
        30,
        alias="TOOL_WEB_SEARCH_TIMEOUT",
        ge=5,
        description="Web search timeout in seconds"
    )
    
    # Knowledge Tools
    arxiv_max_results: int = Field(
        3,
        alias="TOOL_ARXIV_MAX_RESULTS",
        ge=1,
        le=10,
        description="Maximum arXiv search results"
    )
    
    wikipedia_max_pages: int = Field(
        3,
        alias="TOOL_WIKIPEDIA_MAX_PAGES",
        ge=1,
        le=10,
        description="Maximum Wikipedia pages to load"
    )
    
    wikipedia_max_chars: int = Field(
        2000,
        alias="TOOL_WIKIPEDIA_MAX_CHARS",
        ge=500,
        description="Maximum characters per Wikipedia page"
    )
    
    # File Operations
    file_read_max_chars: int = Field(
        10000,
        alias="TOOL_FILE_READ_MAX_CHARS",
        ge=1000,
        description="Maximum characters to read from files"
    )
    
    file_download_timeout: int = Field(
        60,
        alias="TOOL_FILE_DOWNLOAD_TIMEOUT",
        ge=10,
        description="File download timeout in seconds"
    )
    
    # Code Execution
    code_execution_timeout: int = Field(
        30,
        alias="TOOL_CODE_EXECUTION_TIMEOUT",
        ge=5,
        le=120,
        description="Code execution timeout in seconds"
    )
    
    code_execution_memory_limit: int = Field(
        512,
        alias="TOOL_CODE_EXECUTION_MEMORY_LIMIT",
        ge=128,
        description="Code execution memory limit in MB"
    )
    
    # Image Processing
    image_max_size: tuple[int, int] = Field(
        (2048, 2048),
        alias="TOOL_IMAGE_MAX_SIZE",
        description="Maximum image dimensions (width, height)"
    )
    
    model_config = {
        "env_prefix": "TOOL_",
        "case_sensitive": False,
        "extra": "ignore",
    }

