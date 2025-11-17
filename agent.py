"""
Enhanced Agent with Structured Outputs and Pydantic Settings.
This is the updated version using all the new improvements.
"""

from typing import Optional

from llama_index.core.agent import ReActAgent
from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from llama_index.llms.openai import OpenAI

from config import get_settings
from config.logging_config import get_logger
from models.responses import AgentResponse
from prompts.system_prompts import MAIN_SYSTEM_PROMPT
from tools import get_all_tools

# Setup logging
logger = get_logger(__name__)

# Get settings
settings = get_settings()


def create_agent(
    use_structured_output: Optional[bool] = None,
    verbose: Optional[bool] = None
) -> ReActAgent:
    """
    Create and configure the ReAct agent with structured outputs.
    
    Args:
        use_structured_output: Whether to use structured outputs (default: from config)
        verbose: Whether to print reasoning steps (default: from config)
    
    Returns:
        Configured ReActAgent instance
    """
    logger.info("Creating enhanced agent with structured outputs...")
    
    # Use config defaults if not specified
    if use_structured_output is None:
        use_structured_output = settings.agent.use_structured_output
    
    if verbose is None:
        verbose = settings.agent.verbose
    
    # Initialize LLM based on configuration
    if settings.agent.use_openai:
        if not settings.api.openai_api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env")
        
        llm = OpenAI(
            model=settings.agent.model_name,
            temperature=settings.agent.temperature,
            api_key=settings.api.openai_api_key,
        )
        logger.info(f"Using OpenAI model: {settings.agent.model_name}")
    else:
        if not settings.api.hf_token:
            raise ValueError("HuggingFace token not found. Set HF_TOKEN in .env")
        
        llm = HuggingFaceInferenceAPI(
            model_name=settings.agent.model_name,
            token=settings.api.hf_token,
            temperature=settings.agent.temperature,
        )
        logger.info(f"Using HuggingFace model: {settings.agent.model_name}")
    
    # Convert to structured LLM if needed
    if use_structured_output:
        logger.info("Enabling structured output mode")
        llm = llm.as_structured_llm(output_cls=AgentResponse)
    
    # Get all tools from registry
    tools = get_all_tools()
    logger.info(f"Loaded {len(tools)} tools")
    
    # Create ReAct agent
    agent = ReActAgent.from_tools(
        tools=tools,
        llm=llm,
        verbose=verbose,
        max_iterations=settings.agent.max_iterations,
        system_prompt=MAIN_SYSTEM_PROMPT,
    )
    
    logger.info("Agent created successfully")
    return agent


def run_agent(
    agent: ReActAgent,
    question: str,
    task_id: Optional[str] = None
) -> str:
    """
    Run the agent on a question and return the cleaned answer.
    
    Args:
        agent: The configured ReActAgent
        question: The question to answer
        task_id: Optional GAIA task ID (for context)
    
    Returns:
        The agent's answer (cleaned and formatted)
    """
    try:
        logger.info(f"Running agent on question: {question[:100]}...")
        
        # Add task_id context if provided
        if task_id:
            question_with_context = f"[Task ID: {task_id}]\n\n{question}"
        else:
            question_with_context = question
        
        # Run the agent
        response = agent.chat(question_with_context)
        
        # Extract answer based on response type
        if isinstance(response, AgentResponse):
            # Structured output - answer is already clean
            answer = response.answer
            logger.info(f"Confidence: {response.confidence}")
            logger.info(f"Tools used: {response.tools_used}")
        elif hasattr(response, 'response'):
            # Standard response object
            answer = str(response.response)
            # Clean the answer
            answer = clean_answer(answer)
        else:
            # Fallback to string conversion
            answer = str(response)
            answer = clean_answer(answer)
        
        logger.info(f"Agent answer: {answer}")
        return answer
    
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        return f"Error: {str(e)}"


def clean_answer(answer: str) -> str:
    """
    Clean the agent's answer for GAIA exact match format.
    
    This is a fallback for when structured outputs aren't used.
    
    Args:
        answer: Raw answer from the agent
    
    Returns:
        Cleaned answer suitable for GAIA submission
    """
    # Remove common prefixes
    prefixes_to_remove = [
        "FINAL ANSWER:",
        "Final Answer:",
        "The answer is:",
        "The answer is",
        "Answer:",
        "Result:",
        "The result is:",
    ]
    
    for prefix in prefixes_to_remove:
        if answer.strip().startswith(prefix):
            answer = answer.strip()[len(prefix):].strip()
    
    # Remove quotes if the entire answer is quoted
    if answer.startswith('"') and answer.endswith('"'):
        answer = answer[1:-1]
    if answer.startswith("'") and answer.endswith("'"):
        answer = answer[1:-1]
    
    # Strip whitespace
    answer = answer.strip()
    
    return answer


def run_agent_with_retry(
    agent: ReActAgent,
    question: str,
    task_id: Optional[str] = None,
    max_retries: Optional[int] = None
) -> str:
    """
    Run agent with retry logic for API failures.
    
    Args:
        agent: The configured ReActAgent
        question: The question to answer
        task_id: Optional GAIA task ID
        max_retries: Maximum retry attempts (default: from config)
    
    Returns:
        The agent's answer or error message
    """
    import time
    
    if max_retries is None:
        max_retries = settings.agent.max_retries
    
    retry_delay = settings.agent.retry_delay
    
    for attempt in range(max_retries + 1):
        try:
            return run_agent(agent, question, task_id)
        
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed")
                return f"Error after {max_retries + 1} attempts: {str(e)}"


if __name__ == "__main__":
    # Test the enhanced agent
    print("=" * 80)
    print("Testing Enhanced Agent with Structured Outputs")
    print("=" * 80)
    
    try:
        # Validate configuration
        print("\n1. Validating configuration...")
        from config.settings import validate_settings
        issues = validate_settings()
        if issues:
            print("⚠️  Configuration issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✓ Configuration valid")
        
        # Create agent
        print("\n2. Creating agent...")
        agent = create_agent(use_structured_output=True, verbose=True)
        print("✓ Agent created")
        
        # Test with a simple question
        print("\n3. Testing with simple question...")
        test_question = "What is 2 + 2?"
        print(f"Question: {test_question}")
        
        answer = run_agent(agent, test_question)
        print(f"Answer: {answer}")
        
        # Test with calculator
        print("\n4. Testing with calculation...")
        calc_question = "What is the square root of 144?"
        print(f"Question: {calc_question}")
        
        answer = run_agent(agent, calc_question)
        print(f"Answer: {answer}")
        
        print("\n" + "=" * 80)
        print("✓ Agent tests completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

