import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables when module is imported
# Look for .env file in the project root directory
project_root = Path(__file__).parent.parent.parent.parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path=dotenv_path)

def call_llm(prompt):    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

if __name__ == "__main__":
    print(call_llm("Tell me a short joke")) 
