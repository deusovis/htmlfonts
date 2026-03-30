import os
import json
import datetime
from google import genai
import tweepy

# 1. SETUP & AI GENERATION
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# High-quality prompt for the "Editor's Desk"
seo_prompt = """Generate a high-value JSON object for a web typography expert blog. 
Target Keywords: CSS typography, UI design, web fonts, user experience. 
The "tip" should be an incredible, punchy 2-sentence piece of advice.
The "css_snippet" must be clean and useful.
The "tweet" must be engaging with emojis and under 200 characters.
Keys MUST exactly match: "title", "slug", "tweet", "tip", "css_snippet".
Return ONLY raw JSON."""

try:
    # Fetch Daily Content from Gemini
    response = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=seo_prompt)
    raw_text = response.text.strip()
    if raw_text.startswith("```json"): 
        raw_text = raw_text[7:-3].strip()
    new_data = json.loads(raw_text)
    new_data["date"] = datetime.datetime.now().strftime("%B %d, %Y")

    # Update the "Live" data and the History Archive
    history = []
    if os.path.exists('history.json'):
        with open('history.json', 'r', encoding='utf-8') as f: 
            history = json.load(f)
    history.insert(0, new_data)
    
    with open('history.json', 'w', encoding='utf-8') as f: json.dump(history, f, indent=4)
    with open('content.json', 'w', encoding='utf-8') as f: json.dump(new_data, f, indent=4)

    # Setup Folders
    os.makedirs('compare', exist_ok=True)
    os.makedirs('article', exist_ok=True)
    
    # Start Sitemap
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="[http://www.sitemaps.org/schemas/sitemap/0.9](http://www.sitemaps.org/schemas/sitemap/0.9)">\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/](https://htmlfonts.com/)</loc><priority>1.0</priority></url>\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/font-vs-font-comparison-tool.html](https://htmlfonts.com/font-vs-font-comparison-tool.html)</loc><priority>0.9</priority></url>\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/daily-css-typography-tips.html](https://htmlfonts.com/daily-css-typography-tips.html)</loc><priority>0.9</priority></url>\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/html-css-font-guides.html](https://htmlfonts.com/html-css-font-guides.html)</loc><priority>0.9</priority></url>\n'

    # 2. GENERATE THE PERMANENT ARTICLE FOR TODAY'S TIP
    safe_code = new_data['css_snippet'].replace('<', '&lt;').replace('>', '&gt;')
    tip_html = f"""<!DOCTYPE html><html lang="en"><head><title>{new_data['title']} | Editor's Desk</title><meta name="description" content="{new_data['tip']}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script></head><body class="bg-slate-50 min-h-screen flex flex-col font-sans selection:bg-indigo-200"><header class="bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 h-16 flex items-center px-6"><div class="max-w-7xl mx-auto w-full flex justify-between items-center"><a href="/" class="font-black text-2xl"><span class="text-indigo-600">html</span>fonts</a><nav class="hidden md:flex space-x-8 text-xs font-bold uppercase tracking-widest text-slate-500"><a href="/">Directory</a><a href="/font-vs-font-comparison-tool.html">Font VS Font</a><a href="/daily-css-typography-tips.html" class="text-indigo-600">Editor's Desk</a></nav></div></header><main class="flex-grow py-16 px-6"><div class="max-w-3xl mx-auto"><a href="/daily-css-typography-tips.html" class="text-indigo-600 font-bold uppercase tracking-widest text-xs">&larr; Back to Archive</a><article class="bg-white p-10 mt-8 rounded-3xl shadow-lg border border-slate-200"><span class="text-indigo-600 text-xs font-black uppercase tracking-widest">{new_data['date']}</span><h1 class="text-4xl font-black mt-2 mb-4 tracking-tight text-slate-900">{new_data['title']}</h1><p class="text-xl text-slate-600 mb-8 font-medium leading-relaxed">{new_data['tip']}</p><div class="bg-slate-900 p-8 rounded-2xl overflow-x-auto border border-slate-800"><pre class="text-indigo-300 font-mono text-sm"><code>{safe_code}</code></pre></div></article></div></main><footer class="bg-white border-t py-12 text-center text-xs font-bold text-slate-500 uppercase tracking-widest"><p>&copy; {datetime.datetime.now().year} htmlfonts</p></footer></body></html>"""
    
    with open(f"article/{new_data['slug']}.html", 'w', encoding='utf-8') as f: f.write(tip_html)
    sitemap += f"  <url><loc>[https://htmlfonts.com/article/](https://htmlfonts.com/article/){new_data['slug']}.html</loc><priority>0.7</priority></url>\n"

    # 3. (Optional) RE-GENERATE ALL OTHER GUIDES/COMPARISONS HERE IF NEEDED...
    # [Insert the Guide/Comparison loops from previous version if you want them rebuilt daily]

    # Finalize Sitemap
    sitemap += '</urlset>'
    with open('sitemap.xml', 'w', encoding='utf-8') as f: f.write(sitemap)
    print(f"✅ Build Successful: Created article/{new_data['slug']}.html")

except Exception as e:
    print(f"❌ Generation Error: {e}")
    exit(1)

# 4. POST TO X (Twitter)
try:
    client_x = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"], 
        consumer_secret=os.environ["X_API_SECRET"], 
        access_token=os.environ["X_ACCESS_TOKEN"], 
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
    )
    # Post the unique tweet generated by Gemini with a link to the new article
    tweet_text = f"{new_data['tweet']}\n\nRead Tip: [https://htmlfonts.com/article/](https://htmlfonts.com/article/){new_data['slug']}.html #webdesign #typography"
    client_x.create_tweet(text=tweet_text)
    print("✅ X Post Successful.")
except Exception as e:
    print(f"❌ X Post Failed: {e}")
