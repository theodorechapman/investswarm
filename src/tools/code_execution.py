"""execution tool"""

import sys
from io import StringIO
from typing import Dict, Any


def execute_python_code(code: str) -> str:
    try:
        namespace = {
            "__builtins__": __builtins__,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "sorted": sorted,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
        }

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            exec(code, namespace)
            output = captured_output.getvalue()
            if 'result' in namespace:
                if output:
                    return f"{output}\nResult: {namespace['result']}"
                return str(namespace['result'])

            if output:
                return output
            results = {
                k: v for k, v in namespace.items()
                if not k.startswith('_') and k not in {
                    "abs", "round", "min", "max", "sum", "len", "range",
                    "enumerate", "zip", "sorted", "list", "dict", "set",
                    "tuple", "str", "int", "float", "bool"
                }
            }

            if results:
                return str(results)

            return "Code executed successfully (no output)"

        finally:
            sys.stdout = old_stdout

    except Exception as e:
        return f"Error executing code: {str(e)}"


def calculate_metrics(data: Dict[str, Any]) -> str:
    code = f"""
# Calculate metrics from provided data
data = {data}

# Example calculations
if 'revenue' in data and 'net_income' in data:
    profit_margin = (data['net_income'] / data['revenue']) * 100
    print(f"Profit Margin: {{profit_margin:.2f}}%")

if 'price' in data and 'eps' in data and data['eps'] > 0:
    pe_ratio = data['price'] / data['eps']
    print(f"P/E Ratio: {{pe_ratio:.2f}}")

result = "Metrics calculated successfully"
"""
    return execute_python_code(code)
