"""
Enhanced LlamaIndex Workflow with Structured Outputs and Configuration.
This is the updated version using all the new improvements.
"""

from typing import Any, Optional
from dataclasses import dataclass

from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step,
    Event,
    Context,
)

from agent import create_agent, run_agent_with_retry
from config import get_settings
from config.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)

# Get settings
settings = get_settings()


# Custom Events
class ProcessQueryEvent(Event):
    """Event to process a query with the agent."""
    question: str
    task_id: Optional[str] = None


class ValidateAnswerEvent(Event):
    """Event to validate and clean the answer."""
    raw_answer: str
    question: str
    task_id: Optional[str] = None


class ErrorEvent(Event):
    """Event for error handling."""
    error: str
    question: str
    task_id: Optional[str] = None


class GAIAAgentWorkflow(Workflow):
    """
    Enhanced workflow for processing GAIA benchmark questions.
    
    Features:
    - Structured outputs via Pydantic
    - Configuration via Pydantic Settings
    - Retry logic for API failures
    - Proper error handling
    - Logging and observability
    
    Flow:
    1. StartEvent: Receives question and optional task_id
    2. ProcessQueryEvent: Agent processes the question using tools
    3. ValidateAnswerEvent: Validate and ensure clean format
    4. StopEvent: Return final answer
    """
    
    def __init__(
        self,
        use_structured_output: bool = False,
        verbose: bool = False,
        timeout: float = 300.0,
        **kwargs
    ):
        """
        Initialize the GAIA Agent Workflow.
        
        Args:
            use_structured_output: Whether to use structured LLM outputs
            verbose: Whether to print detailed logs
            timeout: Maximum execution time in seconds
        """
        super().__init__(timeout=timeout, **kwargs)
        
        self.use_structured_output = use_structured_output
        self.verbose = verbose
        
        # Agent will be created lazily
        self._agent = None
    
    def get_agent(self):
        """Lazy initialization of agent."""
        if self._agent is None:
            logger.info("Initializing agent in workflow...")
            self._agent = create_agent(
                use_structured_output=self.use_structured_output,
                verbose=self.verbose
            )
        return self._agent
    
    @step
    async def start(self, ctx: Context, ev: StartEvent) -> ProcessQueryEvent | ErrorEvent:
        """
        Entry point: receive question and task_id.
        
        Args:
            ctx: Workflow context
            ev: Start event with question and task_id
        
        Returns:
            ProcessQueryEvent to trigger agent processing or ErrorEvent
        """
        question = getattr(ev, "question", None)
        task_id = getattr(ev, "task_id", None)
        
        if not question:
            logger.error("No question provided in StartEvent")
            return ErrorEvent(
                error="No question provided",
                question="",
                task_id=task_id
            )
        
        logger.info(f"Workflow started for question: {question[:100]}...")
        if task_id:
            logger.info(f"Task ID: {task_id}")
        
        # Store in context for later use
        await ctx.store.set("question", question)
        await ctx.store.set("task_id", task_id)
        await ctx.store.set("start_time", __import__('time').time())
        
        return ProcessQueryEvent(question=question, task_id=task_id)
    
    @step
    async def process_query(
        self, ctx: Context, ev: ProcessQueryEvent
    ) -> ValidateAnswerEvent | ErrorEvent:
        """
        Process the query using the agent with retry logic.
        
        Args:
            ctx: Workflow context
            ev: Process query event
        
        Returns:
            ValidateAnswerEvent with the raw answer or ErrorEvent on failure
        """
        try:
            logger.info("Processing query with agent...")
            
            # Get the agent
            agent = self.get_agent()
            
            # Run the agent with retry logic
            raw_answer = await run_agent_with_retry(
                agent=agent,
                question=ev.question,
                task_id=ev.task_id,
                max_retries=settings.agent.max_retries
            )
            
            # Store raw answer in context
            await ctx.store.set("raw_answer", raw_answer)
            
            # Calculate elapsed time
            start_time = await ctx.store.get("start_time")
            elapsed = __import__('time').time() - start_time
            await ctx.store.set("elapsed_time", elapsed)
            
            logger.info(f"Agent completed in {elapsed:.2f}s")
            
            return ValidateAnswerEvent(
                raw_answer=raw_answer,
                question=ev.question,
                task_id=ev.task_id
            )
        
        except Exception as e:
            logger.error("Error processing query: {}", e, exc_info=True)
            return ErrorEvent(
                error=str(e),
                question=ev.question,
                task_id=ev.task_id
            )
    
    @step
    async def validate_answer(
        self, ctx: Context, ev: ValidateAnswerEvent
    ) -> StopEvent:
        """
        Validate and ensure the answer is in correct format.
        
        Args:
            ctx: Workflow context
            ev: Validate answer event
        
        Returns:
            StopEvent with the final cleaned answer
        """
        try:
            logger.info("Validating answer format...")
            
            answer = ev.raw_answer
            
            # If structured output was used, answer should already be clean
            # But we can add additional validation here if needed
            
            # Basic validation: check if answer is not empty
            if not answer or answer.strip() == "":
                logger.warning("Empty answer received")
                answer = "Unable to determine answer"
            
            # Check if it's an error message
            if answer.startswith("Error:"):
                logger.warning(f"Error in answer: {answer}")
            
            # Store final answer in context
            await ctx.store.set("final_answer", answer)
            
            # Get metadata
            elapsed_time = await ctx.store.get("elapsed_time") or 0.0
            
            logger.info(f"Final answer: {answer}")
            logger.info(f"Total time: {elapsed_time:.2f}s")
            
            return StopEvent(
                result={
                    "answer": answer,
                    "elapsed_time": elapsed_time,
                    "task_id": ev.task_id,
                }
            )
        
        except Exception as e:
            logger.error(f"Error validating answer: {e}", exc_info=True)
            # Return the raw answer if validation fails
            return StopEvent(
                result={
                    "answer": ev.raw_answer,
                    "elapsed_time": 0.0,
                    "task_id": ev.task_id,
                    "validation_error": str(e)
                }
            )
    
    @step
    async def handle_error(self, ctx: Context, ev: ErrorEvent) -> StopEvent:
        """
        Handle errors in the workflow.
        
        Args:
            ctx: Workflow context
            ev: Error event
        
        Returns:
            StopEvent with error information
        """
        logger.error(f"Workflow error: {ev.error}")
        
        # Store error in context
        await ctx.store.set("error", ev.error)
        
        # Get elapsed time if available
        start_time = await ctx.store.get("start_time")
        elapsed_time = 0.0
        if start_time:
            elapsed_time = __import__('time').time() - start_time
        
        # Return error as result
        return StopEvent(
            result={
                "answer": f"Error: {ev.error}",
                "elapsed_time": elapsed_time,
                "task_id": ev.task_id,
                "error": ev.error
            }
        )


