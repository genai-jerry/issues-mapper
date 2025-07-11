"""
LLM Utilities Module

Provides utility functions for code processing and analysis.
"""

import ast
import re
from typing import List, Dict, Optional, Any
from pathlib import Path


class CodeProcessor:
    """Utility class for processing and analyzing code."""
    
    @staticmethod
    def extract_python_functions(source_code: str) -> List[Dict[str, Any]]:
        """Extract function code blocks from Python source code.
        
        Args:
            source_code: Python source code as string
            
        Returns:
            List[Dict]: List of function dictionaries with name, code, and metadata
        """
        try:
            tree = ast.parse(source_code)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
                    func_code = '\n'.join(source_code.splitlines()[start_line:end_line])
                    
                    # Extract function metadata
                    metadata = {
                        'name': node.name,
                        'code': func_code,
                        'start_line': node.lineno,
                        'end_line': end_line,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
                        'docstring': ast.get_docstring(node),
                        'returns': CodeProcessor._extract_return_type(node)
                    }
                    
                    functions.append(metadata)
            
            return functions
            
        except SyntaxError as e:
            print(f"Syntax error in code: {e}")
            return []
        except Exception as e:
            print(f"Error extracting functions: {e}")
            return []
    
    @staticmethod
    def extract_python_classes(source_code: str) -> List[Dict[str, Any]]:
        """Extract class definitions from Python source code.
        
        Args:
            source_code: Python source code as string
            
        Returns:
            List[Dict]: List of class dictionaries with name, code, and metadata
        """
        try:
            tree = ast.parse(source_code)
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
                    class_code = '\n'.join(source_code.splitlines()[start_line:end_line])
                    
                    # Extract class metadata
                    metadata = {
                        'name': node.name,
                        'code': class_code,
                        'start_line': node.lineno,
                        'end_line': end_line,
                        'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
                        'methods': [],
                        'docstring': ast.get_docstring(node)
                    }
                    
                    # Extract methods within the class
                    for child in ast.walk(node):
                        if isinstance(child, ast.FunctionDef) and child != node:
                            method_metadata = {
                                'name': child.name,
                                'args': [arg.arg for arg in child.args.args],
                                'docstring': ast.get_docstring(child),
                                'returns': CodeProcessor._extract_return_type(child)
                            }
                            metadata['methods'].append(method_metadata)
                    
                    classes.append(metadata)
            
            return classes
            
        except SyntaxError as e:
            print(f"Syntax error in code: {e}")
            return []
        except Exception as e:
            print(f"Error extracting classes: {e}")
            return []
    
    @staticmethod
    def extract_imports(source_code: str) -> Dict[str, List[str]]:
        """Extract import statements from Python source code.
        
        Args:
            source_code: Python source code as string
            
        Returns:
            Dict: Dictionary with 'imports' and 'from_imports' lists
        """
        try:
            tree = ast.parse(source_code)
            imports = []
            from_imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        from_imports.append(f"{module}.{alias.name}")
            
            return {
                'imports': imports,
                'from_imports': from_imports
            }
            
        except SyntaxError as e:
            print(f"Syntax error in code: {e}")
            return {'imports': [], 'from_imports': []}
    
    @staticmethod
    def analyze_code_complexity(source_code: str) -> Dict[str, Any]:
        """Analyze code complexity metrics.
        
        Args:
            source_code: Python source code as string
            
        Returns:
            Dict: Complexity metrics
        """
        try:
            tree = ast.parse(source_code)
            
            # Count various elements
            functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            imports = len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])
            
            # Count lines
            lines = source_code.splitlines()
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            comment_lines = len([line for line in lines if line.strip().startswith('#')])
            blank_lines = total_lines - code_lines - comment_lines
            
            # Calculate cyclomatic complexity (simplified)
            complexity = 1  # Base complexity
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            
            return {
                'total_lines': total_lines,
                'code_lines': code_lines,
                'comment_lines': comment_lines,
                'blank_lines': blank_lines,
                'functions': functions,
                'classes': classes,
                'imports': imports,
                'cyclomatic_complexity': complexity,
                'comment_ratio': comment_lines / total_lines if total_lines > 0 else 0
            }
            
        except SyntaxError as e:
            print(f"Syntax error in code: {e}")
            return {}
    
    @staticmethod
    def extract_code_blocks(source_code: str, language: str = "python") -> List[Dict[str, Any]]:
        """Extract code blocks from source code.
        
        Args:
            source_code: Source code as string
            language: Programming language
            
        Returns:
            List[Dict]: List of code blocks with metadata
        """
        if language.lower() == "python":
            functions = CodeProcessor.extract_python_functions(source_code)
            classes = CodeProcessor.extract_python_classes(source_code)
            
            blocks = []
            
            # Add functions
            for func in functions:
                blocks.append({
                    'type': 'function',
                    'name': func['name'],
                    'code': func['code'],
                    'metadata': func
                })
            
            # Add classes
            for cls in classes:
                blocks.append({
                    'type': 'class',
                    'name': cls['name'],
                    'code': cls['code'],
                    'metadata': cls
                })
            
            return blocks
        else:
            # For other languages, return the entire code as one block
            return [{
                'type': 'file',
                'name': 'main',
                'code': source_code,
                'metadata': {}
            }]
    
    @staticmethod
    def format_code_for_analysis(code: str, include_metadata: bool = True) -> str:
        """Format code for LLM analysis.
        
        Args:
            code: Code to format
            include_metadata: Whether to include metadata comments
            
        Returns:
            str: Formatted code
        """
        if not include_metadata:
            return code
        
        # Add basic metadata
        lines = code.splitlines()
        formatted_lines = []
        
        # Add header
        formatted_lines.append("# Code Analysis Target")
        formatted_lines.append("# " + "=" * 50)
        
        # Add original code
        formatted_lines.extend(lines)
        
        # Add footer
        formatted_lines.append("# " + "=" * 50)
        formatted_lines.append("# End of Code")
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def _extract_return_type(node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation from function definition."""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
            else:
                return ast.unparse(node.returns)
        return None
    
    @staticmethod
    def validate_python_syntax(source_code: str) -> Dict[str, Any]:
        """Validate Python syntax and return any errors.
        
        Args:
            source_code: Python source code as string
            
        Returns:
            Dict: Validation results
        """
        try:
            ast.parse(source_code)
            return {
                'valid': True,
                'errors': []
            }
        except SyntaxError as e:
            return {
                'valid': False,
                'errors': [{
                    'line': e.lineno,
                    'column': e.offset,
                    'message': str(e)
                }]
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [{
                    'line': None,
                    'column': None,
                    'message': str(e)
                }]
            } 