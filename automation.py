import os
import json
import datetime
from google import genai
import tweepy

# 1. Setup Gemini SDK
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

seo_prompt = """Generate a JSON object for htmlfonts.com. 
Target Keywords: Free Web Fonts, CSS typography, UI design. 
Keys MUST exactly match: "title", "slug", "tweet", "tip", "css_snippet".
Return ONLY raw JSON."""

try:
    # Fetch Daily Tip from AI
    response = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=seo_prompt)
    raw_text = response.text.strip()
    if raw_text.startswith("```json"): 
        raw_text = raw_text[7:-3].strip()
    new_data = json.loads(raw_text)
    new_data["date"] = datetime.datetime.now().strftime("%B %d, %Y")

    # Read and Update Archive History
    history = []
    if os.path.exists('history.json'):
        with open('history.json', 'r', encoding='utf-8') as f: 
            history = json.load(f)
    history.insert(0, new_data)
    
    with open('history.json', 'w', encoding='utf-8') as f: 
        json.dump(history, f, indent=4)
    with open('content.json', 'w', encoding='utf-8') as f: 
        json.dump(new_data, f, indent=4)

    # Setup Directory Structure
    os.makedirs('compare', exist_ok=True)
    
    # Initialize XML Sitemap
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="[http://www.sitemaps.org/schemas/sitemap/0.9](http://www.sitemaps.org/schemas/sitemap/0.9)">\n'
    sitemap += '  <url>\n    <loc>[https://htmlfonts.com/](https://htmlfonts.com/)</loc>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n'

    # 2. GENERATE THE TOP 30 FONT VS FONT COMPARISON PAGES
    print("Generating Top 30 Font VS Font Pages...")
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
        ("Rubik", "Karla", "'Rubik', sans-serif", "'Karla', sans-serif", "Rubik:wght@400;700", "Karla:wght@400;700"),
        ("Roboto", "Open Sans", "'Roboto', sans-serif", "'Open Sans', sans-serif", "Roboto:wght@400;700", "Open+Sans:wght@400;700"),
        ("Montserrat", "Poppins", "'Montserrat', sans-serif", "'Poppins', sans-serif", "Montserrat:wght@400;700", "Poppins:wght@400;700"),
        ("Lato", "Roboto", "'Lato', sans-serif", "'Roboto', sans-serif", "Lato:wght@400;700", "Roboto:wght@400;700"),
        ("Work Sans", "Fira Sans", "'Work Sans', sans-serif", "'Fira Sans', sans-serif", "Work+Sans:wght@400;700", "Fira+Sans:wght@400;700"),
        ("Barlow", "Rubik", "'Barlow', sans-serif", "'Rubik', sans-serif", "Barlow:wght@400;700", "Rubik:wght@400;700"),
        ("Space Grotesk", "Lexend", "'Space Grotesk', sans-serif", "'Lexend', sans-serif", "Space+Grotesk:wght@400;700", "Lexend:wght@400;700"),
        ("Public Sans", "DM Sans", "'Public Sans', sans-serif", "'DM Sans', sans-serif", "Public+Sans:wght@400;700", "DM+Sans:wght@400;700"),
        ("Crimson Text", "Cormorant", "'Crimson Text', serif", "'Cormorant', serif", "Crimson+Text:wght@400;700", "Cormorant:wght@400;700"),
        ("Bitter", "Noto Serif", "'Bitter', serif", "'Noto Serif', serif", "Bitter:wght@400;700", "Noto+Serif:wght@400;700"),
        ("Source Code Pro", "Inconsolata", "'Source Code Pro', monospace", "'Inconsolata', monospace", "Source+Code+Pro:wght@400;700", "Inconsolata:wght@400;700"),
        ("Anton", "Oswald", "'Anton', sans-serif", "'Oswald', sans-serif", "Anton", "Oswald:wght@400;700"),
        ("Pacifico", "Dancing Script", "'Pacifico', cursive", "'Dancing Script', cursive", "Pacifico", "Dancing+Script:wght@400;700"),
        ("Caveat", "Pacifico", "'Caveat', cursive", "'Pacifico', cursive", "Caveat:wght@400;700", "Pacifico"),
        ("Comfortaa", "Quicksand", "'Comfortaa', display", "'Quicksand', sans-serif", "Comfortaa:wght@400;700", "Quicksand:wght@400;700"),
        ("Righteous", "Anton", "'Righteous', display", "'Anton', sans-serif", "Righteous", "Anton"),
        ("IBM Plex Mono", "Space Mono", "'IBM Plex Mono', monospace", "'Space Mono', monospace", "IBM+Plex+Mono:wght@400;600", "Space+Mono:wght@400;700"),
        ("Crimson Pro", "Zilla Slab", "'Crimson Pro', serif", "'Zilla Slab', serif", "Crimson+Pro:wght@400;600", "Zilla+Slab:wght@400;600"),
        ("Teko", "Bebas Neue", "'Teko', sans-serif", "'Bebas Neue', sans-serif", "Teko:wght@400;600", "Bebas+Neue")
    ]
    
    for font_a, font_b, css_a, css_b, link_a, link_b in top_comparisons:
        slug = f"{font_a.lower().replace(' ', '-')}-vs-{font_b.lower().replace(' ', '-')}"
        
        # Determine correct HTML or System Comment
        html_import_a = f"<link href='[https://fonts.googleapis.com/css2?family=](https://fonts.googleapis.com/css2?family=){link_a}&display=swap' rel='stylesheet'>" if link_a else ""
        html_import_b = f"<link href='[https://fonts.googleapis.com/css2?family=](https://fonts.googleapis.com/css2?family=){link_b}&display=swap' rel='stylesheet'>" if link_b else ""

        safe_html_a = html_import_a.replace('<', '&lt;').replace('>', '&gt;')
        safe_html_b = html_import_b.replace('<', '&lt;').replace('>', '&gt;')

        vs_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{font_a} vs {font_b} | Free Web Fonts Comparison</title>
    <meta name="description" content="Compare {font_a} vs {font_b} side-by-side. Copy the HTML and CSS snippets instantly for your web design project.">
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
    {html_import_a}
    {html_import_b}
    <style>
        body {{ font-family: system-ui, sans-serif; }}
        .toast-enter {{ opacity: 0; transform: translate(-50%, 20px); }}
        .toast-active {{ opacity: 1; transform: translate(-50%, 0); transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
    </style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col">
    <div id="toast" class="fixed bottom-10 left-1/2 transform -translate-x-1/2 hidden bg-slate-900 text-white px-8 py-4 rounded-2xl shadow-2xl z-[100] text-sm font-black tracking-widest uppercase toast-enter border border-slate-700 flex items-center gap-3">
        <svg class="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
        <span>Code copied! 🚀</span>
    </div>

    <header class="bg-white border-b border-slate-200 py-4 px-6 text-center shadow-sm">
        <a href="/" class="text-indigo-600 font-black tracking-tighter text-2xl">html<span class="text-slate-900">fonts</span></a>
    </header>
    
    <div class="max-w-6xl mx-auto px-4 py-16 w-full flex-grow">
        <div class="text-center mb-12">
            <a href="/#vs-tool" class="text-indigo-600 font-bold text-xs uppercase tracking-widest hover:underline">&larr; Back to Font VS Font Tool</a>
            <h1 class="text-5xl md:text-6xl font-black mt-6 tracking-tight text-slate-900">{font_a} vs {font_b}</h1>
            <p class="text-xl text-slate-500 mt-4 font-medium">Live typography comparison test.</p>
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
                    
                    <div class="mt-8 relative group">
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2">1. Add to HTML Head</label>
                        <div class="bg-slate-900 p-4 rounded-xl"><code id="code-html-a" class="text-xs font-mono text-indigo-300">{safe_html_a}</code></div>
                        <button onclick="copyData('code-html-a')" class="absolute bottom-3 right-3 text-[10px] font-bold text-white bg-indigo-600 px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition shadow-md">COPY</button>
                    </div>
                    
                    <div class="mt-4 relative group">
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2">2. Apply CSS Rule</label>
                        <div class="bg-slate-900 p-4 rounded-xl"><code id="code-css-a" class="text-xs font-mono text-indigo-300">font-family: {css_a};</code></div>
                        <button onclick="copyData('code-css-a')" class="absolute bottom-3 right-3 text-[10px] font-bold text-white bg-indigo-600 px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition shadow-md">COPY</button>
                    </div>
                </div>

                <div class="md:pl-10 pt-6 md:pt-0">
                    <h3 class="text-2xl font-black text-slate-800 mb-6">{font_b}</h3>
                    <p id="preview-b" class="text-5xl text-slate-900 break-words leading-tight" style="font-family: {css_b};">Optimize your UI design with fast-loading free web fonts.</p>
                    
                    <div class="mt-8 relative group">
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2">1. Add to HTML Head</label>
                        <div class="bg-slate-900 p-4 rounded-xl"><code id="code-html-b" class="text-xs font-mono text-indigo-300">{safe_html_b}</code></div>
                        <button onclick="copyData('code-html-b')" class="absolute bottom-3 right-3 text-[10px] font-bold text-white bg-indigo-600 px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition shadow-md">COPY</button>
                    </div>
                    
                    <div class="mt-4 relative group">
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2">2. Apply CSS Rule</label>
                        <div class="bg-slate-900 p-4 rounded-xl"><code id="code-css-b" class="text-xs font-mono text-indigo-300">font-family: {css_b};</code></div>
                        <button onclick="copyData('code-css-b')" class="absolute bottom-3 right-3 text-[10px] font-bold text-white bg-indigo-600 px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition shadow-md">COPY</button>
                    </div>
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
        
        // Bulletproof copy logic for generated pages
        function fallbackCopy(text) {{
            var textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            document.body.appendChild(textArea);
            textArea.focus(); textArea.select();
            try {{ document.execCommand('copy'); }} catch (err) {{ }}
            document.body.removeChild(textArea);
        }}
        
        function copyData(id) {{
            const text = document.getElementById(id).textContent;
            if (!navigator.clipboard) {{ fallbackCopy(text); }} 
            else {{ navigator.clipboard.writeText(text).catch(() => fallbackCopy(text)); }}
            
            const toast = document.getElementById('toast');
            toast.classList.remove('hidden');
            setTimeout(() => toast.classList.add('toast-active'), 10);
            setTimeout(() => {{ 
                toast.classList.remove('toast-active'); 
                setTimeout(() => toast.classList.add('hidden'), 300);
            }}, 3000);
        }}
    </script>
</body>
</html>"""
        
        with open(f"compare/{slug}.html", 'w', encoding='utf-8') as f:
            f.write(vs_html)
        
        sitemap += f"  <url>\n    <loc>[https://htmlfonts.com/compare/](https://htmlfonts.com/compare/){slug}.html</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.9</priority>\n  </url>\n"

    # Save daily tip page so old links keep working
    with open(f"compare/{new_data['slug']}.html", 'w', encoding='utf-8') as f:
        f.write(f"<!DOCTYPE html><html><head><title>{new_data['title']} | htmlfonts.com</title><script src='[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)'></script></head><body class='bg-slate-50 p-10'><a href='/' class='text-indigo-600 font-bold'>&larr; Back Home</a><h1 class='text-4xl font-black mt-8'>{new_data['title']}</h1><p class='mt-4 text-xl'>{new_data['tip']}</p></body></html>")
    
    # Add History Article Archives to Sitemap
    for item in history:
        if 'slug' in item: 
            sitemap += f"  <url>\n    <loc>[https://htmlfonts.com/compare/](https://htmlfonts.com/compare/){item['slug']}.html</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"
    
    sitemap += '</urlset>'
    with open('sitemap.xml', 'w', encoding='utf-8') as f: 
        f.write(sitemap)
    
    print("✅ System update complete: JSON, Comparison Pages, and Sitemap successfully generated.")

except Exception as e:
    print(f"❌ Error during generation: {e}")
    exit(1)

# 3. Post to X.com
try:
    client_x = tweepy.Client(consumer_key=os.environ["X_API_KEY"], consumer_secret=os.environ["X_API_SECRET"], access_token=os.environ["X_ACCESS_TOKEN"], access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"])
    client_x.create_tweet(text=f"{new_data['tweet']}\n\nRead more: [https://htmlfonts.com/compare/](https://htmlfonts.com/compare/){new_data['slug']}.html")
except Exception as e: pass
