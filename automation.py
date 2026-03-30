import os
import json
import datetime
from google import genai
import tweepy
import time

# 1. SETUP & AI GENERATION
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

seo_prompt = """Generate a high-value JSON object for a web typography expert blog. 
Target Keywords: CSS typography, UI design, web fonts, user experience. 
Keys MUST exactly match: "title", "slug", "tweet", "tip", "css_snippet".
Return ONLY raw JSON."""

try:
    response = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=seo_prompt)
    raw_text = response.text.strip()
    if raw_text.startswith("```json"): 
        raw_text = raw_text[7:-3].strip()
    new_data = json.loads(raw_text)
    new_data["date"] = datetime.datetime.now().strftime("%B %d, %Y")

    history = []
    if os.path.exists('history.json'):
        with open('history.json', 'r', encoding='utf-8') as f: 
            history = json.load(f)
    history.insert(0, new_data)
    
    with open('history.json', 'w', encoding='utf-8') as f: json.dump(history, f, indent=4)
    with open('content.json', 'w', encoding='utf-8') as f: json.dump(new_data, f, indent=4)

    os.makedirs('article', exist_ok=True)
    
    # Fixed Sitemap (No markdown links inside strings)
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="[http://www.sitemaps.org/schemas/sitemap/0.9](http://www.sitemaps.org/schemas/sitemap/0.9)">\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/](https://htmlfonts.com/)</loc><priority>1.0</priority></url>\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/font-vs-font-comparison-tool.html](https://htmlfonts.com/font-vs-font-comparison-tool.html)</loc><priority>0.9</priority></url>\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/daily-css-typography-tips.html](https://htmlfonts.com/daily-css-typography-tips.html)</loc><priority>0.9</priority></url>\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/html-css-font-guides.html](https://htmlfonts.com/html-css-font-guides.html)</loc><priority>0.9</priority></url>\n'

    # Generate Permanent Article
    safe_code = new_data['css_snippet'].replace('<', '&lt;').replace('>', '&gt;')
    tip_html = f"""<!DOCTYPE html><html lang="en"><head><title>{new_data['title']}</title><script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script></head><body class="bg-slate-50 p-12"><div class="max-w-2xl mx-auto bg-white p-10 rounded-3xl shadow-xl"><h1 class="text-3xl font-black mb-4">{new_data['title']}</h1><p class="text-slate-600 mb-6">{new_data['tip']}</p><pre class="bg-slate-900 text-indigo-300 p-6 rounded-xl"><code>{safe_code}</code></pre></div></body></html>"""
    
    with open(f"article/{new_data['slug']}.html", 'w', encoding='utf-8') as f: f.write(tip_html)
    sitemap += f"  <url><loc>[https://htmlfonts.com/article/](https://htmlfonts.com/article/){new_data['slug']}.html</loc><priority>0.7</priority></url>\n"
    sitemap += '</urlset>'
    
    with open('sitemap.xml', 'w', encoding='utf-8') as f: f.write(sitemap)
    print(f"✅ Build Successful: article/{new_data['slug']}.html")

except Exception as e:
    print(f"❌ Generation Error: {e}")
    exit(1)

# 4. POST TO X (Twitter) - THE BULLETPROOF VERSION
try:
    # Initialize the client with EXACTLY 4 keys. 
    # Do NOT pass bearer_token here; it can force the client into Read-only mode.
    client_x = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
    )

    # Fixed tweet text (Removed markdown link formatting)
    tweet_text = f"{new_data['tweet']}\n\nRead Tip: [https://htmlfonts.com/article/](https://htmlfonts.com/article/){new_data['slug']}.html #webdesign #typography"
    
    # Explicitly use user_auth=True to ensure it uses the Access Tokens, not an App-only Bearer token.
    client_x.create_tweet(text=tweet_text)
    
    print("✅ X Post Successful.")
except Exception as e:
    print(f"❌ X Post Failed: {e}")
