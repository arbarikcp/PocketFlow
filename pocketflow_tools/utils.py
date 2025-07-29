"""
Utility functions for PocketFlow tools
"""

from typing import List, Dict, Any


class ActionSpaceGenerator:
    """Generate action space descriptions from tool specifications"""
    
    @staticmethod
    def generate_action_space(tools: List[Any]) -> str:
        """Generate action space description from available tools"""
        action_space = []
        
        for i, tool in enumerate(tools, 1):
            # If tool is a node instance, get its spec
            if hasattr(tool, 'get_tool_spec'):
                tool_spec = tool.get_tool_spec()
            elif isinstance(tool, dict):
                tool_spec = tool
            else:
                # Skip tools that don't have proper specs
                continue
            
            action_space.append(f"""[{i}] {tool_spec['name']}
  Description: {tool_spec['description']}
  Type: {tool_spec.get('node_type', 'sync')}
  Parameters:""")
            
            parameters = tool_spec.get('parameters', {})
            if parameters:
                for param_name, param_spec in parameters.items():
                    required = "required" if param_spec.get('required', True) else "optional"
                    param_type = param_spec.get('type', 'str')
                    description = param_spec.get('description', '')
                    action_space.append(f"    - {param_name} ({param_type}, {required}): {description}")
            else:
                action_space.append("    - No parameters required")
        
        return "\n".join(action_space)
    
    @staticmethod
    def generate_action_space_dict(tools: List[Any]) -> Dict[str, Any]:
        """Generate action space as a structured dictionary"""
        action_space = {
            "tools": [],
            "total_tools": 0
        }
        
        for i, tool in enumerate(tools, 1):
            # If tool is a node instance, get its spec
            if hasattr(tool, 'get_tool_spec'):
                tool_spec = tool.get_tool_spec()
            elif isinstance(tool, dict):
                tool_spec = tool
            else:
                # Skip tools that don't have proper specs
                continue
            
            tool_info = {
                "id": i,
                "name": tool_spec['name'],
                "description": tool_spec['description'],
                "type": tool_spec.get('node_type', 'sync'),
                "parameters": tool_spec.get('parameters', {})
            }
            
            action_space["tools"].append(tool_info)
        
        action_space["total_tools"] = len(action_space["tools"])
        return action_space 