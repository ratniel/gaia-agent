"""Tool registry for managing all available tools."""

from typing import Dict, List, Optional

from llama_index.core.tools import BaseTool

from tools.knowledge import KNOWLEDGE_TOOLS
from tools.web_search import WEB_SEARCH_TOOLS
from tools.files import FILE_TOOLS
from tools.calculator import CALCULATOR_TOOLS
from tools.code_execution import CODE_EXECUTION_TOOLS
from config.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)

# Central tool registry
_TOOL_REGISTRY: Dict[str, BaseTool] = {}


def register_tool(tool: BaseTool) -> None:
    """
    Register a tool in the central registry.
    
    Args:
        tool: The tool to register
    """
    tool_name = tool.metadata.name
    if tool_name in _TOOL_REGISTRY:
        logger.warning(f"Tool '{tool_name}' already registered. Overwriting.")
    
    _TOOL_REGISTRY[tool_name] = tool
    logger.info(f"Registered tool: {tool_name}")


def get_tool_by_name(tool_name: str) -> Optional[BaseTool]:
    """
    Get a tool by its name.
    
    Args:
        tool_name: Name of the tool
    
    Returns:
        The tool if found, None otherwise
    """
    return _TOOL_REGISTRY.get(tool_name)


def get_all_tools() -> List[BaseTool]:
    """
    Get all registered tools.
    
    Returns:
        List of all available tools
    """
    # Register all tools if registry is empty
    if not _TOOL_REGISTRY:
        _register_all_tools()
    
    return list(_TOOL_REGISTRY.values())


def get_tools_by_category(category: str) -> List[BaseTool]:
    """
    Get tools by category.
    
    Args:
        category: Category name (knowledge, web_search, files, calculator, code_execution)
    
    Returns:
        List of tools in that category
    """
    category_map = {
        "knowledge": KNOWLEDGE_TOOLS,
        "web_search": WEB_SEARCH_TOOLS,
        "files": FILE_TOOLS,
        "calculator": CALCULATOR_TOOLS,
        "code_execution": CODE_EXECUTION_TOOLS,
    }
    
    return category_map.get(category, [])


def list_available_tools() -> Dict[str, str]:
    """
    List all available tools with their descriptions.
    
    Returns:
        Dictionary mapping tool names to descriptions
    """
    all_tools = get_all_tools()
    return {
        tool.metadata.name: tool.metadata.description
        for tool in all_tools
    }


def _register_all_tools() -> None:
    """Register all tools in the central registry."""
    logger.info("Registering all tools...")
    
    # Register each category
    for tool in KNOWLEDGE_TOOLS:
        register_tool(tool)
    
    for tool in WEB_SEARCH_TOOLS:
        register_tool(tool)
    
    for tool in FILE_TOOLS:
        register_tool(tool)
    
    for tool in CALCULATOR_TOOLS:
        register_tool(tool)
    
    for tool in CODE_EXECUTION_TOOLS:
        register_tool(tool)
    
    logger.info(f"Registered {len(_TOOL_REGISTRY)} tools total")


def print_tool_summary() -> None:
    """Print a summary of all available tools."""
    tools = get_all_tools()
    
    print("=" * 80)
    print("AVAILABLE TOOLS SUMMARY")
    print("=" * 80)
    
    categories = {
        "Knowledge Tools": KNOWLEDGE_TOOLS,
        "Web Search Tools": WEB_SEARCH_TOOLS,
        "File Tools": FILE_TOOLS,
        "Calculator Tools": CALCULATOR_TOOLS,
        "Code Execution Tools": CODE_EXECUTION_TOOLS,
    }
    
    for category_name, category_tools in categories.items():
        print(f"\n{category_name} ({len(category_tools)}):")
        for tool in category_tools:
            print(f"  - {tool.metadata.name}")
            desc = tool.metadata.description
            # Print first 100 chars of description
            desc_short = desc[:100] + "..." if len(desc) > 100 else desc
            print(f"    {desc_short}")
    
    print(f"\nTotal tools: {len(tools)}")
    print("=" * 80)


# Initialize registry on import
_register_all_tools()


if __name__ == "__main__":
    # Test the registry
    print_tool_summary()
    
    print("\n" + "=" * 80)
    print("TOOL DETAILS")
    print("=" * 80)
    
    all_tools = get_all_tools()
    for tool in all_tools:
        print(f"\nTool: {tool.metadata.name}")
        print(f"Description: {tool.metadata.description}")
        print(f"Function: {tool.metadata.fn_schema}")

