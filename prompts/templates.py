"""Reusable prompt templates."""

from llama_index.core.prompts import PromptTemplate

# Answer Extraction Template
ANSWER_EXTRACTION_TEMPLATE = PromptTemplate(
    "Given the following information:\n\n"
    "{context}\n\n"
    "Question: {question}\n\n"
    "Instructions:\n"
    "1. Extract the exact answer from the context\n"
    "2. Provide ONLY the answer, no explanations\n"
    "3. Match the expected format exactly\n\n"
    "Answer:"
)

# Tool Selection Template
TOOL_SELECTION_TEMPLATE = PromptTemplate(
    "Question: {question}\n\n"
    "Available tools:\n{tools}\n\n"
    "Which tool(s) would be most helpful to answer this question?\n"
    "Consider:\n"
    "- What type of information is needed\n"
    "- Which tools can provide that information\n"
    "- The most efficient approach\n\n"
    "Explain your tool selection briefly."
)

# Validation Template
VALIDATION_TEMPLATE = PromptTemplate(
    "Validate this answer:\n\n"
    "Question: {question}\n"
    "Answer: {answer}\n\n"
    "Check:\n"
    "1. Does it directly answer the question?\n"
    "2. Is the format correct?\n"
    "3. Is it concise (no extra text)?\n"
    "4. Is it accurate?\n\n"
    "Validation result:"
)

# Answer Correction Template
ANSWER_CORRECTION_TEMPLATE = PromptTemplate(
    "Extract the core answer from this text:\n\n"
    "Raw text: {raw_answer}\n"
    "Question: {question}\n"
    "Expected format: {format}\n\n"
    "Return ONLY the core answer, nothing else."
)

# Context Synthesis Template
CONTEXT_SYNTHESIS_TEMPLATE = PromptTemplate(
    "Synthesize information from multiple sources:\n\n"
    "{sources}\n\n"
    "Question: {question}\n\n"
    "Combine the information to answer the question.\n"
    "Provide only the final answer."
)

# Reasoning Chain Template
REASONING_CHAIN_TEMPLATE = PromptTemplate(
    "Question: {question}\n\n"
    "Think step-by-step:\n"
    "1. What is being asked?\n"
    "2. What information do I need?\n"
    "3. How can I get that information?\n"
    "4. What is the final answer?\n\n"
    "Reasoning:"
)

# Multi-hop Question Template
MULTI_HOP_TEMPLATE = PromptTemplate(
    "This question requires multiple steps:\n\n"
    "Question: {question}\n\n"
    "Break it down:\n"
    "Step 1: {step1}\n"
    "Step 2: {step2}\n"
    "Step 3: {step3}\n\n"
    "Execute each step and combine results."
)

# Confidence Assessment Template
CONFIDENCE_ASSESSMENT_TEMPLATE = PromptTemplate(
    "Assess confidence in this answer:\n\n"
    "Question: {question}\n"
    "Answer: {answer}\n"
    "Sources: {sources}\n\n"
    "Consider:\n"
    "- Source reliability\n"
    "- Information consistency\n"
    "- Completeness\n"
    "- Certainty level\n\n"
    "Confidence score (0-1):"
)

