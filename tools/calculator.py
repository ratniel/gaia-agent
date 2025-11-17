"""Mathematical calculator tool using SymPy."""

from typing import Any

from llama_index.core.tools import FunctionTool
from config.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)


def calculate(expression: str) -> str:
    """
    Evaluate mathematical expressions using SymPy.
    
    Supports:
    - Basic arithmetic: +, -, *, /, **, %
    - Functions: sin, cos, tan, log, exp, sqrt, abs
    - Constants: pi, e
    - Symbolic math
    
    Args:
        expression: Mathematical expression to evaluate
    
    Returns:
        Result of the calculation or error message
    """
    try:
        import sympy
        
        logger.info(f"Calculating: {expression}")
        
        # Parse and evaluate the expression
        result = sympy.sympify(expression)
        
        # Try to get numerical value
        try:
            numerical_result = float(result.evalf())
            # Check if it's close to an integer
            if abs(numerical_result - round(numerical_result)) < 1e-10:
                return str(int(round(numerical_result)))
            else:
                return str(numerical_result)
        except (TypeError, AttributeError):
            # Return symbolic result
            return str(result)
    
    except ImportError:
        error_msg = "sympy not installed. Run: pip install sympy"
        logger.error(error_msg)
        return error_msg
    
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        return f"Error evaluating expression: {str(e)}"


def solve_equation(equation: str, variable: str = "x") -> str:
    """
    Solve an equation for a variable using SymPy.
    
    Args:
        equation: Equation to solve (e.g., "x**2 - 4 = 0")
        variable: Variable to solve for (default: "x")
    
    Returns:
        Solution(s) or error message
    """
    try:
        import sympy
        
        logger.info(f"Solving equation: {equation} for {variable}")
        
        # Parse the equation
        var = sympy.Symbol(variable)
        
        # Split by = if present
        if '=' in equation:
            left, right = equation.split('=')
            expr = sympy.sympify(left) - sympy.sympify(right)
        else:
            expr = sympy.sympify(equation)
        
        # Solve the equation
        solutions = sympy.solve(expr, var)
        
        if not solutions:
            return "No solutions found"
        
        # Format solutions
        if len(solutions) == 1:
            return f"{variable} = {solutions[0]}"
        else:
            solutions_str = ", ".join(str(sol) for sol in solutions)
            return f"{variable} = {solutions_str}"
    
    except ImportError:
        error_msg = "sympy not installed. Run: pip install sympy"
        logger.error(error_msg)
        return error_msg
    
    except Exception as e:
        logger.error(f"Equation solving error: {e}")
        return f"Error solving equation: {str(e)}"


def simplify_expression(expression: str) -> str:
    """
    Simplify a mathematical expression using SymPy.
    
    Args:
        expression: Expression to simplify
    
    Returns:
        Simplified expression or error message
    """
    try:
        import sympy
        
        logger.info(f"Simplifying: {expression}")
        
        expr = sympy.sympify(expression)
        simplified = sympy.simplify(expr)
        
        return str(simplified)
    
    except ImportError:
        error_msg = "sympy not installed. Run: pip install sympy"
        logger.error(error_msg)
        return error_msg
    
    except Exception as e:
        logger.error(f"Simplification error: {e}")
        return f"Error simplifying expression: {str(e)}"


# Create FunctionTool instances
calculator_tool = FunctionTool.from_defaults(
    fn=calculate,
    name="calculate",
    description=(
        "Evaluate mathematical expressions and perform calculations. "
        "Supports arithmetic operations, trigonometric functions, logarithms, "
        "exponents, and symbolic math. "
        "Examples: '2 + 2', 'sin(pi/2)', 'log(100, 10)', 'sqrt(16)', '2**10'. "
        "Use this for: calculations, mathematical operations, formula evaluation."
    )
)

equation_solver_tool = FunctionTool.from_defaults(
    fn=solve_equation,
    name="solve_equation",
    description=(
        "Solve equations for a variable. "
        "Format: provide equation (e.g., 'x**2 - 4 = 0') and optionally the variable. "
        "Returns solution(s) for the equation. "
        "Use this for: solving algebraic equations, finding roots, equation solving."
    )
)

simplify_tool = FunctionTool.from_defaults(
    fn=simplify_expression,
    name="simplify",
    description=(
        "Simplify mathematical expressions. "
        "Returns the simplified form of the expression. "
        "Use this for: simplifying complex expressions, algebraic simplification."
    )
)


# Export tools
CALCULATOR_TOOLS = [calculator_tool, equation_solver_tool, simplify_tool]

