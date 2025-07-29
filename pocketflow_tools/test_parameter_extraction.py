"""
Test different parameter extraction strategies in pocketflow_tools
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pocketflow import Node
from pocketflow_tools import tool, tool_registry


def test_manual_parameters():
    """Test manually specified parameters"""
    print("Testing manual parameter specification...")
    
    @tool(
        name="manual_tool",
        description="Tool with manually specified parameters",
        parameters={
            "query": {
                "type": "str",
                "required": True,
                "description": "Search query to execute"
            },
            "max_results": {
                "type": "int",
                "required": False,
                "default": 10,
                "description": "Maximum number of results"
            }
        }
    )
    class ManualTool(Node):
        def prep(self, shared):
            return shared.get("query", "")
        
        def exec(self, query):
            return f"Manual tool executed with: {query}"
        
        def post(self, shared, prep_res, exec_res):
            shared["result"] = exec_res
            return "done"
    
    tool_instance = ManualTool()
    spec = tool_registry.get_tool_spec(tool_instance)
    
    assert spec['parameters']['query']['type'] == 'str'
    assert spec['parameters']['max_results']['type'] == 'int'
    assert spec['parameters']['max_results']['default'] == 10
    
    print("✅ Manual parameter specification works correctly")


def test_signature_parameters():
    """Test parameter extraction from method signature"""
    print("Testing signature parameter extraction...")
    
    @tool(name="signature_tool", description="Tool with parameters in signature")
    class SignatureTool(Node):
        def prep(self, shared, query: str, limit: int = 5):
            """Get parameters from method signature"""
            return shared.get("query", query), limit
        
        def exec(self, inputs):
            query, limit = inputs
            return f"Signature tool executed with: {query}, limit: {limit}"
        
        def post(self, shared, prep_res, exec_res):
            shared["result"] = exec_res
            return "done"
    
    tool_instance = SignatureTool()
    spec = tool_registry.get_tool_spec(tool_instance)
    
    assert spec['parameters']['query']['type'] == 'str'
    assert spec['parameters']['query']['required'] == True
    assert spec['parameters']['limit']['type'] == 'int'
    assert spec['parameters']['limit']['required'] == False
    assert spec['parameters']['limit']['default'] == 5
    
    print("✅ Signature parameter extraction works correctly")


def test_docstring_pattern1():
    """Test parameter extraction from docstring pattern 1"""
    print("Testing docstring pattern 1 extraction...")
    
    @tool(name="docstring_tool1", description="Tool with docstring parameters")
    class DocstringTool1(Node):
        """
        Tool that processes text data.
        
        Parameters:
        - text: str - Text to process
        - language: str - Language of the text
        """
        def prep(self, shared):
            return shared.get("text", "")
        
        def exec(self, text):
            return f"Docstring tool 1 processed: {text}"
        
        def post(self, shared, prep_res, exec_res):
            shared["result"] = exec_res
            return "done"
    
    tool_instance = DocstringTool1()
    spec = tool_registry.get_tool_spec(tool_instance)
    
    assert spec['parameters']['text']['type'] == 'str'
    assert spec['parameters']['language']['type'] == 'str'
    
    print("✅ Docstring pattern 1 extraction works correctly")


def test_docstring_pattern2():
    """Test parameter extraction from docstring pattern 2"""
    print("Testing docstring pattern 2 extraction...")
    
    @tool(name="docstring_tool2", description="Tool with alternative docstring format")
    class DocstringTool2(Node):
        """
        Tool that searches for information.
        
        query: str - Search query to execute
        filters: dict - Search filters to apply
        """
        def prep(self, shared):
            return shared.get("query", "")
        
        def exec(self, query):
            return f"Docstring tool 2 searched for: {query}"
        
        def post(self, shared, prep_res, exec_res):
            shared["result"] = exec_res
            return "done"
    
    tool_instance = DocstringTool2()
    spec = tool_registry.get_tool_spec(tool_instance)
    
    assert spec['parameters']['query']['type'] == 'str'
    assert spec['parameters']['filters']['type'] == 'dict'
    
    print("✅ Docstring pattern 2 extraction works correctly")


def test_common_keyword_detection():
    """Test detection of common parameter keywords"""
    print("Testing common keyword detection...")
    
    @tool(name="keyword_tool", description="Tool that processes files and URLs")
    class KeywordTool(Node):
        """This tool processes files and URLs to extract data"""
        def prep(self, shared):
            return shared.get("file", "")
        
        def exec(self, file):
            return f"Keyword tool processed file: {file}"
        
        def post(self, shared, prep_res, exec_res):
            shared["result"] = exec_res
            return "done"
    
    tool_instance = KeywordTool()
    spec = tool_registry.get_tool_spec(tool_instance)
    
    # Should detect 'file' and 'url' from docstring
    assert 'file' in spec['parameters']
    assert 'url' in spec['parameters']
    
    print("✅ Common keyword detection works correctly")


def test_default_parameters():
    """Test default parameter generation"""
    print("Testing default parameter generation...")
    
    @tool(name="default_tool", description="Tool with no specific parameters")
    class DefaultTool(Node):
        """A simple tool that does basic processing"""
        def prep(self, shared):
            return shared.get("data", "")
        
        def exec(self, data):
            return f"Default tool processed: {data}"
        
        def post(self, shared, prep_res, exec_res):
            shared["result"] = exec_res
            return "done"
    
    tool_instance = DefaultTool()
    spec = tool_registry.get_tool_spec(tool_instance)
    
    # Should have default 'input' parameter
    assert 'input' in spec['parameters']
    assert spec['parameters']['input']['type'] == 'str'
    
    print("✅ Default parameter generation works correctly")


def test_parameter_extraction_priority():
    """Test that parameter extraction follows the correct priority order"""
    print("Testing parameter extraction priority...")
    
    @tool(
        name="priority_tool",
        description="Tool to test extraction priority",
        parameters={
            "manual_param": {
                "type": "str",
                "description": "Manually specified parameter"
            }
        }
    )
    class PriorityTool(Node):
        """
        Tool with multiple parameter sources.
        
        signature_param: str - Parameter from signature
        docstring_param: str - Parameter from docstring
        """
        def prep(self, shared, signature_param: str):
            return shared.get("data", "")
        
        def exec(self, data):
            return f"Priority tool processed: {data}"
        
        def post(self, shared, prep_res, exec_res):
            shared["result"] = exec_res
            return "done"
    
    tool_instance = PriorityTool()
    spec = tool_registry.get_tool_spec(tool_instance)
    
    # Manual parameters should take priority
    assert 'manual_param' in spec['parameters']
    # Signature parameters should not be included (manual takes priority)
    assert 'signature_param' not in spec['parameters']
    # Docstring parameters should not be included (manual takes priority)
    assert 'docstring_param' not in spec['parameters']
    
    print("✅ Parameter extraction priority works correctly")


if __name__ == "__main__":
    print("Running parameter extraction tests...")
    
    test_manual_parameters()
    test_signature_parameters()
    test_docstring_pattern1()
    test_docstring_pattern2()
    test_common_keyword_detection()
    test_default_parameters()
    test_parameter_extraction_priority()
    
    print("\n🎉 All parameter extraction tests passed!") 