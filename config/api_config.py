"""API keys and endpoints configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings


class APIConfig(BaseSettings):
    """API keys and endpoints configuration."""
    
    # Required
    hf_token: str = Field(..., alias="HF_TOKEN", description="HuggingFace API token")
    
    # Optional API Keys
    openai_api_key: str | None = Field(
        None, 
        alias="OPENAI_API_KEY",
        description="OpenAI API key for enhanced multimodal support"
    )
    openweather_api_key: str | None = Field(
        None,
        alias="OPENWEATHER_API_KEY",
        description="OpenWeatherMap API key for weather data"
    )
    serper_api_key: str | None = Field(
        None,
        alias="SERPER_API_KEY",
        description="Serper API key for enhanced web search"
    )
    
    # GAIA Benchmark API
    gaia_api_url: str = Field(
        "https://agents-course-unit4-scoring.hf.space",
        alias="GAIA_API_URL",
        description="GAIA benchmark API base URL"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

