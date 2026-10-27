"""First call to Gemma 4 through the Gemini API.

Before you run it:
  1. pip install -r requirements.txt
  2. Put your free key from aistudio.google.com/apikey into sample.env, then rename
     that file to .env.
  3. Make sure .env is listed in .gitignore, so the key never goes on GitHub.

Run it with: python hello_gemma.py
"""

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()                      # reads GEMINI_API_KEY from .env
client = genai.Client()            # picks the key up from the environment

response = client.models.generate_content(
    model="gemma-4-26b-a4b-it",    # Google's suggested starting model; gemma-4-31b-it is the bigger one
    contents="In two sentences: what does a hackathon team need to know about aged care in South Australia?",
    # Gemma 4 thinks first by default (20 to 60 s); "minimal" answers in seconds
    config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_level="minimal")),
)
print(response.text)
