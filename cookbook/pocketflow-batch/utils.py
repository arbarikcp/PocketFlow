from anthropic import Anthropic
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables when module is imported
# Look for .env file in the project root directory
project_root = Path(__file__).parent.parent.parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path=dotenv_path)


def call_llm(prompt):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    messages=[
            {"role": "user", "content": prompt}
        ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content


def call_anthropic_llm(prompt):
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "your-api-key"))
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=20000,
        thinking={
            "type": "enabled",
            "budget_tokens": 16000
        },
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[1].text


if __name__ == "__main__":
    print("## Testing call_llm")
    prompt = "In a few words, what is the meaning of life?"
    print(f"## Prompt: {prompt}")
    response = call_llm(prompt)
    print(f"## Response: {response}")
