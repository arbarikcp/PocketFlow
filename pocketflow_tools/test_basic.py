"""
Basic test for pocketflow_tools functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pocketflow import Node
from pocketflow_tools import tool, tool_registry, ActionSpaceGenerator


@tool(name="test_tool", description="A test tool for demonstration")
class TestTool(Node):
    """A test tool that demonstrates the tool functionality"""
    
    def prep(self, shared):
        return shared.get("test_input", "")
        
    def exec(self, test_input):
        return f"Processed: {test_input}"
    
    def post(self, shared, prep_res, exec_res):
        shared["test_output"] = exec_res
        return "done"


def test_tool_registration():
    """Test that tools are properly registered"""
    print("Testing tool registration...")
    
    # Create an instance
    test_tool = TestTool()
    
    # Check if it's registered as a tool
    assert hasattr(test_tool, '_is_tool')
    assert test_tool._is_tool == True
    assert test_tool._tool_name == "test_tool"
    
    print("✅ Tool registration works correctly")


def test_tool_spec_extraction():
    """Test that tool specifications are extracted correctly"""
    print("Testing tool spec extraction...")
    
    test_tool = TestTool()
    spec = tool_registry.get_tool_spec(test_tool)
    
    assert spec['name'] == "test_tool"
    assert spec['description'] == "A test tool for demonstration"
    assert spec['node_type'] == "sync"
    assert 'parameters' in spec
    
    print("✅ Tool spec extraction works correctly")


def test_action_space_generation():
    """Test that action space is generated correctly"""
    print("Testing action space generation...")
    
    test_tool = TestTool()
    action_space = ActionSpaceGenerator.generate_action_space([test_tool])
    
    print(f"Generated action space: {action_space}")
    
    assert "test_tool" in action_space
    assert "A test tool for demonstration" in action_space
    assert "Parameters:" in action_space
    
    print("✅ Action space generation works correctly")


def test_action_space_dict_generation():
    """Test that action space dictionary is generated correctly"""
    print("Testing action space dictionary generation...")
    
    test_tool = TestTool()
    action_space_dict = ActionSpaceGenerator.generate_action_space_dict([test_tool])
    
    assert "tools" in action_space_dict
    assert "total_tools" in action_space_dict
    assert action_space_dict["total_tools"] == 1
    assert len(action_space_dict["tools"]) == 1
    assert action_space_dict["tools"][0]["name"] == "test_tool"
    
    print("✅ Action space dictionary generation works correctly")


if __name__ == "__main__":
    print("Running basic tests for pocketflow_tools...")
    
    test_tool_registration()
    test_tool_spec_extraction()
    test_action_space_generation()
    test_action_space_dict_generation()
    
    print("\n🎉 All tests passed!") 