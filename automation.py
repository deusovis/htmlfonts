import os
import json
import datetime
from google import genai
import tweepy

# 1. Setup Gemini
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

seo_prompt = """Generate a JSON object for htmlfonts.com. Target Keywords: Free Web Fonts, CSS typography. Keys MUST exactly match: "title", "slug", "tweet", "tip", "css_snippet"."""

try:
    response = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=seo_prompt)
    raw_text = response.text.strip()
    if raw_text.startswith("
http://googleusercontent.com/immersive_entry_chip/0

Push these two files, and your programmatic machine will instantly build over a dozen standalone Web Apps for the highest-performing queries in your niche, linking them all back to your master directory.
