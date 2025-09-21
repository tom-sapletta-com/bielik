#!/usr/bin/env python3
"""
Calculator Command - Advanced mathematical operations and calculations.

This command provides a powerful calculator with support for basic operations,
scientific functions, and expression evaluation.
"""

import ast
import operator
import math
import re
from typing import Dict, List, Any

# Import the command API from the parent package
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from bielik.cli.command_api import ContextProviderCommand


class CalculatorCommand(ContextProviderCommand):
    """Advanced calculator command with expression evaluation."""
    
    def __init__(self):
        super().__init__()
        self.name = "calc"
        self.description = "Advanced calculator with mathematical functions"
        
        # Safe operators for expression evaluation
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.BitXor: operator.xor,
            ast.USub: operator.neg,
        }
        
        # Mathematical functions
        self.functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'sinh': math.sinh,
            'cosh': math.cosh,
            'tanh': math.tanh,
            'log': math.log,
            'log10': math.log10,
            'log2': math.log2,
            'exp': math.exp,
            'sqrt': math.sqrt,
            'abs': abs,
            'ceil': math.ceil,
            'floor': math.floor,
            'round': round,
            'factorial': math.factorial,
            'degrees': math.degrees,
            'radians': math.radians,
        }
        
        # Mathematical constants
        self.constants = {
            'pi': math.pi,
            'e': math.e,
            'tau': math.tau,
            'inf': math.inf,
        }
    
    def provide_context(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate context data from calculator operations.
        
        Args:
            args: Command arguments (e.g., ['calc:', '2', '+', '3'])
            context: Current context data
            
        Returns:
            Dictionary with calculation results and context data
        """
        if len(args) < 2:  # args[0] is 'calc:'
            return {
                "error": "Please provide a mathematical expression",
                "help": "Usage: calc: 2 + 3 * 4",
                "calculation": None,
                "result": None
            }
        
        # Join all arguments after 'calc:' to form the expression
        expression = ' '.join(args[1:])
        
        try:
            # Handle special commands
            if expression.lower() in ['help', '?']:
                return {
                    "type": "help",
                    "content": self.get_help(),
                    "calculation": None,
                    "result": None
                }
            elif expression.lower() == 'functions':
                return {
                    "type": "functions_list",
                    "content": self._list_functions(),
                    "calculation": None,
                    "result": None
                }
            elif expression.lower() == 'constants':
                return {
                    "type": "constants_list", 
                    "content": self._list_constants(),
                    "calculation": None,
                    "result": None
                }
            
            # Evaluate the mathematical expression
            result = self._evaluate_expression(expression)
            
            return {
                "type": "calculation",
                "expression": expression,
                "result": result,
                "formatted_result": f"🧮 {expression} = {result}",
                "calculation": {
                    "input": expression,
                    "output": result,
                    "success": True
                }
            }
            
        except Exception as e:
            return {
                "type": "error",
                "expression": expression,
                "error": str(e),
                "formatted_result": f"❌ Calculation error: {str(e)}",
                "calculation": {
                    "input": expression,
                    "output": None,
                    "success": False,
                    "error": str(e)
                }
            }
    
    def _evaluate_expression(self, expr: str) -> float:
        """Safely evaluate a mathematical expression."""
        # Pre-process the expression
        expr = self._preprocess_expression(expr)
        
        try:
            # Parse the expression into an AST
            node = ast.parse(expr, mode='eval')
            return self._eval_node(node.body)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")
    
    def _preprocess_expression(self, expr: str) -> str:
        """Preprocess expression to handle functions and constants."""
        # Replace constants
        for const_name, const_value in self.constants.items():
            expr = re.sub(r'\b' + const_name + r'\b', str(const_value), expr)
        
        # Handle function calls - convert to Python function calls
        for func_name in self.functions.keys():
            pattern = r'\b' + func_name + r'\s*\('
            if re.search(pattern, expr):
                # Function call is already in correct format
                continue
        
        return expr
    
    def _eval_node(self, node):
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.BinOp):
            return self.operators[type(node.op)](
                self._eval_node(node.left), 
                self._eval_node(node.right)
            )
        elif isinstance(node, ast.UnaryOp):
            return self.operators[type(node.op)](self._eval_node(node.operand))
        elif isinstance(node, ast.Call):
            func_name = node.func.id
            if func_name in self.functions:
                args = [self._eval_node(arg) for arg in node.args]
                return self.functions[func_name](*args)
            else:
                raise ValueError(f"Unknown function: {func_name}")
        elif isinstance(node, ast.Name):
            if node.id in self.constants:
                return self.constants[node.id]
            else:
                raise ValueError(f"Unknown variable: {node.id}")
        else:
            raise ValueError(f"Unsupported operation: {type(node)}")
    
    def _list_functions(self) -> str:
        """List available mathematical functions."""
        funcs = []
        for func_name in sorted(self.functions.keys()):
            funcs.append(f"  {func_name}(x)")
        
        return "🔢 Available Functions:\n" + "\n".join(funcs)
    
    def _list_constants(self) -> str:
        """List available mathematical constants."""
        consts = []
        for const_name, const_value in sorted(self.constants.items()):
            consts.append(f"  {const_name} = {const_value}")
        
        return "📐 Available Constants:\n" + "\n".join(consts)
    
    def get_help(self) -> str:
        """Return help text for calculator command."""
        return """🧮 Calculator Command Help

Usage:
  calc: <expression>          # Evaluate mathematical expression
  calc: 2 + 3 * 4            # Basic arithmetic: 2 + 3 * 4 = 14
  calc: sqrt(16) + sin(pi/2) # Functions: sqrt(16) + sin(pi/2) = 5.0
  calc: 2**8                 # Powers: 2**8 = 256
  calc: log10(1000)          # Logarithms: log10(1000) = 3.0
  calc: factorial(5)         # Factorial: factorial(5) = 120

Special Commands:
  calc: functions            # List available functions
  calc: constants            # List available constants
  calc: help                 # Show this help

Supported Operations:
  +, -, *, /, ** (power), sqrt, sin, cos, tan, log, exp, etc.

Constants:
  pi, e, tau, inf

Examples:
  calc: (3 + 4) * 5
  calc: sin(pi/4) + cos(pi/4)
  calc: sqrt(2) * sqrt(8)
  calc: log(e**2)
"""

    def get_usage(self) -> str:
        """Return usage example."""
        return "calc: <mathematical_expression>"
