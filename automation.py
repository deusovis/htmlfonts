import os
import json
import datetime
from google import genai
import tweepy

# 1. Setup Gemini API (Using the new 2026 'google-genai' SDK)
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. Generate Content
# We use 'gemini-1.5-flash' which remains the most reliable free-tier model.
seo_prompt = """
You are a Senior SEO Expert for htmlfonts.com. 
Generate a JSON object for a daily web typography tip. 
Keys: "tweet" (max 240 chars), "tip" (2 paragraphs), "css_snippet" (modern CSS). 
Focus on 'Fluid Typography' and 'Variable Fonts'. 
Return ONLY raw JSON.
"""

try:
    # New SDK method: client.models.generate_content
    response = client_gemini.models.generate_content(
        model='gemini-1.5-flash',
        contents=seo_prompt
    )
    
    # Extract text from the new response object structure
    raw_text = response.text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:-3].strip()
    
    content_data = json.loads(raw_text)
    content_data["date"] = datetime.datetime.now().strftime("%B %d, %Y")
    
    # Save for the website
    with open('content.json', 'w') as f:
        json.dump(content_data, f, indent=4)
    print("Content generated and saved successfully.")

except Exception as e:
    print(f"Gemini/Parsing Error: {e}")
    exit(1)

# 3. Post to X
try:
    client_x = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
    )
    client_x.create_tweet(text=content_data["tweet"])
    print("Tweet posted successfully.")
except Exception as e:
    print(f"X.com API Error: {e}")