async def run_workflow(
    question: str,
    task_id: Optional[str] = None,
    use_structured_output: bool = False,
    verbose: bool = False
) -> dict[str, Any]:
    """
    Convenience function to run the workflow.
    
    Args:
        question: The question to answer
        task_id: Optional GAIA task ID
        use_structured_output: Whether to use structured outputs
        verbose: Whether to print logs
    
    Returns:
        Dictionary with answer and metadata
    """
    workflow = GAIAAgentWorkflow(
        use_structured_output=use_structured_output,
        verbose=verbose,
        timeout=settings.agent.timeout
    )
    
    result = await workflow.run(
        question=question,
        task_id=task_id,
        timeout=settings.agent.timeout
    )
    
    return result


def run_workflow_sync(
    question: str,
    task_id: Optional[str] = None,
    use_structured_output: bool = False,
    verbose: bool = False
) -> str:
    """
    Synchronous wrapper for run_workflow.
    
    Args:
        question: The question to answer
        task_id: Optional GAIA task ID
        use_structured_output: Whether to use structured outputs
        verbose: Whether to print logs
    
    Returns:
        The final answer (string)
    """
    import asyncio
    
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, use nest_asyncio
            try:
                import nest_asyncio
                nest_asyncio.apply()
            except ImportError:
                logger.warning("nest_asyncio not installed. Install for better async support.")
            
            result = loop.run_until_complete(
                run_workflow(question, task_id, use_structured_output, verbose)
            )
        else:
            result = loop.run_until_complete(
                run_workflow(question, task_id, use_structured_output, verbose)
            )
    except RuntimeError:
        # No event loop, create a new one
        result = asyncio.run(
            run_workflow(question, task_id, use_structured_output, verbose)
        )
    
    # Extract answer from result
    if isinstance(result, dict):
        return result.get("answer", str(result))
    return str(result)


if __name__ == "__main__":
    # Test the enhanced workflow
    print("=" * 80)
    print("Testing Enhanced GAIA Agent Workflow")
    print("=" * 80)
    
    import asyncio
    
    async def test():
        # Test questions
        test_questions = [
            "What is the capital of France?",
            "What is 15 * 23?",
            "What is the square root of 256?",
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n[Test {i}] Question: {question}")
            print("-" * 80)
            
            result = await run_workflow(
                question=question,
                use_structured_output=False,
                verbose=True
            )
            
            print(f"Answer: {result['answer']}")
            print(f"Time: {result['elapsed_time']:.2f}s")
            
            if 'error' in result:
                print(f"Error: {result['error']}")
    
    try:
        asyncio.run(test())
        print("\n" + "=" * 80)
        print("✓ Workflow tests completed")
        print("=" * 80)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

