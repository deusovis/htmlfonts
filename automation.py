import os
import json
import datetime
import google.generativeai as genai
import tweepy

# 1. Setup Gemini API (Using 1.5 Flash for reliable, fast, free-tier text generation)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Generate Content
prompt = """
You are an expert web developer and typographer. 
Provide a unique, modern web typography tip or font pairing for frontend developers.
Respond ONLY in valid JSON format with three keys: 
"tweet" (A short, engaging tweet about the tip, max 250 chars, including #CSS #WebDesign), 
"tip" (A 2-3 sentence explanation of the font pairing or typography trick), 
"css_snippet" (The actual CSS code block to implement it).
"""

response = model.generate_content(prompt)

# Clean and parse JSON response
try:
    response_text = response.text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:-3]
    content_data = json.loads(response_text)
except Exception as e:
    print(f"Error parsing Gemini response: {e}")
    exit(1)

content_data["date"] = datetime.datetime.now().strftime("%Y-%m-%d")

# 3. Update Website JSON
with open('content.json', 'w') as f:
    json.dump(content_data, f, indent=4)
print("Website content.json updated successfully.")

# 4. Post to X.com
try:
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
    )
    client.create_tweet(text=content_data["tweet"])
    print("Tweet posted successfully.")
except Exception as e:
    print(f"Error posting to X: {e}")
    # We don't exit(1) here so the GitHub action still commits the website update even if X fails.
