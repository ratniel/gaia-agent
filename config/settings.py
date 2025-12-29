"""Main settings module combining all configurations."""

from functools import lru_cache
from pydantic import BaseModel
from config.api_config import APIConfig
from config.agent_config import AgentConfig
from config.tool_config import ToolConfig


class Settings(BaseModel):
    """Main settings class combining all configurations."""
    
    api: APIConfig
    agent: AgentConfig
    tool: ToolConfig
    
    model_config = {
        "frozen": True,  # Make settings immutable
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings instance with all configurations loaded
    """
    return Settings(
        api=APIConfig(),
        agent=AgentConfig(),
        tool=ToolConfig(),
    )


def validate_settings() -> list[str]:
    """
    Validate settings and return list of issues.
    
    Returns:
        List of validation issues (empty if all valid)
    """
    issues = []
    
    try:
        settings = get_settings()
        
        # Check required API keys
        if not settings.api.openweather_api_key:
            issues.append("OPENWEATHER_API_KEY not set (optional, weather tool will be disabled)")
        
    except Exception as e:
        issues.append(f"Configuration error: {str(e)}")
    
    return issues


if __name__ == "__main__":
    print("=" * 80)
    print("GAIA Agent Configuration Validation")
    print("=" * 80)
    
    try:
        settings = get_settings()
        
        print("\n✓ Configuration loaded successfully\n")
        
        print("API Configuration:")
        print(f"  HF Token: {'✓ Set' if settings.api.hf_token else '✗ Not set'}")
        print(f"  Weather Key: {'✓ Set' if settings.api.openweather_api_key else '✗ Not set (optional)'}")
        print(f"  GAIA API: {settings.api.gaia_api_url}")
        
        print("\nAgent Configuration:")
        print(f"  Model: {settings.agent.model_name}")
        print(f"  Temperature: {settings.agent.temperature}")
        print(f"  Max Iterations: {settings.agent.max_iterations}")
        print(f"  Structured Output: {settings.agent.use_structured_output}")
        print(f"  Verbose: {settings.agent.verbose}")
        
        print("\nTool Configuration:")
        print(f"  Web Search Max Results: {settings.tool.web_search_max_results}")
        print(f"  arXiv Max Results: {settings.tool.arxiv_max_results}")
        print(f"  File Read Max Chars: {settings.tool.file_read_max_chars}")
        print(f"  Code Execution Timeout: {settings.tool.code_execution_timeout}s")
        
        # Validation
        issues = validate_settings()
        if issues:
            print("\n⚠️  Configuration Issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✓ All required configurations are valid")
        
    except Exception as e:
        print(f"\n✗ Error loading configuration: {e}")
        print("\nMake sure you have a .env file with HF_TOKEN set.")
    
    print("\n" + "=" * 80)

