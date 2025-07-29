"""
Example usage of pocketflow_tools module
"""

from pocketflow import Node, Flow
from pocketflow_tools import tool, tool_registry, ActionSpaceGenerator
import yaml


@tool(name="web_search", description="Search the web for information using DuckDuckGo")
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


@tool(description="Answer questions based on available context")
class AnswerQuestion(Node):
    """Answer questions based on available context"""
    
    def prep(self, shared):
        """Get the question and context for answering."""
        return shared["question"], shared.get("context", "")
        
    def exec(self, inputs):
        """Call the LLM to generate a final answer."""
        question, context = inputs
        print(f"✍️ Crafting final answer...")
        # In a real implementation, you would call your LLM here
        answer = f"Answer to '{question}' based on context: {context[:50]}..."
        return answer
    
    def post(self, shared, prep_res, exec_res):
        """Save the final answer and complete the flow."""
        shared["answer"] = exec_res
        print(f"✅ Answer generated successfully")
        return "done"


class DecideAction(Node):
    """Enhanced decision node that uses tool specifications"""
    
    def prep(self, shared):
        """Prepare the context and question for the decision-making process."""
        context = shared.get("context", "No previous search")
        question = shared["question"]
        
        # Get available tools from shared store
        available_tools = shared.get("available_tools", [])
        
        return question, context, available_tools
        
    def exec(self, inputs):
        """Call the LLM to decide which tool to use."""
        question, context, available_tools = inputs
        
        print(f"🤔 Agent deciding what to do next...")
        
        # Generate action space using ActionSpaceGenerator
        action_space = ActionSpaceGenerator.generate_action_space(available_tools)
        
        # Generate custom prompt based on the action space
        prompt = self._generate_custom_prompt(question, context, action_space)
        
        # In a real implementation, you would call your LLM here
        # For this example, we'll simulate a decision
        if "search" in context.lower():
            decision = {
                "thinking": "Previous search found information, now I can answer",
                "action": "answer",
                "reason": "Enough information gathered",
                "parameters": {}
            }
        else:
            decision = {
                "thinking": "Need to search for more information",
                "action": "web_search",
                "reason": "No previous research available",
                "parameters": {"query": question}
            }
        
        return decision
    
    def _generate_custom_prompt(self, question: str, context: str, action_space: str) -> str:
        """Generate a custom prompt based on the action space"""
        # This is where the caller can customize the prompt format
        # based on their specific LLM and use case
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

IMPORTANT: Make sure to:
1. Use proper indentation (4 spaces) for all multi-line fields
2. Use the | character for multi-line text fields
3. Keep single-line fields without the | character
4. Only include parameters that are required for the chosen action
"""
    
    def post(self, shared, prep_res, exec_res):
        """Save the decision and determine the next step in the flow."""
        if exec_res["action"] == "web_search":
            shared["search_query"] = exec_res["parameters"]["query"]
            print(f"🔍 Agent decided to search for: {exec_res['parameters']['query']}")
        else:
            print(f"💡 Agent decided to answer the question")
        
        return exec_res["action"]


def create_enhanced_agent_flow():
    """Create and connect the nodes to form a complete agent flow using pocketflow_tools."""
    
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


def demo_tool_registry():
    """Demonstrate the tool registry functionality"""
    print("=== Tool Registry Demo ===")
    
    # Create instances to see their specs
    search = SearchWeb()
    answer = AnswerQuestion()
    
    print("\n1. Individual tool specifications:")
    print("SearchWeb spec:", tool_registry.get_tool_spec(search))
    print("AnswerQuestion spec:", tool_registry.get_tool_spec(answer))
    
    print("\n2. All registered tool specifications:")
    all_specs = tool_registry.get_all_tool_specs()
    for spec in all_specs:
        print(f"- {spec['name']}: {spec['description']}")
    
    print("\n3. Generated action space:")
    action_space = ActionSpaceGenerator.generate_action_space([search, answer])
    print(action_space)
    
    print("\n4. Generated action space as dictionary:")
    action_space_dict = ActionSpaceGenerator.generate_action_space_dict([search, answer])
    print(f"Total tools: {action_space_dict['total_tools']}")
    for tool_info in action_space_dict['tools']:
        print(f"  - {tool_info['name']}: {tool_info['description']}")


if __name__ == "__main__":
    # Demo the tool registry
    demo_tool_registry()
    
    print("\n" + "="*50)
    print("Running enhanced agent flow...")
    
    # Create and run the flow
    flow, shared = create_enhanced_agent_flow()
    flow.run(shared)
    
    print(f"\nFinal answer: {shared['answer']}") 