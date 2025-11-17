"""Agent behavior configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings


class AgentConfig(BaseSettings):
    """Agent behavior and model configuration."""
    
    # Model Selection
    model_name: str = Field(
        "Qwen/Qwen2.5-72B-Instruct",
        alias="AGENT_MODEL_NAME",
        description="LLM model name for the agent"
    )
    
    use_openai: bool = Field(
        False,
        alias="AGENT_USE_OPENAI",
        description="Whether to use OpenAI instead of HuggingFace"
    )
    
    # Agent Parameters
    temperature: float = Field(
        0.1,
        alias="AGENT_TEMPERATURE",
        ge=0.0,
        le=2.0,
        description="LLM temperature (lower = more deterministic)"
    )
    
    max_iterations: int = Field(
        15,
        alias="AGENT_MAX_ITERATIONS",
        ge=1,
        le=50,
        description="Maximum reasoning iterations"
    )
    
    verbose: bool = Field(
        True,
        alias="AGENT_VERBOSE",
        description="Whether to print reasoning steps"
    )
    
    use_structured_output: bool = Field(
        True,
        alias="AGENT_USE_STRUCTURED_OUTPUT",
        description="Whether to use structured LLM outputs"
    )
    
    # Retry Configuration
    max_retries: int = Field(
        3,
        alias="AGENT_MAX_RETRIES",
        ge=0,
        description="Maximum API call retries"
    )
    
    retry_delay: float = Field(
        1.0,
        alias="AGENT_RETRY_DELAY",
        ge=0.0,
        description="Delay between retries in seconds"
    )
    
    model_config = {
        "env_prefix": "AGENT_",
        "case_sensitive": False,
        "extra": "ignore",
    }

