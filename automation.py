import os
import json
import datetime
from google import genai
import tweepy

# 1. Setup Gemini (2026 Stable SDK)
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. Generate SEO Content
seo_prompt = """
Generate a JSON object for htmlfonts.com. 
Keywords: Web Typography, CSS design, UI performance. 
Return ONLY raw JSON with these keys: 
"title" (SEO title), 
"slug" (url-safe-string), 
"tweet" (short social post), 
"tip" (2 paragraphs of expert advice), 
"css_snippet" (clean CSS).
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
    
    # --- Generate Individual Tip Page ---
    os.makedirs('tips', exist_ok=True)
    file_path = f"tips/{new_data['slug']}.html"
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{new_data['title']} | htmlfonts.com</title>
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
    <link href="[https://fonts.googleapis.com/css2?family=Inter:wght@400;800&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;800&display=swap)" rel="stylesheet">
    <style>body {{ font-family: 'Inter', sans-serif; }}</style>
</head>
<body class="bg-slate-50 text-slate-900 p-6 md:p-20">
    <div class="max-w-3xl mx-auto">
        <a href="/" class="text-indigo-600 font-bold text-xs uppercase tracking-widest hover:underline mb-12 inline-block">&larr; Back to Directory</a>
        <article class="bg-white p-8 md:p-16 rounded-[40px] shadow-2xl border border-slate-100">
            <h1 class="text-4xl md:text-6xl font-black mb-8 tracking-tighter italic">{new_data['title']}</h1>
            <p class="text-slate-400 text-xs font-bold uppercase tracking-[0.3em] mb-12">{new_data['date']}</p>
            <p class="text-xl text-slate-600 leading-relaxed mb-12">{new_data['tip']}</p>
            <div class="bg-slate-950 rounded-3xl p-8"><pre class="text-indigo-300 font-mono text-sm overflow-x-auto"><code>{new_data['css_snippet']}</code></pre></div>
        </article>
    </div>
</body>
</html>"""

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    # --- Update Archives & History ---
    history_file = 'history.json'
    history = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            try: history = json.load(f)
            except: history = []
    
    history.insert(0, new_data)
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=4)
    with open('content.json', 'w') as f:
        json.dump(new_data, f, indent=4)

    # --- Generate XML Sitemap ---
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="[http://www.sitemaps.org/schemas/sitemap/0.9](http://www.sitemaps.org/schemas/sitemap/0.9)">\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/](https://htmlfonts.com/)</loc><priority>1.0</priority></url>\n'
    for item in history:
        if 'slug' in item:
            sitemap += f"  <url><loc>[https://htmlfonts.com/tips/](https://htmlfonts.com/tips/){item['slug']}.html</loc><priority>0.8</priority></url>\n"
    sitemap += '</urlset>'
    with open('sitemap.xml', 'w') as f:
        f.write(sitemap)

    print(f"✅ Created: {file_path}")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# 3. Post to X
try:
    client_x = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"], consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"], access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
    )
    client_x.create_tweet(text=f"{new_data['tweet']}\n\nRead more: [https://htmlfonts.com/tips/](https://htmlfonts.com/tips/){new_data['slug']}.html")
    print("✅ Tweeted.")
except Exception as e:
    print(f"⚠️ X Error: {e}")
