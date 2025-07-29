"""
Demonstration of the new generic parameter extraction system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pocketflow import Node, Flow
from pocketflow_tools import tool, tool_registry, ActionSpaceGenerator
import yaml


# Example 1: Manual parameter specification (highest priority)
@tool(
    name="web_search",
    description="Search the web for information using DuckDuckGo",
    parameters={
        "query": {
            "type": "str",
            "required": True,
            "description": "Search query to execute"
        },
        "max_results": {
            "type": "int",
            "required": False,
            "default": 5,
            "description": "Maximum number of search results"
        }
    }
)
class SearchWeb(Node):
    """Search the web for information using DuckDuckGo"""
    
    def prep(self, shared):
        """Get the search query from shared store"""
        return shared.get("search_query", "")
        
    def exec(self, search_query):
        """Search the web for the given query."""
        print(f"🌐 Searching the web for: {search_query}")
        # In a real implementation, you would call your search utility here
        results = f"Search results for: {search_query}"
        return results
    
    def post(self, shared, prep_res, exec_res):
        """Save the search results and go back to the decision node."""
        previous = shared.get("context", "")
        shared["context"] = previous + "\n\nSEARCH: " + shared["search_query"] + "\nRESULTS: " + exec_res
        print(f"📚 Found information, analyzing results...")
        return "decide"


# Example 2: Method signature extraction
@tool(name="text_processor", description="Process and analyze text content")
class TextProcessor(Node):
    def prep(self, shared, text: str, language: str = "en", max_length: int = 1000):
        """Get text and processing parameters from method signature"""
        return shared.get("text", text), language, max_length
        
    def exec(self, inputs):
        """Process the text with given parameters."""
        text, language, max_length = inputs
        print(f"📝 Processing text in {language}, max length: {max_length}")
        # In a real implementation, you would process the text here
        processed = f"Processed text: {text[:max_length]}..."
        return processed
    
    def post(self, shared, prep_res, exec_res):
        """Save the processed text."""
        shared["processed_text"] = exec_res
        return "done"


# Example 3: Docstring pattern extraction
@tool(name="file_analyzer", description="Analyze files and extract information")
class FileAnalyzer(Node):
    """
    Tool that analyzes files and extracts structured information.
    
    Parameters:
    - file_path: str - Path to the file to analyze
    - extract_type: str - Type of information to extract (text, metadata, etc.)
    - include_headers: bool - Whether to include file headers
    """
    def prep(self, shared):
        """Get file path from shared store"""
        return shared.get("file_path", "")
        
    def exec(self, file_path):
        """Analyze the file and extract information."""
        print(f"📄 Analyzing file: {file_path}")
        # In a real implementation, you would analyze the file here
        analysis = f"Analysis results for: {file_path}"
        return analysis
    
    def post(self, shared, prep_res, exec_res):
        """Save the analysis results."""
        shared["file_analysis"] = exec_res
        return "done"


# Example 4: Common keyword detection
@tool(name="data_processor", description="Process various types of data")
class DataProcessor(Node):
    """This tool processes data, files, and URLs to extract insights"""
    def prep(self, shared):
        """Get data from shared store"""
        return shared.get("data", "")
        
    def exec(self, data):
        """Process the data and extract insights."""
        print(f"🔍 Processing data and extracting insights")
        # In a real implementation, you would process the data here
        insights = f"Insights extracted from data: {data[:50]}..."
        return insights
    
    def post(self, shared, prep_res, exec_res):
        """Save the insights."""
        shared["insights"] = exec_res
        return "done"


# Example 5: Default generic parameter
@tool(name="simple_tool", description="A simple tool with no specific parameters")
class SimpleTool(Node):
    """A simple tool that does basic processing"""
    def prep(self, shared):
        """Get input from shared store"""
        return shared.get("input", "")
        
    def exec(self, input_data):
        """Process the input data."""
        print(f"⚙️ Simple tool processing input")
        # In a real implementation, you would process the input here
        result = f"Simple processing result: {input_data}"
        return result
    
    def post(self, shared, prep_res, exec_res):
        """Save the result."""
        shared["simple_result"] = exec_res
        return "done"


def demonstrate_parameter_extraction():
    """Demonstrate the different parameter extraction strategies"""
    print("=== Parameter Extraction Demonstration ===\n")
    
    # Create instances of all tools
    tools = [
        SearchWeb(),
        TextProcessor(),
        FileAnalyzer(),
        DataProcessor(),
        SimpleTool()
    ]
    
    # Show tool specifications
    for i, tool_instance in enumerate(tools, 1):
        spec = tool_registry.get_tool_spec(tool_instance)
        print(f"{i}. {spec['name']} - {spec['description']}")
        print(f"   Parameters:")
        for param_name, param_spec in spec['parameters'].items():
            required = "required" if param_spec.get('required', True) else "optional"
            default = f" (default: {param_spec.get('default')})" if param_spec.get('default') is not None else ""
            print(f"     - {param_name}: {param_spec['type']}, {required}{default}")
            print(f"       Description: {param_spec.get('description', 'No description')}")
        print()
    
    # Generate and show action space
    print("=== Generated Action Space ===")
    action_space = ActionSpaceGenerator.generate_action_space(tools)
    print(action_space)
    
    # Generate action space as dictionary
    print("\n=== Generated Action Space (Dictionary Format) ===")
    action_space_dict = ActionSpaceGenerator.generate_action_space_dict(tools)
    print(f"Total tools: {action_space_dict['total_tools']}")
    for tool_info in action_space_dict['tools']:
        print(f"  - {tool_info['name']}: {tool_info['description']}")
        print(f"    Parameters: {list(tool_info['parameters'].keys())}")
    
    # Show how to create custom prompts
    print("\n=== Custom Prompt Generation Example ===")
    question = "What is machine learning?"
    context = "No previous research available"
    
    # Example 1: Simple prompt format
    simple_prompt = f"""
