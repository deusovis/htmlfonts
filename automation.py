import os
import json
import datetime
import google.generativeai as genai
import tweepy

# 1. Setup Gemini API (1.5 Flash - Bulletproof Free Tier)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. SEO-Tuned Prompt
# We are forcing Gemini to use 2026 SEO keywords that developers actually search for.
seo_prompt = """
You are a Senior SEO Expert and Lead Frontend Developer. 
Generate a high-utility 'Daily Font Insight' for the website htmlfonts.com.

TARGET KEYWORDS: Fluid Typography, CSS clamp(), Variable Fonts performance, 
System UI font stacks, Font-display swap, A11y typography, modern web-safe fonts.

OUTPUT FORMAT: You must return ONLY a raw JSON object with these exact keys:
{
  "tweet": "A viral-style tweet (max 240 chars) with 3 relevant hashtags.",
  "tip": "A 2-paragraph expert explanation of a modern CSS typography technique.",
  "css_snippet": "A clean, copy-pasteable CSS code block using modern 2026 standards.",
  "seo_keywords": "5 comma-separated keywords for meta tags"
}

GUIDELINES:
- Focus on performance (Core Web Vitals).
- No old HTML tags (like <font>); use only modern CSS.
- Ensure the CSS snippet is useful for a professional project.
"""

response = model.generate_content(seo_prompt)

# Clean and parse JSON response
try:
    # Handle potential markdown formatting in AI response
    raw_text = response.text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:-3].strip()
    
    content_data = json.loads(raw_text)
    content_data["date"] = datetime.datetime.now().strftime("%B %d, %Y")
except Exception as e:
    print(f"Error parsing Gemini response: {e}")
    # Fallback content to prevent site breakage
    content_data = {
        "tweet": "Optimize your web performance with system font stacks! #WebDev #CSS #Performance",
        "tip": "System font stacks are the ultimate choice for performance-first web design in 2026.",
        "css_snippet": "body { font-family: system-ui, -apple-system, sans-serif; }",
        "date": datetime.datetime.now().strftime("%B %d, %Y")
    }

# 3. Update Website JSON File
with open('content.json', 'w') as f:
    json.dump(content_data, f, indent=4)

# 4. Post to X (Twitter)
try:
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
    )
    client.create_tweet(text=content_data["tweet"])
    print("SEO Tweet deployed.")
except Exception as e:
    print(f"X.com API Error: {e}")
