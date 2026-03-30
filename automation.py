import os
import json
import datetime
from google import genai
import tweepy

# 1. SETUP & AI GENERATION
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

seo_prompt = """Generate a JSON object for htmlfonts.com. 
Target Keywords: Free Web Fonts, CSS typography, UI design. 
Keys MUST exactly match: "title", "slug", "tweet", "tip", "css_snippet".
Return ONLY raw JSON."""

try:
    # Fetch Daily Tip from Gemini 3 Flash
    response = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=seo_prompt)
    raw_text = response.text.strip()
    if raw_text.startswith("```json"): 
        raw_text = raw_text[7:-3].strip()
    new_data = json.loads(raw_text)
    new_data["date"] = datetime.datetime.now().strftime("%B %d, %Y")

    # Update Archives
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
    
    # Start Sitemap (Adding new URLs)
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="[http://www.sitemaps.org/schemas/sitemap/0.9](http://www.sitemaps.org/schemas/sitemap/0.9)">\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/](https://htmlfonts.com/)</loc><priority>1.0</priority></url>\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/font-vs-font-comparison-tool.html](https://htmlfonts.com/font-vs-font-comparison-tool.html)</loc><priority>0.9</priority></url>\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/daily-css-typography-tips.html](https://htmlfonts.com/daily-css-typography-tips.html)</loc><priority>0.9</priority></url>\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/html-css-font-guides.html](https://htmlfonts.com/html-css-font-guides.html)</loc><priority>0.9</priority></url>\n'

    # 2. DATA ARRAYS: THE SEO ENGINE
    # TOP 30 HOW-TO ARTICLES
    top_guides = [
        ("how-to-change-font-size-in-html", "How to Change Font Size in HTML", "Learn to use the CSS font-size property with px, rem, and em units.", "font-size: 16px;"),
        ("how-to-add-google-fonts-to-html", "How to Add Google Fonts to HTML", "Step-by-step guide to embedding external fonts via the <link> tag.", "<link href='...' rel='stylesheet'>"),
        ("how-to-change-font-color-in-html", "How to Change Font Color in HTML", "Use CSS hex codes and RGB values to style your web typography.", "color: #4f46e5;"),
        ("how-to-bold-text-in-html", "How to Bold Text in HTML", "Master the font-weight property for stronger visual hierarchy.", "font-weight: 800;"),
        ("how-to-center-text-in-html", "How to Center Text in HTML", "The best ways to align text using CSS text-align and flexbox.", "text-align: center;"),
        ("what-is-the-best-font-for-reading", "The Best Fonts for On-Screen Reading", "Why high x-height fonts like Inter and Roboto lead the industry.", "font-family: 'Inter', sans-serif;"),
        ("how-to-use-custom-fonts-in-css", "How to Use Custom Fonts in CSS", "Tutorial on @font-face for self-hosting your own font files.", "@font-face { font-family: 'MyFont'; src: url('...'); }"),
        ("how-to-add-text-shadow-in-css", "How to Add Text Shadow in CSS", "Create depth with the text-shadow property and rgba colors.", "text-shadow: 2px 2px 5px rgba(0,0,0,0.1);"),
        ("how-to-import-local-fonts", "How to Import Local Fonts in HTML", "Using system-ui and locally installed typefaces for speed.", "font-family: system-ui, sans-serif;"),
        ("how-to-underline-text-in-css", "How to Underline Text in CSS", "Beyond the <u> tag: modern text-decoration styling.", "text-decoration: underline;"),
        ("how-to-make-fluid-typography", "Creating Fluid Typography in CSS", "Using clamp() to make fonts responsive across all devices.", "font-size: clamp(1rem, 5vw, 2rem);"),
        ("rem-vs-em-css-guide", "REM vs EM: Which CSS Unit is Best?", "A comparison of relative units for modern web accessibility.", "font-size: 1.25rem;"),
        ("how-to-change-line-height-in-css", "Improving Readability with Line Height", "How to adjust vertical spacing between lines of text.", "line-height: 1.6;"),
        ("how-to-style-drop-caps-in-html", "How to Style Drop Caps in HTML", "Using the ::first-letter pseudo-element for editorial design.", "p::first-letter { font-size: 3em; }"),
        ("how-to-add-letter-spacing-in-css", "How to Adjust Letter Spacing (Tracking)", "Fine-tuning the horizontal space between characters.", "letter-spacing: 0.05em;"),
        ("how-to-use-variable-fonts-in-html", "How to Use Variable Fonts in HTML", "Control multiple font weights with a single file import.", "font-variation-settings: 'wght' 600;"),
        ("how-to-prevent-text-wrapping-css", "Preventing Text Wrapping in CSS", "Using white-space properties to keep text on one line.", "white-space: nowrap;"),
        ("how-to-create-gradient-text-css", "How to Create Gradient Text in CSS", "Modern techniques using background-clip and transparent text.", "background-clip: text; color: transparent;"),
        ("best-fonts-for-mobile-apps", "The Best Fonts for Mobile App UI", "Choosing legible typefaces for small screen environments.", "font-family: 'Outfit', sans-serif;"),
        ("how-to-load-fonts-asynchronously", "How to Load Fonts Asynchronously", "Speed up your site using font-display: swap and preloading.", "font-display: swap;"),
        ("how-to-use-monospace-fonts-for-coding", "Best Monospace Fonts for Developers", "Top picks for code editors and technical documentation.", "font-family: 'Fira Code', monospace;"),
        ("how-to-italicize-text-in-css", "How to Italicize Text in CSS", "The difference between font-style: italic and oblique.", "font-style: italic;"),
        ("how-to-change-font-weight-numerically", "Font Weight 100 to 900 Explained", "A guide to numerical font weights for CSS developers.", "font-weight: 900;"),
        ("how-to-capitalize-first-letter-css", "Capitalizing First Letters with CSS", "Automating text transformations without changing HTML.", "text-transform: capitalize;"),
        ("how-to-add-columns-to-text", "Creating Newspaper Columns in CSS", "Using column-count for multi-column text layouts.", "column-count: 3;"),
        ("how-to-fix-blurry-fonts-on-browser", "How to Fix Blurry Fonts in Chrome", "Optimizing font rendering for high-DPI displays.", "-webkit-font-smoothing: antialiased;"),
        ("how-to-import-adobe-fonts", "How to Import Adobe Typekit Fonts", "Integrating Creative Cloud fonts into your web project.", "<script src='[https://use.typekit.net/](https://use.typekit.net/)...'></script>"),
        ("what-is-x-height-typography", "Understanding X-Height in Typography", "How vertical proportions affect font legibility on web.", "/* Concept Guide */"),
        ("best-serif-fonts-for-minimalist-web", "Best Serif Fonts for Minimalism", "Top serif choices for modern, clean web interfaces.", "font-family: 'Lora', serif;"),
        ("how-to-add-font-fallback-stacks", "Creating Bulletproof Font Stacks", "How to ensure your site looks good even if fonts fail.", "font-family: 'Inter', Arial, sans-serif;")
    ]

    # TOP 30 FONT-VS-FONT COMPARISONS
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

    # 3. GENERATION LOOPS
    # Loop 1: Articles
    for slug, title, desc, code in top_guides:
        safe_code = code.replace('<', '&lt;').replace('>', '&gt;')
        # Notice the back link points directly to /html-css-font-guides.html
        html = f"""<!DOCTYPE html><html lang="en"><head><title>{title} | htmlfonts Guides</title><meta name="description" content="{desc}"><script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script><style>body {{ font-family: system-ui, sans-serif; }}</style></head><body class="bg-slate-50 py-16 px-6"><div class="max-w-3xl mx-auto"><a href="/html-css-font-guides.html" class="text-indigo-600 font-bold uppercase tracking-widest text-xs">&larr; Back to Guides</a><article class="bg-white p-10 mt-8 rounded-3xl shadow-lg border border-slate-200"><h1 class="text-4xl font-black mb-4 tracking-tight">{title}</h1><p class="text-xl text-slate-600 mb-8">{desc}</p><div class="bg-slate-900 p-6 rounded-xl overflow-x-auto"><code class="text-indigo-300 font-mono text-sm whitespace-pre">{safe_code}</code></div></article></div></body></html>"""
        with open(f"article/{slug}.html", 'w', encoding='utf-8') as f: f.write(html)
        sitemap += f"  <url><loc>[https://htmlfonts.com/article/](https://htmlfonts.com/article/){slug}.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>\n"

    # Loop 2: Comparisons
    for font_a, font_b, css_a, css_b, link_a, link_b in top_comparisons:
        slug = f"{font_a.lower().replace(' ', '-')}-vs-{font_b.lower().replace(' ', '-')}"
        imp_a = f"<link href='[https://fonts.googleapis.com/css2?family=](https://fonts.googleapis.com/css2?family=){link_a}&display=swap' rel='stylesheet'>" if link_a else ""
        imp_b = f"<link href='[https://fonts.googleapis.com/css2?family=](https://fonts.googleapis.com/css2?family=){link_b}&display=swap' rel='stylesheet'>" if link_b else ""
        safe_a = imp_a.replace('<', '&lt;').replace('>', '&gt;')
        safe_b = imp_b.replace('<', '&lt;').replace('>', '&gt;')
        
        # Notice the back link points directly to /font-vs-font-comparison-tool.html
        vs_html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{font_a} vs {font_b} | Comparison</title><script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>{imp_a}{imp_b}<style>body {{ font-family: system-ui, sans-serif; }} .toast-active {{ opacity: 1; transform: translate(-50%, 0); transition: all 0.3s; }}</style></head><body class="bg-slate-50 min-h-screen flex flex-col"><div id="toast" class="fixed bottom-10 left-1/2 transform -translate-x-1/2 hidden bg-slate-900 text-white px-8 py-4 rounded-2xl shadow-2xl z-[100] text-sm font-black uppercase">Copied! 🚀</div><header class="bg-white border-b py-4 px-6 text-center"><a href="/" class="text-indigo-600 font-black text-2xl">htmlfonts</a></header><div class="max-w-6xl mx-auto px-4 py-16 w-full"><div class="text-center mb-12"><a href="/font-vs-font-comparison-tool.html" class="text-indigo-600 font-bold text-xs uppercase">&larr; Back to Tool</a><h1 class="text-5xl font-black mt-6 tracking-tight text-slate-900">{font_a} vs {font_b}</h1></div><div class="bg-white rounded-3xl p-12 shadow-2xl border"><input type="text" id="vs-text" value="Optimize your UI design with fast-loading fonts." oninput="u()" class="w-full mb-10 px-6 py-4 bg-slate-50 border rounded-xl text-xl text-center"><div class="grid grid-cols-1 md:grid-cols-2 gap-10 divide-x divide-slate-100"><div><h3 class="text-2xl font-black mb-6">{font_a}</h3><p id="pa" class="text-5xl leading-tight" style="font-family: {css_a};">Optimize your UI design with fast-loading fonts.</p><div class="mt-8 bg-slate-900 p-4 rounded-xl relative group"><code id="ha" class="text-xs text-indigo-300 font-mono">{safe_a}</code><button onclick="c('ha')" class="absolute top-2 right-2 bg-indigo-600 text-white px-2 py-1 rounded text-[10px] opacity-0 group-hover:opacity-100">COPY</button></div><div class="mt-4 bg-slate-900 p-4 rounded-xl relative group"><code id="ca" class="text-xs text-indigo-300 font-mono">font-family: {css_a};</code><button onclick="c('ca')" class="absolute top-2 right-2 bg-indigo-600 text-white px-2 py-1 rounded text-[10px] opacity-0 group-hover:opacity-100">COPY</button></div></div><div><h3 class="text-2xl font-black mb-6">{font_b}</h3><p id="pb" class="text-5xl leading-tight" style="font-family: {css_b};">Optimize your UI design with fast-loading fonts.</p><div class="mt-8 bg-slate-900 p-4 rounded-xl relative group"><code id="hb" class="text-xs text-indigo-300 font-mono">{safe_b}</code><button onclick="c('hb')" class="absolute top-2 right-2 bg-indigo-600 text-white px-2 py-1 rounded text-[10px] opacity-0 group-hover:opacity-100">COPY</button></div><div class="mt-4 bg-slate-900 p-4 rounded-xl relative group"><code id="cb" class="text-xs text-indigo-300 font-mono">font-family: {css_b};</code><button onclick="c('cb')" class="absolute top-2 right-2 bg-indigo-600 text-white px-2 py-1 rounded text-[10px] opacity-0 group-hover:opacity-100">COPY</button></div></div></div></div></div><script>function u() {{ const v = document.getElementById('vs-text').value; document.getElementById('pa').innerText = v; document.getElementById('pb').innerText = v; }} function c(id) {{ const t = document.getElementById(id).textContent; navigator.clipboard.writeText(t).then(() => {{ const ts = document.getElementById('toast'); ts.classList.remove('hidden'); setTimeout(() => ts.classList.add('toast-active'), 10); setTimeout(() => {{ ts.classList.remove('toast-active'); setTimeout(() => ts.classList.add('hidden'), 300); }}, 3000); }}); }}</script></body></html>"""
        with open(f"compare/{slug}.html", 'w', encoding='utf-8') as f: f.write(vs_html)
        sitemap += f"  <url><loc>[https://htmlfonts.com/compare/](https://htmlfonts.com/compare/){slug}.html</loc><changefreq>monthly</changefreq><priority>0.9</priority></url>\n"

    # Daily Tip Archive
    sitemap += f"  <url><loc>[https://htmlfonts.com/article/](https://htmlfonts.com/article/){new_data['slug']}.html</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>\n"

    # Finalize Sitemap
    sitemap += '</urlset>'
    with open('sitemap.xml', 'w', encoding='utf-8') as f: f.write(sitemap)
    print("✅ Build Successful: Sitemap, 30 Articles, 30 Comparisons.")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# 4. POST TO X
try:
    client_x = tweepy.Client(consumer_key=os.environ["X_API_KEY"], consumer_secret=os.environ["X_API_SECRET"], access_token=os.environ["X_ACCESS_TOKEN"], access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"])
    client_x.create_tweet(text=f"{new_data['tweet']}\n\nRead more: [https://htmlfonts.com/article/](https://htmlfonts.com/article/){new_data['slug']}.html")
    print("✅ X Post Successful.")
except Exception as e: pass
