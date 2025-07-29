from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables when module is imported
# Look for .env file in the project root directory
project_root = Path(__file__).parent.parent.parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path=dotenv_path)

def call_llm(messages):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    print(f"Looking for .env file at: {dotenv_path}")
    print(f"OPENAI_API_KEY loaded: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}")
    
    # Test the LLM call
    messages = [{"role": "user", "content": "In a few words, what's the meaning of life?"}]
    response = call_llm(messages)
    print(f"Prompt: {messages[0]['content']}")
    print(f"Response: {response}")

