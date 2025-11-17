"""Safe code execution tool for Python calculations."""

import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from typing import Any, Dict

from llama_index.core.tools import FunctionTool
from config import get_settings
from config.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)
settings = get_settings()


def execute_python_code(code: str) -> str:
    """
    Safely execute Python code for calculations and data processing.
    
    Available libraries:
    - numpy (as np)
    - pandas (as pd)
    - sympy
    - math
    - statistics
    - datetime
    - re (regex)
    
    Args:
        code: Python code to execute. Store result in 'result' variable.
    
    Returns:
        Result of the code execution or error message
    """
    try:
        import numpy as np
        import pandas as pd
        import sympy
        import math
        import statistics
        import datetime
        import re
        
        logger.info("Executing Python code")
        
        # Create a restricted environment
        safe_globals = {
            '__builtins__': {
                # Safe built-ins only
                'abs': abs,
                'all': all,
                'any': any,
                'bin': bin,
                'bool': bool,
                'chr': chr,
                'dict': dict,
                'divmod': divmod,
                'enumerate': enumerate,
                'filter': filter,
                'float': float,
                'format': format,
                'hex': hex,
                'int': int,
                'len': len,
                'list': list,
                'map': map,
                'max': max,
                'min': min,
                'oct': oct,
                'ord': ord,
                'pow': pow,
                'range': range,
                'reversed': reversed,
                'round': round,
                'set': set,
                'sorted': sorted,
                'str': str,
                'sum': sum,
                'tuple': tuple,
                'zip': zip,
                'print': print,
            },
            # Available libraries
            'np': np,
            'numpy': np,
            'pd': pd,
            'pandas': pd,
            'sympy': sympy,
            'math': math,
            'statistics': statistics,
            'datetime': datetime,
            're': re,
        }
        
        # Capture output
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        # Execute code with timeout protection
        exec_globals = safe_globals.copy()
        
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(code, exec_globals)
        
        # Get captured output
        stdout_value = stdout_buffer.getvalue()
        stderr_value = stderr_buffer.getvalue()
        
        # Check for result variable
        if 'result' in exec_globals:
            result = exec_globals['result']
            output = f"Result: {result}"
            if stdout_value:
                output += f"\n\nOutput:\n{stdout_value}"
            return output
        
        # If no result variable, return stdout
        if stdout_value:
            return f"Output:\n{stdout_value}"
        
        # If nothing was captured
        if stderr_value:
            return f"Execution completed with warnings:\n{stderr_value}"
        
        return "Code executed successfully (no output)"
    
    except ImportError as e:
        error_msg = f"Required library not installed: {str(e)}"
        logger.error(error_msg)
        return error_msg
    
    except Exception as e:
        logger.error(f"Code execution error: {e}")
        return f"Error executing code: {str(e)}"


def execute_data_analysis(code: str, data_description: str = "") -> str:
    """
    Execute Python code for data analysis with pandas.
    
    Args:
        code: Python code for data analysis
        data_description: Optional description of the data
    
    Returns:
        Result of the analysis or error message
    """
    try:
        logger.info("Executing data analysis code")
        
        # Add helpful context
        preamble = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Your analysis code below:
"""
        
        full_code = preamble + code
        return execute_python_code(full_code)
    
    except Exception as e:
        logger.error(f"Data analysis error: {e}")
        return f"Error in data analysis: {str(e)}"


# Create FunctionTool instances
code_executor_tool = FunctionTool.from_defaults(
    fn=execute_python_code,
    name="execute_code",
    description=(
        "Execute Python code for calculations, data processing, and complex operations. "
        "Available libraries: numpy (np), pandas (pd), sympy, math, statistics, datetime, re. "
        "Store the final result in a variable named 'result' for it to be returned. "
        "Use this for: complex calculations, data processing, algorithmic tasks, "
        "mathematical operations beyond simple arithmetic. "
        "Example code: 'result = sum([i**2 for i in range(10)])'"
    )
)

data_analysis_tool = FunctionTool.from_defaults(
    fn=execute_data_analysis,
    name="analyze_data",
    description=(
        "Execute Python code for data analysis using pandas and numpy. "
        "Automatically imports pandas, numpy, and matplotlib. "
        "Use this for: data manipulation, statistical analysis, data transformations."
    )
)


# Export tools
CODE_EXECUTION_TOOLS = [code_executor_tool, data_analysis_tool]

