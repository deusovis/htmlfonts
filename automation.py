import os
import json
import datetime
from google import genai
import tweepy

client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

seo_prompt = """Generate a JSON object for htmlfonts.com. 
Target Keywords: Free Web Fonts, CSS typography, UI design. 
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

    os.makedirs('compare', exist_ok=True)
    
    top_comparisons = [
        ("Arial", "Helvetica", "Arial, sans-serif", "Helvetica, Arial, sans-serif", "", ""), 
        ("Inter", "Roboto", "'Inter', sans-serif", "'Roboto', sans-serif", "Inter:wght@400;700", "Roboto:wght@400;700"), 
        ("Open Sans", "Lato", "'Open Sans', sans-serif", "'Lato', sans-serif", "Open+Sans:wght@400;700", "Lato:wght@400;700"), 
        ("Montserrat", "Raleway", "'Montserrat', sans-serif", "'Raleway', sans-serif", "Montserrat:wght@400;700", "Raleway:wght@400;700"), 
        ("Playfair Display", "Merriweather", "'Playfair Display', serif", "'Merriweather', serif", "Playfair+Display:wght@400;700", "Merriweather:wght@400;700"), 
        ("Fira Code", "JetBrains Mono", "'Fira Code', monospace", "'JetBrains Mono', monospace", "Fira+Code:wght@400;700", "JetBrains+Mono:wght@400;700"),
        ("Oswald", "Bebas Neue", "'Oswald', sans-serif", "'Bebas Neue', sans-serif", "Oswald:wght@400;700", "Bebas+Neue"), 
        ("Ubuntu", "Quicksand", "'Ubuntu', sans-serif", "'Quicksand', sans-serif", "Ubuntu:wght@400;700", "Quicksand:wght@400;700"), 
        ("Lora", "PT Serif", "'Lora', serif", "'PT Serif', serif", "Lora:wght@400;700", "PT+Serif:wght@400;700"), 
        ("Nunito", "Poppins", "'Nunito', sans-serif", "'Poppins', sans-serif", "Nunito:wght@400;700", "Poppins:wght@400;700"),
        ("Outfit", "Lexend", "'Outfit', sans-serif", "'Lexend', sans-serif", "Outfit:wght@400;700", "Lexend:wght@400;700"),
        ("Rubik", "Karla", "'Rubik', sans-serif", "'Karla', sans-serif", "Rubik:wght@400;700", "Karla:wght@400;700")
    ]
    
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="[http://www.sitemaps.org/schemas/sitemap/0.9](http://www.sitemaps.org/schemas/sitemap/0.9)">\n'
    sitemap += '  <url>\n    <loc>[https://htmlfonts.com/](https://htmlfonts.com/)</loc>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n'
    
    for font_a, font_b, css_a, css_b, link_a, link_b in top_comparisons:
        slug = f"{font_a.lower().replace(' ', '-')}-vs-{font_b.lower().replace(' ', '-')}"
        html_import_a = f"<link href='[https://fonts.googleapis.com/css2?family=](https://fonts.googleapis.com/css2?family=){link_a}&display=swap' rel='stylesheet'>" if link_a else ""
        html_import_b = f"<link href='[https://fonts.googleapis.com/css2?family=](https://fonts.googleapis.com/css2?family=){link_b}&display=swap' rel='stylesheet'>" if link_b else ""

        vs_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{font_a} vs {font_b} | Free Web Fonts Comparison</title>
    <meta name="description" content="Compare {font_a} vs {font_b} side-by-side. Copy the HTML and CSS snippets instantly for your web design project.">
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
    {html_import_a}
    {html_import_b}
    <style>body {{ font-family: system-ui, sans-serif; }}</style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col">
    <header class="bg-white border-b border-slate-200 py-4 px-6 text-center shadow-sm">
        <a href="/" class="text-indigo-600 font-black tracking-tighter text-2xl">html<span class="text-slate-900">fonts</span></a>
    </header>
    <div class="max-w-6xl mx-auto px-4 py-16 w-full flex-grow">
        <div class="text-center mb-12">
            <a href="/#vs-tool" class="text-indigo-600 font-bold text-xs uppercase tracking-widest hover:underline">&larr; Back to Font VS Font Tool</a>
            <h1 class="text-5xl md:text-6xl font-black mt-6 tracking-tight text-slate-900">{font_a} vs {font_b}</h1>
            <p class="text-xl text-slate-500 mt-4">Live typography comparison test.</p>
        </div>
        <div class="bg-white rounded-3xl p-8 md:p-12 shadow-2xl border border-slate-200">
            <input type="text" id="vs-text" value="Optimize your UI design with fast-loading free web fonts." 
                onfocus="if(this.value===this.defaultValue) this.value='';" 
                onblur="if(this.value==='') this.value=this.defaultValue;"
                oninput="updateText()"
                class="w-full mb-10 px-6 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none text-xl text-center font-medium shadow-inner">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-10 divide-y md:divide-y-0 md:divide-x divide-slate-100">
                <div class="md:pr-10 pt-6 md:pt-0">
                    <h3 class="text-2xl font-black text-slate-800 mb-6">{font_a}</h3>
                    <p id="preview-a" class="text-5xl text-slate-900 break-words leading-tight" style="font-family: {css_a};">Optimize your UI design with fast-loading free web fonts.</p>
                    <div class="mt-8 bg-slate-900 p-4 rounded-xl"><code class="text-xs font-mono text-indigo-300">{html_import_a.replace('<', '&lt;').replace('>', '&gt;')}</code></div>
                    <div class="mt-2 bg-slate-900 p-4 rounded-xl"><code class="text-xs font-mono text-indigo-300">font-family: {css_a};</code></div>
                </div>
                <div class="md:pl-10 pt-6 md:pt-0">
                    <h3 class="text-2xl font-black text-slate-800 mb-6">{font_b}</h3>
                    <p id="preview-b" class="text-5xl text-slate-900 break-words leading-tight" style="font-family: {css_b};">Optimize your UI design with fast-loading free web fonts.</p>
                    <div class="mt-8 bg-slate-900 p-4 rounded-xl"><code class="text-xs font-mono text-indigo-300">{html_import_b.replace('<', '&lt;').replace('>', '&gt;')}</code></div>
                    <div class="mt-2 bg-slate-900 p-4 rounded-xl"><code class="text-xs font-mono text-indigo-300">font-family: {css_b};</code></div>
                </div>
            </div>
        </div>
    </div>
    <script>
        function updateText() {{
            const val = document.getElementById('vs-text').value || document.getElementById('vs-text').defaultValue;
            document.getElementById('preview-a').innerText = val;
            document.getElementById('preview-b').innerText = val;
        }}
    </script>
</body>
</html>"""
        with open(f"compare/{slug}.html", 'w', encoding='utf-8') as f:
            f.write(vs_html)
        sitemap += f"  <url>\n    <loc>[https://htmlfonts.com/compare/](https://htmlfonts.com/compare/){slug}.html</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.9</priority>\n  </url>\n"

    # Tip standalone generation 
    tip_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{new_data['title']} | htmlfonts.com</title>
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen flex flex-col items-center py-12 px-6">
    <div class="max-w-3xl w-full">
        <a href="/#editor-desk" class="text-indigo-600 font-bold text-xs uppercase tracking-widest hover:underline mb-8 inline-block">&larr; Back to Directory</a>
        <article class="bg-white p-8 md:p-12 rounded-3xl shadow-xl border border-slate-200">
            <h1 class="text-4xl md:text-5xl font-black mb-6">{new_data['title']}</h1>
            <p class="text-lg text-slate-700 leading-relaxed mb-10">{new_data['tip']}</p>
            <div class="bg-slate-950 rounded-2xl p-6 relative">
                <pre class="font-mono text-sm text-indigo-300 overflow-x-auto"><code>{new_data['css_snippet']}</code></pre>
            </div>
        </article>
    </div>
</body>
</html>"""
    
    with open(f"compare/{new_data['slug']}.html", 'w', encoding='utf-8') as f: f.write(tip_html)

    for item in history:
        if 'slug' in item: sitemap += f"  <url>\n    <loc>[https://htmlfonts.com/compare/](https://htmlfonts.com/compare/){item['slug']}.html</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"
    
    sitemap += '</urlset>'
    with open('sitemap.xml', 'w', encoding='utf-8') as f: f.write(sitemap)
    print("✅ System update complete.")

except Exception as e:
    print(f"❌ Error during generation: {e}")
    exit(1)

try:
    client_x = tweepy.Client(consumer_key=os.environ["X_API_KEY"], consumer_secret=os.environ["X_API_SECRET"], access_token=os.environ["X_ACCESS_TOKEN"], access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"])
    client_x.create_tweet(text=f"{new_data['tweet']}\n\nRead more: [https://htmlfonts.com/compare/](https://htmlfonts.com/compare/){new_data['slug']}.html")
except Exception as e: print(f"⚠️ X.com Error: {e}")
