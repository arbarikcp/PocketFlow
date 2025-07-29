# PocketFlow Tools

A module for creating tool-enabled nodes in PocketFlow, making it easier to build agent systems with dynamic action spaces.

## Overview

PocketFlow Tools provides a decorator-based approach to mark PocketFlow nodes as tools, automatically extracting their specifications and generating action spaces for agent decision-making.

## Features

- **@tool decorator**: Mark any Node class as a tool with automatic parameter extraction
- **Tool Registry**: Centralized management of all registered tools
- **Action Space Generation**: Automatically generate action space descriptions from tool specifications
- **Generic Parameter Extraction**: Multiple strategies for extracting tool parameters
- **Type Safety**: Parameter type extraction from function signatures
- **Backward Compatible**: Works with existing PocketFlow nodes

## Installation

The module is part of the PocketFlow project. No additional installation required.

## Quick Start

### 1. Mark Nodes as Tools

```python
from pocketflow import Node
from pocketflow_tools import tool

@tool(name="web_search", description="Search the web for information")
class SearchWeb(Node):
    """Search the web for information using DuckDuckGo"""
    
    def prep(self, shared):
        """Get the search query from shared store"""
        return shared.get("search_query", "")
        
    def exec(self, search_query):
        """Search the web for the given query."""
        print(f"🌐 Searching the web for: {search_query}")
        results = search_web_duckduckgo(search_query)
        return results
    
    def post(self, shared, prep_res, exec_res):
        """Save the search results and go back to the decision node."""
        previous = shared.get("context", "")
        shared["context"] = previous + "\n\nSEARCH: " + shared["search_query"] + "\nRESULTS: " + exec_res
        return "decide"

@tool(description="Answer questions based on available context")
class AnswerQuestion(Node):
    """Answer questions based on available context"""
    
    def prep(self, shared):
        """Get the question and context for answering."""
        return shared["question"], shared.get("context", "")
        
    def exec(self, inputs):
        """Call the LLM to generate a final answer."""
        question, context = inputs
        answer = call_llm(f"Question: {question}\nContext: {context}\nAnswer:")
        return answer
    
    def post(self, shared, prep_res, exec_res):
        """Save the final answer and complete the flow."""
        shared["answer"] = exec_res
        return "done"
```

### 2. Create Enhanced Decision Node

```python
from pocketflow_tools import ActionSpaceGenerator

class DecideAction(Node):
    """Enhanced decision node that uses tool specifications"""
    
    def prep(self, shared):
        """Prepare the context and question for the decision-making process."""
        context = shared.get("context", "No previous search")
        question = shared["question"]
        available_tools = shared.get("available_tools", [])
        return question, context, available_tools
        
    def exec(self, inputs):
        """Call the LLM to decide which tool to use."""
        question, context, available_tools = inputs
        
        # Generate action space using ActionSpaceGenerator
        action_space = ActionSpaceGenerator.generate_action_space(available_tools)
        
        # Generate custom prompt based on your specific needs
        prompt = self._generate_custom_prompt(question, context, action_space)
        
        # Call your LLM here
        response = call_llm(prompt)
        
        # Parse the response
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        decision = yaml.safe_load(yaml_str)
        
        return decision
    
    def _generate_custom_prompt(self, question: str, context: str, action_space: str) -> str:
        """Generate a custom prompt based on the action space"""
        # Customize this based on your LLM and use case
        return f"""
### CONTEXT
You are a research assistant with access to the following tools.
Question: {question}
Previous Research: {context}

### ACTION SPACE
{action_space}

## NEXT ACTION
Decide the next action based on the context and available actions.
Return your response in this format:

```yaml
thinking: |
    <your step-by-step reasoning process>
action: <tool_name>
reason: <why you chose this action>
parameters:
    <parameter_name>: <parameter_value>
```
"""
    
    def post(self, shared, prep_res, exec_res):
        """Save the decision and determine the next step in the flow."""
        if exec_res["action"] == "web_search":
            shared["search_query"] = exec_res["parameters"]["query"]
        return exec_res["action"]
```

### 3. Create Flow with Tools

