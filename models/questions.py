"""Models for GAIA questions."""

from pydantic import BaseModel, Field


class GAIAQuestion(BaseModel):
    """Model for GAIA benchmark questions."""
    
    task_id: str = Field(..., description="Unique task identifier")
    
    question: str = Field(..., description="The question text")
    
    level: int | str = Field(..., description="Difficulty level (1, 2, or 3)")
    
    final_answer: str | None = Field(
        None,
        alias="Final answer",
        description="Ground truth answer (if available)"
    )
    
    file_name: str | None = Field(
        None,
        alias="file_name",
        description="Associated file name (if any)"
    )
    
    file_path: str | None = Field(
        None,
        description="Path to downloaded file (if any)"
    )
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "task_id": "task_001",
                "question": "What is the capital of France?",
                "level": 1,
                "Final answer": "Paris"
            }
        }


class GAIASubmission(BaseModel):
    """Model for GAIA benchmark submission."""
    
    username: str = Field(..., description="HuggingFace username")
    
    agent_code: str = Field(
        ...,
        description="URL to agent code repository"
    )
    
    answers: list[dict[str, str]] = Field(
        ...,
        description="List of answers with task_id and submitted_answer"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "my_username",
                "agent_code": "https://huggingface.co/spaces/my_space/tree/main",
                "answers": [
                    {"task_id": "task_001", "submitted_answer": "Paris"},
                    {"task_id": "task_002", "submitted_answer": "42"}
                ]
            }
        }


class GAIAResult(BaseModel):
    """Model for GAIA benchmark results."""
    
    task_id: str = Field(..., description="Task identifier")
    
    question: str = Field(..., description="The question")
    
    submitted_answer: str = Field(..., description="Agent's answer")
    
    ground_truth: str | None = Field(
        None,
        description="Ground truth answer"
    )
    
    correct: bool = Field(..., description="Whether answer is correct")
    
    level: int | str = Field(..., description="Question difficulty level")
    
    execution_time: float | None = Field(
        None,
        ge=0.0,
        description="Time taken to answer"
    )
    
    tools_used: list[str] = Field(
        default_factory=list,
        description="Tools used for this question"
    )

