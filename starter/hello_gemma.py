"""First call to Gemma 4 through the Gemini API.

Before you run it:
  1. pip install -r requirements.txt
  2. Put your free key from aistudio.google.com/apikey in a file called .env:
     GEMINI_API_KEY=paste-your-key-here
  3. Make sure .env is listed in .gitignore, so the key never goes on GitHub.

Run it with: python hello_gemma.py
"""

from dotenv import load_dotenv
from google import genai

load_dotenv()                      # reads GEMINI_API_KEY from .env
client = genai.Client()            # picks the key up from the environment

response = client.models.generate_content(
    model="gemma-4-26b-a4b-it",    # Google's suggested starting model; gemma-4-31b-it is the bigger one
    contents="In two sentences: what does a hackathon team need to know about aged care in South Australia?",
)
print(response.text)
