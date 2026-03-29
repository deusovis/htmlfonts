import os
import json
import datetime
from google import genai
import tweepy

# 1. Setup Gemini
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. Generate SEO Content with Title and Slug
seo_prompt = """
Generate a JSON object for htmlfonts.com. 
Target Keywords: Web Typography, CSS, UI Design. 
Keys MUST exactly match: 
"title" (A catchy, SEO-optimized title for an article),
"slug" (A lowercase, hyphen-separated url slug based on the title),
"tweet" (max 240 chars for social), 
"tip" (2 paragraphs of advanced CSS/typography advice), 
"css_snippet" (clean CSS code block). 
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
    
    # --- PROGRAMMATIC SEO: Generate the standalone HTML page ---
    os.makedirs('tips', exist_ok=True) # Ensure the folder exists
    file_path = f"tips/{new_data['slug']}.html"
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{new_data['title']} | htmlfonts.com Editor's Desk</title>
    <meta name="description" content="{new_data['tip'][:150]}...">
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
    <link href="[https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap)" rel="stylesheet">
    <style>body {{ font-family: 'Inter', sans-serif; }} .no-scrollbar::-webkit-scrollbar {{ display: none; }}</style>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen p-6 md:p-12">
    <div class="max-w-3xl mx-auto">
        <a href="/" class="text-indigo-600 font-bold text-xs uppercase tracking-widest hover:underline mb-8 inline-block">&larr; Back to Directory</a>
        <article class="bg-white p-8 md:p-12 rounded-3xl shadow-xl border border-slate-200">
            <h1 class="text-4xl md:text-5xl font-black mb-6 tracking-tight italic">{new_data['title']}</h1>
            <div class="flex items-center space-x-4 mb-10 border-b border-slate-100 pb-6">
                <span class="bg-slate-900 text-white text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded">Editor's Desk</span>
                <span class="text-slate-400 text-xs font-bold uppercase tracking-widest">{new_data['date']}</span>
            </div>
            <p class="text-lg text-slate-700 leading-relaxed mb-10">{new_data['tip']}</p>
            <div class="bg-slate-950 rounded-2xl p-6 relative">
                <pre class="font-mono text-sm text-indigo-300 overflow-x-auto no-scrollbar"><code>{new_data['css_snippet']}</code></pre>
            </div>
        </article>
    </div>
</body>
</html>"""

    # Save the new standalone HTML page
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # --- Update Archives ---
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
        
    print(f"✅ Success! Generated new page: /{file_path}")

except Exception as e:
    print(f"❌ Automation Error: {e}")
    exit(1)

# 3. Post to X
try:
    client_x = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
    )
    # Include the direct link to the new page in the tweet
    tweet_text = f"{new_data['tweet']}\n\nRead more: [https://htmlfonts.com/tips/](https://htmlfonts.com/tips/){new_data['slug']}.html"
    client_x.create_tweet(text=tweet_text)
    print("✅ X.com post successful.")
except Exception as e:
    print(f"⚠️ X.com Error: {e} (Website update preserved)")
