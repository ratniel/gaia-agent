"""Web search tool using DuckDuckGo."""

from typing import Optional

from llama_index.core.tools import FunctionTool
from config import get_settings
from config.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)
settings = get_settings()


def search_web(query: str, max_results: Optional[int] = None) -> str:
    """
    Search the web using DuckDuckGo for current information.
    
    Args:
        query: The search query
        max_results: Maximum number of results (default: from config)
    
    Returns:
        Formatted search results or error message
    """
    try:
        from duckduckgo_search import DDGS
        
        if max_results is None:
            max_results = settings.tool.web_search_max_results
        
        logger.info(f"Searching web for: {query} (max_results={max_results})")
        
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                max_results=max_results,
                backend="auto"
            ))
        
        if not results:
            return f"No web search results found for: {query}"
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('body', 'No description')
            url = result.get('href', 'No URL')
            
            formatted_results.append(
                f"[{i}] {title}\n"
                f"{snippet}\n"
                f"URL: {url}"
            )
        
        return "\n\n---\n\n".join(formatted_results)
    
    except ImportError:
        error_msg = "DuckDuckGo search library not installed. Run: pip install duckduckgo-search"
        logger.error(error_msg)
        return error_msg
    
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return f"Error performing web search: {str(e)}"


def search_news(query: str, max_results: int = 5) -> str:
    """
    Search for recent news articles using DuckDuckGo.
    
    Args:
        query: The search query
        max_results: Maximum number of results (default: 5)
    
    Returns:
        Formatted news results or error message
    """
    try:
        from duckduckgo_search import DDGS
        
        logger.info(f"Searching news for: {query}")
        
        with DDGS() as ddgs:
            results = list(ddgs.news(
                query,
                max_results=max_results
            ))
        
        if not results:
            return f"No news articles found for: {query}"
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('body', 'No description')
            url = result.get('url', 'No URL')
            date = result.get('date', 'Unknown date')
            source = result.get('source', 'Unknown source')
            
            formatted_results.append(
                f"[{i}] {title}\n"
                f"Source: {source} | Date: {date}\n"
                f"{snippet}\n"
                f"URL: {url}"
            )
        
        return "\n\n---\n\n".join(formatted_results)
    
    except ImportError:
        error_msg = "DuckDuckGo search library not installed. Run: pip install duckduckgo-search"
        logger.error(error_msg)
        return error_msg
    
    except Exception as e:
        logger.error(f"News search error: {e}")
        return f"Error searching news: {str(e)}"


# Create FunctionTool instances
web_search_tool = FunctionTool.from_defaults(
    fn=search_web,
    name="web_search",
    description=(
        "Search the web using DuckDuckGo for current information, news, and real-time data. "
        "Best for: recent events, current information, news, up-to-date facts, "
        "information not in training data. Use this when you need fresh, current information."
    )
)

news_search_tool = FunctionTool.from_defaults(
    fn=search_news,
    name="news_search",
    description=(
        "Search for recent news articles and current events. "
        "Best for: breaking news, recent developments, current events, latest updates. "
        "Returns articles with date, source, and content."
    )
)


# Export tools
WEB_SEARCH_TOOLS = [web_search_tool, news_search_tool]

