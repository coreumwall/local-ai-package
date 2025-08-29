import os
import json
from anthropic import Anthropic

# Initialize Claude client
client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

def analyze_with_claude(prompt):
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # or claude-opus-4-1-20250805
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text

# Example: Analyze code changes
if __name__ == "__main__":
    # You can access GitHub context through environment variables
    event_name = os.environ.get('GITHUB_EVENT_NAME', '')
    
    # Example use cases:
    # - Review pull requests
    # - Generate documentation
    # - Analyze code quality
    # - Answer questions in issues
    
    # Your custom logic here
    result = analyze_with_claude("Analyze this repository and suggest improvements")
    print(result)
