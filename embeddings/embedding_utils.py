"""
Embedding utilities for code processing and embedding generation.

This module provides utilities for extracting code blocks and generating embeddings.
"""

from typing import List, Dict
import ast
import re
from .embedding_manager import EmbeddingManager

# Create global instances for backward compatibility
_embedding_manager = EmbeddingManager()


class CodeProcessor:
    """Utility class for processing code and extracting functions."""
    
    @staticmethod
    def extract_python_functions(source_code: str) -> List[Dict]:
        """Extract function code blocks from Python source code.
        
        Args:
            source_code: Python source code as string
            
        Returns:
            List[Dict]: List of dictionaries with 'name' and 'code' keys
        """
        try:
            tree = ast.parse(source_code)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Get the function source code
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
                    
                    lines = source_code.split('\n')
                    function_lines = lines[start_line:end_line]
                    function_code = '\n'.join(function_lines)
                    
                    functions.append({
                        'name': node.name,
                        'code': function_code
                    })
            
            return functions
        except SyntaxError:
            # Fallback to regex-based extraction for malformed code
            return CodeProcessor._extract_functions_regex(source_code)
    
    @staticmethod
    def _extract_functions_regex(source_code: str) -> List[Dict]:
        """Fallback regex-based function extraction."""
        functions = []
        pattern = r'def\s+(\w+)\s*\([^)]*\)\s*:'
        
        for match in re.finditer(pattern, source_code):
            func_name = match.group(1)
            start_pos = match.start()
            
            # Find the end of the function (simplified)
            lines = source_code[start_pos:].split('\n')
            function_lines = []
            indent_level = None
            
            for line in lines:
                if indent_level is None and line.strip():
                    indent_level = len(line) - len(line.lstrip())
                    function_lines.append(line)
                elif indent_level is not None:
                    if line.strip() == '':
                        function_lines.append(line)
                    elif len(line) - len(line.lstrip()) > indent_level:
                        function_lines.append(line)
                    else:
                        break
            
            function_code = '\n'.join(function_lines)
            functions.append({
                'name': func_name,
                'code': function_code
            })
        
        return functions


def extract_python_functions(source_code: str) -> List[Dict]:
    """Extract function code blocks from Python source code.
    
    This function is now a wrapper around the new CodeProcessor.
    """
    functions = CodeProcessor.extract_python_functions(source_code)
    # Convert to legacy format for backward compatibility
    return [{'name': f['name'], 'code': f['code']} for f in functions]

def generate_embedding(code: str) -> List[float]:
    """Generate embeddings for a code block using the new LLM package.
    
    Args:
        code: The code block to generate embeddings for
        model_name: The name of the embedding model to use (default: text-embedding-ada-002)
        
    Returns:
        List[float]: The embedding vector
    """
    return _embedding_manager.generate_embedding(code)