```python
from pocketflow import Flow
from pocketflow_tools import tool_registry

def create_agent_flow():
    """Create and connect the nodes to form a complete agent flow."""
    
    # Create instances of each node
    decide = DecideAction()
    search = SearchWeb()
    answer = AnswerQuestion()
    
    # Get tool specifications for all registered tools
    available_tools = [search, answer]
    
    # Connect the nodes
    decide - "web_search" >> search
    decide - "answer" >> answer
    search - "decide" >> decide
    
    # Create flow
    flow = Flow(start=decide)
    
    # Create shared store with available tools
    shared = {
        "available_tools": available_tools,
        "question": "What is artificial intelligence?",
        "context": "",
        "search_query": "",
        "answer": ""
    }
    
    return flow, shared

# Run the flow
flow, shared = create_agent_flow()
flow.run(shared)
print(f"Final answer: {shared['answer']}")
```

## Parameter Extraction Strategies

The module uses multiple strategies to extract tool parameters, in order of priority:

### 1. Manual Parameter Specification

```python
@tool(
    name="custom_tool",
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
class CustomTool(Node):
    # Implementation here
    pass
```

### 2. Method Signature Extraction

```python
@tool(name="signature_tool", description="Tool with parameters in signature")
class SignatureTool(Node):
    def prep(self, shared, query: str, limit: int = 5):
        """Get parameters from method signature"""
        return shared.get("query", query), limit
    
    # Rest of implementation
```

### 3. Docstring Pattern Extraction

The module can extract parameters from docstrings using multiple patterns:

#### Pattern 1: "Parameters:" section
```python
@tool(name="docstring_tool1", description="Tool with docstring parameters")
class DocstringTool1(Node):
    """
    Tool that processes text data.
    
    Parameters:
    - text: str - Text to process
    - language: str - Language of the text
    """
    # Implementation here
```

#### Pattern 2: "param: type - description" format
```python
@tool(name="docstring_tool2", description="Tool with alternative docstring format")
class DocstringTool2(Node):
    """
    Tool that searches for information.
    
    query: str - Search query to execute
    filters: dict - Search filters to apply
    """
    # Implementation here
```

### 4. Common Keyword Detection

If no explicit parameters are found, the module looks for common parameter keywords in the docstring:

- `query` → Search query
- `question` → Question to process
- `text` → Text to process
- `file` → File path
- `url` → URL to process
- `data` → Data to process
- `input` → Input data
- `prompt` → Prompt text
- `context` → Context information

### 5. Default Generic Parameter

If no parameters are detected, a generic `input` parameter is provided.

## API Reference

### @tool decorator

```python
@tool(name: str = None, description: str = None, parameters: Dict = None)
```

**Parameters:**
- `name`: Optional custom name for the tool (defaults to class name in lowercase)
- `description`: Optional description (defaults to class docstring)
- `parameters`: Optional manual parameter specification (takes highest priority)

### ToolRegistry

```python
from pocketflow_tools import tool_registry

# Get tool specification for a node instance
spec = tool_registry.get_tool_spec(node_instance)

# Get all registered tool specifications
all_specs = tool_registry.get_all_tool_specs()
```

### ActionSpaceGenerator

```python
from pocketflow_tools import ActionSpaceGenerator

# Generate action space description (text format)
action_space = ActionSpaceGenerator.generate_action_space(tools)

# Generate action space as structured dictionary
action_space_dict = ActionSpaceGenerator.generate_action_space_dict(tools)

# Use the action space in your custom prompts
custom_prompt = f"""
Question: {question}
Context: {context}

Available tools:
{action_space}

Choose the best tool and provide parameters:
"""
```

## Tool Specification Format

Each tool specification contains:

```python
{
    'name': 'tool_name',
    'description': 'Tool description',
    'node_type': 'sync|batch|async|async_batch',
    'parameters': {
        'param_name': {
            'type': 'str',
            'required': True,
            'default': None,
            'description': 'Parameter description'
        }
    }
}
```

## Examples

See `example.py` for a complete working example and `test_parameter_extraction.py` for comprehensive parameter extraction tests.

## Future Enhancements

- Enhanced docstring parsing with more sophisticated NLP
- Support for complex parameter types (lists, objects, etc.)
- Tool composition and dependencies
- Validation of tool specifications
- Integration with PocketFlow's async and batch nodes
- Parameter validation and type checking 