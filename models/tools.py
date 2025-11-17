"""Models for tool inputs and outputs."""

from pydantic import BaseModel, Field
from typing import Any


class ToolInput(BaseModel):
    """Generic tool input model."""
    
    query: str = Field(..., description="The input query or parameter")
    
    options: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional options for the tool"
    )


class ToolOutput(BaseModel):
    """Generic tool output model."""
    
    result: str = Field(..., description="The tool's result")
    
    success: bool = Field(..., description="Whether the tool executed successfully")
    
    error: str | None = Field(
        None,
        description="Error message if tool failed"
    )
    
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata from tool execution"
    )


class WebSearchResult(BaseModel):
    """Structured output for web search results."""
    
    title: str = Field(..., description="Page title")
    
    snippet: str = Field(..., description="Page snippet/description")
    
    url: str = Field(..., description="Page URL")
    
    relevance_score: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Relevance score if available"
    )


class FileInfo(BaseModel):
    """Information about a file."""
    
    path: str = Field(..., description="File path")
    
    name: str = Field(..., description="File name")
    
    size: int = Field(..., ge=0, description="File size in bytes")
    
    extension: str = Field(..., description="File extension")
    
    mime_type: str | None = Field(None, description="MIME type if known")


class CodeExecutionResult(BaseModel):
    """Result from code execution."""
    
    output: str = Field(..., description="Code output")
    
    success: bool = Field(..., description="Whether code executed successfully")
    
    error: str | None = Field(None, description="Error message if failed")
    
    execution_time: float = Field(..., ge=0.0, description="Execution time in seconds")
    
    return_value: Any | None = Field(None, description="Return value if any")

