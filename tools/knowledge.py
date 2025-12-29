"""Knowledge-based tools using LlamaIndex Readers."""

from typing import Optional

from llama_index.core.tools import FunctionTool
from llama_index.readers.wikipedia import WikipediaReader
from llama_index.readers.papers import ArxivReader
from llama_index.readers.weather import WeatherReader

from config import get_settings
from config.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)
settings = get_settings()


def search_wikipedia(query: str, max_pages: int = 3) -> str:
    """
    Search Wikipedia for factual information using official LlamaIndex reader.
    
    Args:
        query: The topic to search for
        max_pages: Maximum number of pages to retrieve (default: 3)
    
    Returns:
        Formatted Wikipedia content or error message
    """
    try:
        logger.info(f"Searching Wikipedia for: {query}")
        
        reader = WikipediaReader()
        
        # Load Wikipedia pages with auto-suggest
        docs = reader.load_data(
            pages=[query],
            auto_suggest=True,
            redirect=True
        )
        
        if not docs:
            return f"No Wikipedia articles found for: {query}"
        
        # Format results
        results = []
        for i, doc in enumerate(docs[:max_pages], 1):
            title = doc.metadata.get('title', 'Unknown')
            # Limit text to configured max chars
            max_chars = settings.tool.wikipedia_max_chars
            text = doc.text[:max_chars]
            
            results.append(f"[{i}] {title}\n{text}")
        
        return "\n\n---\n\n".join(results)
    
    except Exception as e:
        logger.error(f"Wikipedia search error: {e}")
        return f"Error searching Wikipedia: {str(e)}"


def search_arxiv(query: str, max_results: int = 3) -> str:
    """
    Search arXiv for academic papers using official LlamaIndex reader.
    
    Args:
        query: Search query for papers
        max_results: Maximum number of papers (default: 3)
    
    Returns:
        Formatted arXiv search results or error message
    """
    try:
        logger.info(f"Searching arXiv for: {query}")
        
        reader = ArxivReader()
        
        # Search arXiv
        docs = reader.load_data(
            search_query=query,
            max_results=max_results
        )
        
        if not docs:
            return f"No arXiv papers found for: {query}"
        
        # Format results
        results = []
        for i, doc in enumerate(docs, 1):
            title = doc.metadata.get('title', 'Unknown')
            authors = doc.metadata.get('authors', [])
            published = doc.metadata.get('published', 'Unknown date')
            
            # Format authors
            if isinstance(authors, list) and authors:
                author_str = ", ".join(authors[:3])
                if len(authors) > 3:
                    author_str += " et al."
            else:
                author_str = str(authors) if authors else "Unknown authors"
            
            # Get summary (first 500 chars)
            summary = doc.text[:500] + "..." if len(doc.text) > 500 else doc.text
            
            results.append(
                f"[{i}] {title}\n"
                f"Authors: {author_str}\n"
                f"Published: {published}\n"
                f"Summary: {summary}"
            )
        
        return "\n\n---\n\n".join(results)
    
    except Exception as e:
        logger.error(f"arXiv search error: {e}")
        return f"Error searching arXiv: {str(e)}"


def get_weather(location: str) -> str:
    """
    Get current weather information using official LlamaIndex reader.
    
    Args:
        location: Location name (e.g., "New York, USA" or "London, UK")
    
    Returns:
        Current weather information or error message
    """
    try:
        # Check if API key is configured
        if not settings.api.openweather_api_key:
            return "Weather API key not configured. Set OPENWEATHER_API_KEY in .env file."
        
        logger.info(f"Getting weather for: {location}")
        
        reader = WeatherReader(token=settings.api.openweather_api_key)
        
        # Get weather data
        docs = reader.load_data(places=[location])
        
        if not docs or not docs[0].text:
            return f"Weather data not available for: {location}"
        
        # The WeatherReader returns formatted weather data
        weather_info = docs[0].text
        
        return weather_info
    
    except Exception as e:
        logger.error(f"Weather retrieval error: {e}")
        return f"Error getting weather data: {str(e)}"


# Create FunctionTool instances
wikipedia_tool = FunctionTool.from_defaults(
    fn=search_wikipedia,
    name="wikipedia_search",
    description=(
        "Search Wikipedia for factual information, definitions, historical data, "
        "and general knowledge. Best for well-established facts and encyclopedic content. "
        "Use this for: biographies, historical events, scientific concepts, definitions."
    )
)

arxiv_tool = FunctionTool.from_defaults(
    fn=search_arxiv,
    name="arxiv_search",
    description=(
        "Search arXiv for academic papers, research findings, and scientific publications. "
        "Best for cutting-edge research and technical information. "
        "Use this for: research papers, scientific discoveries, academic studies, technical details."
    )
)

weather_tool = FunctionTool.from_defaults(
    fn=get_weather,
    name="weather",
    description=(
        "Get current weather information for a specific location. "
        "Provides temperature, conditions, humidity, and wind speed. "
        "Use this for: current weather queries, temperature checks, weather conditions. "
        "Format location as 'City, Country' (e.g., 'New York, USA' or 'London, UK')."
    )
)


# Export tools
KNOWLEDGE_TOOLS = [wikipedia_tool, arxiv_tool, weather_tool]

