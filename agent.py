"""
Enhanced Agent with Structured Outputs and Pydantic Settings.
This is the updated version using all the new improvements.
"""

import asyncio
from typing import Optional

from llama_index.core.agent import ReActAgent
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.llms.openai import OpenAI
from llama_index.llms.google_genai import GoogleGenAI

from config import get_settings
from config.logging_config import get_logger
from models.responses import AgentResponse
from prompts.system_prompts import MAIN_SYSTEM_PROMPT
from tools import get_all_tools

# Setup logging
logger = get_logger(__name__)


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
    
    settings = get_settings()
    
    # Use config defaults if not specified
    if use_structured_output is None:
        use_structured_output = settings.agent.use_structured_output
    
    if verbose is None:
        verbose = settings.agent.verbose
    
    # Initialize LLM based on flags
    model_name = settings.agent.model_name
    
    if settings.agent.use_openai:
        llm = OpenAI(
            model=model_name,
            temperature=settings.agent.temperature,
        )
        logger.info(f"Using OpenAI model: {model_name}")
    elif settings.agent.use_gemini:
        # LlamaIndex Gemini usually expects models/ prefix for some operations
        full_model_name = model_name if model_name.startswith("models/") else f"models/{model_name}"
        llm = GoogleGenAI(
            model=full_model_name,
            temperature=settings.agent.temperature,
            api_key=settings.api.gemini_api_key,
            max_retries=3,
            is_function_calling_model=True,
        )
        logger.info(f"Using Gemini model: {full_model_name}")
    elif settings.agent.use_hf:
        if not settings.api.hf_token:
            raise ValueError("HuggingFace token not found. Set HF_TOKEN in .env")
        
        llm = HuggingFaceInferenceAPI(
            model_name=model_name,
            token=settings.api.hf_token,
            temperature=settings.agent.temperature,
            provider="auto",
        )
        logger.info(f"Using HuggingFace model: {model_name}")
    else:
        # Fallback to model name detection if no flags set
        if any(x in model_name.lower() for x in ["gpt-", "o1-"]):
            llm = OpenAI(model=model_name, temperature=settings.agent.temperature)
        elif "gemini" in model_name.lower():
            full_model_name = model_name if model_name.startswith("models/") else f"models/{model_name}"
            llm = GoogleGenAI(
                model=full_model_name,
                temperature=settings.agent.temperature,
                api_key=settings.api.gemini_api_key,
                max_retries=3,
                is_function_calling_model=True,
            )
        else:
            llm = HuggingFaceInferenceAPI(
                model_name=model_name,
                token=settings.api.hf_token,
                temperature=settings.agent.temperature,
                provider="auto",
            )
        logger.info(f"Using detected model: {model_name}")
    
    # Convert to structured LLM if needed
    if use_structured_output:
        logger.info("Enabling structured output mode")
        llm = llm.as_structured_llm(output_cls=AgentResponse)
    
    # Get all tools from registry
    tools = get_all_tools()
    logger.info(f"Loaded {len(tools)} tools")
    
    # Create ReAct agent
    agent = ReActAgent(
        tools=tools,
        llm=llm,
        verbose=verbose,
        max_iterations=settings.agent.max_iterations,
        system_prompt=MAIN_SYSTEM_PROMPT,
        streaming=False,
    )
    
    logger.info("Agent created successfully")
    return agent


async def run_agent(
    agent: ReActAgent,
    question: str,
    task_id: Optional[str] = None
) -> str:
    """
    Run the agent- [x] Run quick_verify.py and identify the 'maximum' field error <!-- id: 0 -->
- [x] Fix the unknown field 'maximum' error <!-- id: 1 -->
- [x] Investigate and fix subsequent errors <!-- id: 2 -->
- [/] Verify successful execution of quick_verify.py <!-- id: 3 -->
    Returns:
        The agent's answer (cleaned and formatted)
    """
    try:
        logger.info(f"Running agent on question: {question}...")
        settings = get_settings()
        
        # Add task_id context if provided
        if task_id:
            question_with_context = f"[Task ID: {task_id}]\n\n{question}"
        else:
            question_with_context = question
        
        # Run the agent
        response = await agent.run(user_msg=question_with_context)
        
        # Extract answer based on response type
        # Extract answer based on response type
        if isinstance(response, AgentResponse):
            # Structured output - answer is already clean
            answer = response.answer
            logger.info(f"Confidence: {response.confidence}")
            logger.info(f"Tools used: {response.tools_used}")
        elif hasattr(response, 'response'):
            # Standard response object
            raw_response = str(response.response)
            logger.info(f"Raw response from agent: {raw_response}")
            
            # Check if this is a string representation of AgentResponse (Gemini often does this)
            is_gemini = settings.agent.use_gemini or "gemini" in settings.agent.model_name.lower()
            if is_gemini:
                try:
                    import json
                    import re
                    
                    # Try to extract JSON block
                    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                    json_text = None
                    if json_match:
                        logger.info(f"Found JSON block: {json_match.group()}")
                        json_text = json_match.group()
                    elif '","confidence":' in raw_response:
                        # Handle malformed case
                        logger.info("Handling malformed Gemini JSON response...")
                        text = raw_response
                        if text.lower().startswith("assistant:"):
                            text = text[10:].strip()
                        json_text = f'{{"answer": "{text}'
                        logger.info(f"Reconstructed JSON: {json_text}")
                    
                    if json_text:
                        data = json.loads(json_text)
                        parsed_response = AgentResponse(**data)
                        answer = parsed_response.answer
                        logger.info(f"Parsed structured output from string: {answer}")
                        return answer
                except Exception as parse_err:
                    logger.warning(f"Failed to parse JSON from response: {parse_err}")
            
            answer = clean_answer(raw_response, is_gemini=is_gemini)
        else:
            # Fallback to string conversion
            answer = str(response)
            answer = clean_answer(answer, is_gemini=settings.agent.use_gemini)
        
        logger.info(f"Agent answer: {answer}")
        return answer
    
    except Exception as e:
        logger.error("Error running agent: {}", e, exc_info=True)
        return f"Error: {str(e)}"


def clean_answer(answer: str, is_gemini: bool = False) -> str:
    """
    Clean the agent's answer for GAIA exact match format.
    
    This is a fallback for when structured outputs aren't used.
    
    Args:
        answer: Raw answer from the agent
        is_gemini: Whether the model is Gemini (applies extra cleaning)
    
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
    
    # Remove assistant: prefix if present (common with some models, especially Gemini)
    if is_gemini and answer.lower().startswith("assistant:"):
        answer = answer[10:].strip()
    
    # Remove quotes if the entire answer is quoted
    if answer.startswith('"') and answer.endswith('"'):
        answer = answer[1:-1]
    if answer.startswith("'") and answer.endswith("'"):
        answer = answer[1:-1]
    
    # Strip whitespace
    answer = answer.strip()
    
    return answer


async def run_agent_with_retry(
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
    
    settings = get_settings()
    
    if max_retries is None:
        max_retries = settings.agent.max_retries
    
    retry_delay = settings.agent.retry_delay
    
    for attempt in range(max_retries + 1):
        try:
            return await run_agent(agent, question, task_id)
        
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
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

