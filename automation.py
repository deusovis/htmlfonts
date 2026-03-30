import os
import json
import datetime
from google import genai
import tweepy

# 1. SETUP
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

seo_prompt = """Generate a high-value JSON object for a web typography expert blog. 
Target Keywords: CSS typography, UI design, web fonts, user experience. 
Keys MUST exactly match: "title", "slug", "tweet", "tip", "css_snippet".
Return ONLY raw JSON."""

try:
    # Daily Tip Generation
    response = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=seo_prompt)
    raw_text = response.text.strip()
    if raw_text.startswith("
http://googleusercontent.com/immersive_entry_chip/0

### The Quick Action You Must Take
Because we renamed the archive page, you need to open your main `index.html` and `font-vs-font-comparison-tool.html` and change the navigation link from `/daily-css-typography-tips.html` to **`/editors-desk.html`**. 

Are you ready to commit this to GitHub and let it run, or do you need help updating the navigation links on your static pages?
