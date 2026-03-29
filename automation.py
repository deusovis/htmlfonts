import os
import json
import datetime
from google import genai
import tweepy

# 1. Setup Gemini (Modern 2026 SDK)
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. Generate SEO-Focused Content
seo_prompt = """
Generate a JSON object for htmlfonts.com. 
Keywords: Fluid Typography, CSS clamp, Variable Fonts. 
Keys: "tweet", "tip", "css_snippet". 
Return ONLY raw JSON.
"""

try:
    response = client_gemini.models.generate_content(
        model='gemini-1.5-flash',
        contents=seo_prompt
    )
    raw_text = response.text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:-3].strip()
    
    content_data = json.loads(raw_text)
    content_data["date"] = datetime.datetime.now().strftime("%B %d, %Y")
    
    with open('content.json', 'w') as f:
        json.dump(content_data, f, indent=4)
    print("✅ Website content updated.")

except Exception as e:
    print(f"❌ Gemini/JSON Error: {e}")
    exit(1)

# 3. Post to X (Graceful Failure)
try:
    client_x = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
    )
    client_x.create_tweet(text=content_data["tweet"])
    print("✅ X.com post successful.")
except Exception as e:
    print(f"⚠️ X.com Error: {e}")
    print("Website was still updated, but the tweet failed (likely 402 Payment Required).")