Question: {question}
Context: {context}

Available tools:
{action_space}

Choose the best tool and provide parameters:
"""
    print("Simple prompt format:")
    print(simple_prompt[:200] + "..." if len(simple_prompt) > 200 else simple_prompt)
    
    # Example 2: Structured prompt format
    structured_prompt = f"""
### TASK
Answer the following question: {question}

### CONTEXT
Previous research: {context}

### AVAILABLE TOOLS
{action_space}

### INSTRUCTIONS
Select the most appropriate tool and provide the required parameters.
"""
    print("\nStructured prompt format:")
    print(structured_prompt[:200] + "..." if len(structured_prompt) > 200 else structured_prompt)


def demonstrate_priority_order():
    """Demonstrate parameter extraction priority order"""
    print("\n=== Parameter Extraction Priority Demonstration ===")
    
    # Create a tool with multiple parameter sources
    @tool(
        name="priority_demo",
        description="Tool to demonstrate parameter extraction priority",
        parameters={
            "manual_param": {
                "type": "str",
                "required": True,
                "description": "Manually specified parameter (highest priority)"
            }
        }
    )
    class PriorityDemoTool(Node):
        """
        Tool with multiple parameter sources.
        
        signature_param: str - Parameter from method signature (medium priority)
        docstring_param: str - Parameter from docstring (low priority)
        """
        def prep(self, shared, signature_param: str):
            """Method signature parameter (medium priority)"""
            return shared.get("data", "")
        
        def exec(self, data):
            return f"Priority demo tool processed: {data}"
        
        def post(self, shared, prep_res, exec_res):
            shared["result"] = exec_res
            return "done"
    
    tool_instance = PriorityDemoTool()
    spec = tool_registry.get_tool_spec(tool_instance)
    
    print("Parameter extraction priority demonstration:")
    print("1. Manual parameters (highest priority):")
    for param_name, param_spec in spec['parameters'].items():
        print(f"   - {param_name}: {param_spec['description']}")
    
    print("\nNote: Signature and docstring parameters are ignored when manual parameters are provided.")


if __name__ == "__main__":
    demonstrate_parameter_extraction()
    demonstrate_priority_order()
    
    print("\n🎉 Generic parameter extraction demonstration completed!") 