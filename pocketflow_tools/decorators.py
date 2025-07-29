"""
Decorators for marking PocketFlow nodes as tools
"""

from typing import Dict, List, Any, Optional, Union
import inspect
import re
from pocketflow import Node


class ToolRegistry:
    """Registry for managing tool nodes"""
    
    def __init__(self):
        self.tools: Dict[str, Dict] = {}
    
    def tool(self, name: str = None, description: str = None, parameters: Dict = None):
        """Decorator to mark a Node class as a tool"""
        def decorator(cls):
            tool_name = name or cls.__name__.lower()
            
            # Store tool metadata on the class
            cls._is_tool = True
            cls._tool_name = tool_name
            cls._tool_description = description or cls.__doc__ or f"Execute {tool_name}"
            cls._tool_parameters = parameters  # Store manually specified parameters
            
            # Add get_tool_spec method to the class
            def get_tool_spec(self):
                return {
                    'name': self._tool_name,
                    'description': self._tool_description,
                    'parameters': self._extract_parameters(),
                    'node_type': self._get_node_type()
                }
            
            cls.get_tool_spec = get_tool_spec
            
            # Add helper methods to the class
            def _extract_parameters(self):
                """Extract parameters using multiple strategies"""
                # Strategy 1: Use manually specified parameters
                if self._tool_parameters:
                    return self._tool_parameters
                
                # Strategy 2: Extract from method signature
                sig_params = self._extract_parameters_from_signature()
                if sig_params:
                    return sig_params
                
                # Strategy 3: Extract from docstring
                doc_params = self._extract_parameters_from_docstring()
                if doc_params:
                    return doc_params
                
                # Strategy 4: Default generic parameter
                return self._get_default_parameters()
            
            def _extract_parameters_from_signature(self):
                """Extract parameters from prep method signature"""
                try:
                    sig = inspect.signature(self.prep)
                    parameters = {}
                    
                    for param_name, param in sig.parameters.items():
                        if param_name not in ['self', 'shared']:
                            param_type = param.annotation if param.annotation != inspect.Parameter.empty else 'str'
                            param_default = param.default if param.default != inspect.Parameter.empty else None
                            
                            # Convert type annotation to string
                            if hasattr(param_type, '__name__'):
                                type_str = param_type.__name__
                            else:
                                type_str = str(param_type)
                            
                            parameters[param_name] = {
                                'type': type_str,
                                'required': param_default is None,
                                'default': param_default,
                                'description': f'Parameter {param_name}'
                            }
                    
                    return parameters
                except Exception:
                    return {}
            
            def _extract_parameters_from_docstring(self):
                """Extract parameters from docstring using intelligent parsing"""
                parameters = {}
                
                # Get docstrings from class and prep method
                class_doc = self.__class__.__doc__ or ""
                prep_doc = getattr(self.prep, '__doc__', "") or ""
                combined_doc = f"{class_doc}\n{prep_doc}"
                
                # Look for parameter patterns in docstring
                # Pattern 1: "param_name: type - description"
                param_pattern = r'(\w+)\s*:\s*(\w+)\s*[-–]\s*([^\n]+)'
                matches = re.findall(param_pattern, combined_doc)
                
                for param_name, param_type, description in matches:
                    parameters[param_name] = {
                        'type': param_type,
                        'required': True,
                        'default': None,
                        'description': description.strip()
                    }
                
                # Pattern 2: "Parameters:" section
                if 'Parameters:' in combined_doc:
                    param_section = combined_doc.split('Parameters:')[1].split('\n\n')[0]
                    # Parse parameter section
                    param_lines = param_section.strip().split('\n')
                    for line in param_lines:
                        line = line.strip()
                        if line.startswith('-') or line.startswith('*'):
                            # Extract parameter info from bullet points
                            param_match = re.search(r'(\w+)\s*\(([^)]+)\)\s*:\s*(.+)', line)
                            if param_match:
                                param_name, param_type, description = param_match.groups()
                                parameters[param_name] = {
                                    'type': param_type.strip(),
                                    'required': True,
                                    'default': None,
                                    'description': description.strip()
                                }
                
                # Pattern 3: Look for common parameter keywords
                if not parameters:
                    common_params = {
                        'query': {'type': 'str', 'description': 'Search query'},
                        'question': {'type': 'str', 'description': 'Question to process'},
                        'text': {'type': 'str', 'description': 'Text to process'},
                        'file': {'type': 'str', 'description': 'File path'},
                        'url': {'type': 'str', 'description': 'URL to process'},
                        'data': {'type': 'str', 'description': 'Data to process'},
                        'input': {'type': 'str', 'description': 'Input data'},
                        'prompt': {'type': 'str', 'description': 'Prompt text'},
                        'context': {'type': 'str', 'description': 'Context information'}
                    }
                    
                    for param_name, param_info in common_params.items():
                        if param_name in combined_doc.lower():
                            parameters[param_name] = {
                                'type': param_info['type'],
                                'required': True,
                                'default': None,
                                'description': param_info['description']
                            }
                
                return parameters
            
            def _get_default_parameters(self):
                """Provide default generic parameters"""
                return {
                    "input": {
                        'type': 'str',
                        'required': True,
                        'default': None,
                        'description': 'Input data for the tool'
                    }
                }
            
            def _get_node_type(self):
                """Determine the type of node (sync, batch, async, etc.)"""
                # Check for async methods first
                if hasattr(self, 'prep_async') or hasattr(self, 'exec_async'):
                    if hasattr(self, '_exec') and hasattr(self, '__iter__'):
                        return 'async_batch'
                    return 'async'
                # Check for batch methods
                elif hasattr(self, '_exec') and hasattr(self, '__iter__'):
                    return 'batch'
                # Default to sync
                return 'sync'
            
            cls._extract_parameters = _extract_parameters
            cls._extract_parameters_from_signature = _extract_parameters_from_signature
            cls._extract_parameters_from_docstring = _extract_parameters_from_docstring
            cls._get_default_parameters = _get_default_parameters
            cls._get_node_type = _get_node_type
            
            # Register the tool class
            self.tools[tool_name] = {
                'class': cls,
                'name': tool_name,
                'description': cls._tool_description
            }
            
            return cls
        return decorator
    
    def get_tool_spec(self, node_instance) -> Dict[str, Any]:
        """Get tool specification for a node instance"""
        if not hasattr(node_instance, '_is_tool') or not node_instance._is_tool:
            raise ValueError(f"Node {node_instance.__class__.__name__} is not registered as a tool")
        
        return {
            'name': node_instance._tool_name,
            'description': node_instance._tool_description,
            'parameters': node_instance._extract_parameters(),
            'node_type': node_instance._get_node_type()
        }
    
    def get_all_tool_specs(self) -> List[Dict[str, Any]]:
        """Get specifications for all registered tools"""
        specs = []
        for tool_info in self.tools.values():
            # Create a temporary instance to get the spec
            temp_instance = tool_info['class']()
            specs.append(self.get_tool_spec(temp_instance))
        return specs


# Global registry instance
tool_registry = ToolRegistry()

def tool(name: str = None, description: str = None, parameters: Dict = None):
    """Convenience decorator to mark a Node class as a tool"""
    return tool_registry.tool(name, description, parameters) 