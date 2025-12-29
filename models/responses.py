"""Response models for structured LLM outputs."""

from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """
    Structured response from agent - optimized for GAIA exact match.
    
    This model ensures the agent returns only the answer without
    extra text like "FINAL ANSWER:" or explanations.
    """
    
    answer: str = Field(
        ...,
        description="The final answer ONLY. No explanations, no prefixes, just the answer."
    )
    
    confidence: float = Field(
        ...,
        description="Confidence score between 0 and 1"
    )
    
    tools_used: list[str] = Field(
        default_factory=list,
        description="List of tool names that were used"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "answer": "42",
                    "confidence": 0.95,
                    "tools_used": ["calculator"]
                },
                {
                    "answer": "Paris",
                    "confidence": 1.0,
                    "tools_used": ["wikipedia_search"]
                }
            ]
        }


class DetailedResponse(AgentResponse):
    """
    Extended response with reasoning information for debugging.
    """
    
    reasoning_steps: int = Field(
        ...,
        description="Number of reasoning steps taken"
    )
    
    intermediate_results: list[str] = Field(
        default_factory=list,
        description="Intermediate outputs from reasoning steps"
    )
    
    tokens_used: int | None = Field(
        None,
        description="Total tokens used (if available)"
    )
    
    execution_time: float | None = Field(
        None,
        description="Execution time in seconds"
    )


class ValidationResponse(BaseModel):
    """Response for answer validation."""
    
    is_valid: bool = Field(..., description="Whether the answer is valid")
    
    format_correct: bool = Field(
        ...,
        description="Whether the answer format is correct"
    )
    
    issues: list[str] = Field(
        default_factory=list,
        description="List of validation issues found"
    )
    
    suggested_fix: str | None = Field(
        None,
        description="Suggested correction if issues found"
    )


class ComparisonResponse(BaseModel):
    """Response for comparing agent answer with ground truth."""
    
    matches: bool = Field(..., description="Whether answers match")
    
    similarity: float = Field(
        ...,
        description="Similarity score"
    )
    
    agent_answer: str = Field(..., description="Agent's answer")
    
    ground_truth: str = Field(..., description="Ground truth answer")
    
    differences: list[str] = Field(
        default_factory=list,
        description="List of differences found"
    )

