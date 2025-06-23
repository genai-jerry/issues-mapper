import ast
from typing import List, Dict

def extract_python_functions(source_code: str) -> List[Dict]:
    """Extract function code blocks from Python source code."""
    tree = ast.parse(source_code)
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
            func_code = '\n'.join(source_code.splitlines()[start_line:end_line])
            functions.append({
                'name': node.name,
                'code': func_code
            })
    return functions

def mock_generate_embedding(code: str) -> str:
    """Generate a mock embedding for a code block (for prototype)."""
    # In a real system, replace with a call to an embedding model
    return str(hash(code)) 