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
    logger.info("Creating agent...")
    
    settings = get_settings()
    
    # Use config defaults if not specified
    if use_structured_output is None:
        use_structured_output = settings.agent.use_structured_output
    
    if verbose is None:
        verbose = settings.agent.verbose
    
    # Initialize LLM based on flags
    model_name = settings.agent.model_name
    use_openai = settings.agent.use_openai
    use_gemini = settings.agent.use_gemini
    use_hf = settings.agent.use_hf
    
    logger.info(f"Model: {model_name} | Gemini: {use_gemini} | HF: {use_hf}")
    
    if use_openai:
        llm = OpenAI(
            model=model_name,
            temperature=settings.agent.temperature,
        )
        logger.info(f"Using OpenAI model: {model_name}")
    elif use_gemini:
        llm = GoogleGenAI(
            model=model_name,
            temperature=settings.agent.temperature,
            api_key=settings.api.gemini_api_key,
            max_retries=3,
            is_function_calling_model=True,
        )
        logger.info(f"Using Gemini model: {model_name}")
    elif use_hf:
        if not settings.api.hf_token:
            raise ValueError("HuggingFace token not found. Set HF_TOKEN in .env")
        
        llm = HuggingFaceInferenceAPI(
            model_name=model_name,
            token=settings.api.hf_token,
            temperature=settings.agent.temperature,
            provider="auto",
            # provider='zai-org',
            additional_kwargs={
                "max_new_tokens": 1024,
                "bill_to": "discord-community"
            }
        )
        logger.info(f"Using HuggingFace model: {model_name}")
    else:
        # Fallback to model name detection
        if "gemini" in model_name.lower():
            llm = GoogleGenAI(
                model=model_name,
                temperature=settings.agent.temperature,
                api_key=settings.api.gemini_api_key,
                max_retries=3,
                is_function_calling_model=True,
            )
        elif any(x in model_name.lower() for x in ["gpt-", "o1-"]):
            llm = OpenAI(model=model_name, temperature=settings.agent.temperature)
        else:
            llm = HuggingFaceInferenceAPI(
                model_name=model_name,
                token=settings.api.hf_token,
                temperature=settings.agent.temperature,
                provider="auto",
                additional_kwargs={"max_new_tokens": 1024}
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
        
        # Run the agent with internal retry for rate limits
        max_rate_limit_retries = 3
        for rate_attempt in range(max_rate_limit_retries + 1):
            try:
                # Try achat if available, otherwise fallback to run
                if hasattr(agent, 'achat'):
                    response = await agent.achat(message=question_with_context)
                    raw_response = str(response.response if hasattr(response, 'response') else response)
                else:
                    response = await agent.run(user_msg=question_with_context)
                    raw_response = str(response.response if hasattr(response, 'response') else response)
                break # Success
            except Exception as run_err:
                err_msg = str(run_err)
                if ("429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg) and rate_attempt < max_rate_limit_retries:
                    logger.warning(f"Internal Rate Limit hit. Waiting 60s (attempt {rate_attempt+1}/{max_rate_limit_retries})...")
                    await asyncio.sleep(60.0)
                    continue
                
                if rate_attempt == max_rate_limit_retries:
                    logger.error(f"Failed after {max_rate_limit_retries} rate limit retries.")
                    raise run_err
                
                # For non-rate-limit errors, just try run as fallback once
                logger.warning(f"Error calling agent: {run_err}. Trying agent.run as fallback...")
                response = await agent.run(user_msg=question_with_context)
                raw_response = str(response.response if hasattr(response, 'response') else response)
                break
        
        # Extract answer based on response type
        if isinstance(response, AgentResponse):
            # Structured output - answer is already clean
            answer = response.answer
            logger.info(f"Confidence: {response.confidence}")
            logger.info(f"Tools used: {response.tools_used}")
        else:
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
                    
                    if json_text:
                        data = json.loads(json_text)
                        parsed_response = AgentResponse(**data)
                        answer = parsed_response.answer
                        logger.info(f"Parsed structured output from string: {answer}")
                        return answer
                except Exception as parse_err:
                    logger.warning(f"Failed to parse JSON from response: {parse_err}")
            
            answer = clean_answer(raw_response, is_gemini=is_gemini)
        
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
    # Try to extract from "FINAL ANSWER: [answer]"
    import re
    final_answer_match = re.search(r"FINAL ANSWER:\s*(.*)", answer, re.IGNORECASE | re.DOTALL)
    if final_answer_match:
        answer = final_answer_match.group(1).strip()

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
    
    # If there's still a lot of text (e.g. reasoning didn't use FINAL ANSWER),
    # try to take the last line if it's short
    if "\n" in answer and len(answer) > 100:
        lines = [l.strip() for l in answer.split("\n") if l.strip()]
        if lines:
            last_line = lines[-1]
            if len(last_line) < 50:
                answer = last_line
    
    return answer


async def run_agent_with_retry(
    agent: ReActAgent,
    question: str,
    task_id: Optional[str] = None,
    max_retries: Optional[int] = None
) -> str:
    """
    Run agent with retry logic for API failures, including rate limits.
    
    Args:
        agent: The configured ReActAgent
        question: The question to answer
        task_id: Optional GAIA task ID
        max_retries: Maximum retry attempts (default: from config)
    
    Returns:
        The agent's answer or error message
    """
    import time
    import random
    
    settings = get_settings()
    
    if max_retries is None:
        # Increase default retries for rate limits
        max_retries = max(settings.agent.max_retries, 5)
    
    base_delay = settings.agent.retry_delay
    
    for attempt in range(max_retries + 1):
        try:
            return await run_agent(agent, question, task_id)
        
        except Exception as e:
            error_str = str(e)
            is_rate_limit = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str
            
            if attempt < max_retries:
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + (random.random() * base_delay)
                
                # If specifically a rate limit, ensure we wait at least 30-60s
                if is_rate_limit:
                    delay = max(delay, 30.0 + random.random() * 10)
                    logger.warning(f"Rate limit hit. Waiting {delay:.2f}s before retry {attempt + 1}/{max_retries}...")
                else:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed")
                return f"Error after {max_retries + 1} attempts: {str(e)}"


if __name__ == "__main__":
    # Test the enhanced agent
    print("=" * 80)
    print("Testing Enhanced Agent without Structured Outputs")
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
        agent = create_agent(use_structured_output=False, verbose=True)
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

