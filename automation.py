import os
import json
import datetime
from google import genai
import tweepy

# 1. Setup Gemini (2026 Stable SDK)
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. Generate SEO Content
# Switching to gemini-2.5-flash (The 2026 GA model)
seo_prompt = """
Generate a JSON object for htmlfonts.com. 
Keywords: Fluid Typography, Variable Fonts, 2026 Web Standards. 
Keys: "tweet", "tip", "css_snippet". 
Return ONLY raw JSON.
"""

try:
    response = client_gemini.models.generate_content(
        model='gemini-2.5-flash', 
        contents=seo_prompt
    )
    raw_text = response.text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:-3].strip()
    
    new_data = json.loads(raw_text)
    new_data["date"] = datetime.datetime.now().strftime("%B %d, %Y")
    
    # --- ARCHIVE LOGIC (SEO BOOSTER) ---
    # Load old history or start new list
    history_file = 'history.json'
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    else:
        history = []
    
    # Add new tip to history (keep last 30 days)
    history.insert(0, new_data)
    history = history[:30] 
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=4)
        
    # Update current content.json for the homepage
    with open('content.json', 'w') as f:
        json.dump(new_data, f, indent=4)
        
    print("✅ Website & History updated.")

except Exception as e:
    print(f"❌ Gemini Error: {e}")
    exit(1)

# 3. Post to X
try:
    client_x = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
    )
    client_x.create_tweet(text=new_data["tweet"])
    print("✅ X.com post successful.")
except Exception as e:
    print(f"⚠️ X.com Social Link failed: {e} (Website still updated!)")
