from dotenv import load_dotenv # Import load_dotenv
import os # Import os to access environment variables
from langfuse.decorators import observe
from langfuse.openai import openai # OpenAI integration

load_dotenv() # Load environment variables from .env file

@observe()
def story():
    return openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
          {"role": "system", "content": "You are a great storyteller."},
          {"role": "user", "content": "Once upon a time in a galaxy far, far away..."}
        ],
    ).choices[0].message.content

@observe()
def main():
    return story()

main()