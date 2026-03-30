import os
import json
import datetime
import sys
import math
import html
import re
from google import genai
import tweepy

# 1. SETUP & CONSTANTS
DOMAIN = "https://htmlfonts.com"
TAILWIND = "https://cdn.tailwindcss.com"
GFONTS = "https://fonts.googleapis.com/css2"

GA_CODE = """    <script async src="https://www.googletagmanager.com/gtag/js?id=G-TKESX7E20P"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-TKESX7E20P');
    </script>"""

client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

seo_prompt = """Generate a high-value JSON object for a web typography expert blog. 
Target Keywords: CSS typography, UI design, web fonts, user experience. 
Keys MUST exactly match: "title", "slug", "tweet", "tip", "css_snippet".
Return ONLY raw JSON."""

try:
    # Daily Tip Generation
    response = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=seo_prompt)
    raw_text = response.text.strip()
    
    if raw_text.startswith('```json'):
        raw_text = raw_text.replace('```json', '').replace('```', '').strip()
        
    new_data = json.loads(raw_text)
    new_data["date"] = datetime.datetime.now().strftime("%B %d, %Y")

    # Sync Archives Safely
    history = []
    if os.path.exists('history.json'):
        with open('history.json', 'r', encoding='utf-8') as f: 
            history = json.load(f)
    history.insert(0, new_data)
    
    with open('history.json', 'w', encoding='utf-8') as f: json.dump(history, f, indent=4)
    with open('content.json', 'w', encoding='utf-8') as f: json.dump(new_data, f, indent=4)

    os.makedirs('compare', exist_ok=True)
    os.makedirs('article', exist_ok=True)
    
    # Start Sitemap
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="[http://www.sitemaps.org/schemas/sitemap/0.9](http://www.sitemaps.org/schemas/sitemap/0.9)">\n'
    sitemap += f'  <url><loc>{DOMAIN}/</loc><priority>1.0</priority></url>\n'
    sitemap += f'  <url><loc>{DOMAIN}/font-vs-font-comparison-tool.html</loc><priority>0.9</priority></url>\n'
    sitemap += f'  <url><loc>{DOMAIN}/editors-desk.html</loc><priority>0.9</priority></url>\n'
    sitemap += f'  <url><loc>{DOMAIN}/html-css-font-guides.html</loc><priority>0.9</priority></url>\n'

    # 2. INCREDIBLE GUIDES DATA (Omitted for brevity, paste your 30 guides here)
    top_guides = [
        ("how-to-change-font-size-in-html", "How to Change Font Size in HTML", "Responsive Typography", "In modern web design, hard-coding pixel sizes creates accessibility issues. You should use relative units like REM or fluid functions like clamp() to dynamically scale your text.", "font-size: clamp(1rem, 2vw + 0.5rem, 1.5rem);", "Always set your root html font-size to 100% and use REMs for paragraphs.")
        # ... Add the rest of your 29 guides back here ...
    ]

    # REAL HIGH-VOLUME SEO SEARCH TARGETS
    top_comparisons = [
        ("Roboto", "Open Sans", "'Roboto', sans-serif", "'Open Sans', sans-serif", "Roboto:wght@400;700", "Open+Sans:wght@400;700"),
        ("Arial", "Helvetica", "Arial, sans-serif", "Helvetica, Arial, sans-serif", "", ""),
        ("Montserrat", "Poppins", "'Montserrat', sans-serif", "'Poppins', sans-serif", "Montserrat:wght@400;700", "Poppins:wght@400;700"),
        ("Lato", "Open Sans", "'Lato', sans-serif", "'Open Sans', sans-serif", "Lato:wght@400;700", "Open+Sans:wght@400;700"),
        ("Inter", "Roboto", "'Inter', sans-serif", "'Roboto', sans-serif", "Inter:wght@400;700", "Roboto:wght@400;700"),
        ("Playfair Display", "Merriweather", "'Playfair Display', serif", "'Merriweather', serif", "Playfair+Display:wght@400;700", "Merriweather:wght@400;700"),
        ("Nunito", "Poppins", "'Nunito', sans-serif", "'Poppins', sans-serif", "Nunito:wght@400;700", "Poppins:wght@400;700"),
        ("Raleway", "Montserrat", "'Raleway', sans-serif", "'Montserrat', sans-serif", "Raleway:wght@400;700", "Montserrat:wght@400;700"),
        ("Times New Roman", "Georgia", "'Times New Roman', Times, serif", "Georgia, serif", "", ""),
        ("Lora", "PT Serif", "'Lora', serif", "'PT Serif', serif", "Lora:wght@400;700", "PT+Serif:wght@400;700"),
        ("Work Sans", "Fira Sans", "'Work Sans', sans-serif", "'Fira Sans', sans-serif", "Work+Sans:wght@400;700", "Fira+Sans:wght@400;700"),
        ("Rubik", "Karla", "'Rubik', sans-serif", "'Karla', sans-serif", "Rubik:wght@400;700", "Karla:wght@400;700"),
        ("Fira Code", "Source Code Pro", "'Fira Code', monospace", "'Source Code Pro', monospace", "Fira+Code:wght@400;700", "Source+Code+Pro:wght@400;700"),
        ("JetBrains Mono", "Fira Code", "'JetBrains Mono', monospace", "'Fira Code', monospace", "JetBrains+Mono:wght@400;700", "Fira+Code:wght@400;700"),
        ("DM Sans", "Poppins", "'DM Sans', sans-serif", "'Poppins', sans-serif", "DM+Sans:wght@400;700", "Poppins:wght@400;700"),
        ("Crimson Text", "Lora", "'Crimson Text', serif", "'Lora', serif", "Crimson+Text:wght@400;700", "Lora:wght@400;700"),
        ("Quicksand", "Nunito", "'Quicksand', sans-serif", "'Nunito', sans-serif", "Quicksand:wght@400;700", "Nunito:wght@400;700"),
        ("Inconsolata", "Roboto Mono", "'Inconsolata', monospace", "'Roboto Mono', monospace", "Inconsolata:wght@400;700", "Roboto+Mono:wght@400;700"),
        ("PT Sans", "Open Sans", "'PT Sans', sans-serif", "'Open Sans', sans-serif", "PT+Sans:wght@400;700", "Open+Sans:wght@400;700"),
        ("Noto Sans", "Roboto", "'Noto Sans', sans-serif", "'Roboto', sans-serif", "Noto+Sans:wght@400;700", "Roboto:wght@400;700"),
        ("Bitter", "Roboto Slab", "'Bitter', serif", "'Roboto Slab', serif", "Bitter:wght@400;700", "Roboto+Slab:wght@400;700"),
        ("Zilla Slab", "Roboto Slab", "'Zilla Slab', serif", "'Roboto Slab', serif", "Zilla+Slab:wght@400;700", "Roboto+Slab:wght@400;700"),
        ("Outfit", "Lexend", "'Outfit', sans-serif", "'Lexend', sans-serif", "Outfit:wght@400;700", "Lexend:wght@400;700"),
        ("Barlow", "Rubik", "'Barlow', sans-serif", "'Rubik', sans-serif", "Barlow:wght@400;700", "Rubik:wght@400;700"),
        ("Space Grotesk", "Lexend", "'Space Grotesk', sans-serif", "'Lexend', sans-serif", "Space+Grotesk:wght@400;700", "Lexend:wght@400;700"),
        ("Public Sans", "DM Sans", "'Public Sans', sans-serif", "'DM Sans', sans-serif", "Public+Sans:wght@400;700", "DM+Sans:wght@400;700"),
        ("Cormorant", "Playfair Display", "'Cormorant', serif", "'Playfair Display', serif", "Cormorant:wght@400;700", "Playfair+Display:wght@400;700"),
        ("Pacifico", "Dancing Script", "'Pacifico', cursive", "'Dancing Script', cursive", "Pacifico", "Dancing+Script:wght@400;700"),
        ("Oswald", "Bebas Neue", "'Oswald', sans-serif", "'Bebas Neue', sans-serif", "Oswald:wght@400;700", "Bebas+Neue"),
        ("IBM Plex Mono", "Space Mono", "'IBM Plex Mono', monospace", "'Space Mono', monospace", "IBM+Plex+Mono:wght@400;700", "Space+Mono:wght@400;700")
    ]

    header_html = """    <header class="bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 h-16 flex items-center px-6 shadow-sm">
        <div class="max-w-7xl mx-auto w-full flex justify-between items-center">
            <a href="/" class="flex items-center gap-2 group">
                <div class="bg-gradient-to-br from-indigo-600 to-violet-600 text-white p-1.5 rounded-lg shadow-md group-hover:scale-105 transition-transform">
                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h8m-8 6h16"></path></svg>
                </div>
                <div class="font-black text-2xl tracking-tighter"><span class="text-indigo-600">html</span>fonts</div>
            </a>
            <nav class="hidden md:flex space-x-8 text-xs font-bold uppercase tracking-widest text-slate-500">
                <a href="/" class="hover:text-indigo-600 transition">Directory</a>
                <a href="/font-vs-font-comparison-tool.html" class="hover:text-indigo-600 transition">Font VS Font</a>
                <a href="/editors-desk.html" class="hover:text-indigo-600 transition">Editor's Desk</a>
                <a href="/html-css-font-guides.html" class="hover:text-indigo-600 transition">Guides</a>
            </nav>
        </div>
    </header>"""

    # 3. GENERATE COMPARISONS AND DYNAMICALLY BUILD INTERNAL LINKS
    comparison_grid_links = ""
    
    for font_a, font_b, css_a, css_b, link_a, link_b in top_comparisons:
        slug = f"{font_a.lower().replace(' ', '-')}-vs-{font_b.lower().replace(' ', '-')}"
        imp_a = f"<link href='{GFONTS}?family={link_a}&display=swap' rel='stylesheet'>" if link_a else ""
        imp_b = f"<link href='{GFONTS}?family={link_b}&display=swap' rel='stylesheet'>" if link_b else ""
        
        # Build the URL links that will be injected into your main tool page
        comparison_grid_links += f'                    <a href="/compare/{slug}.html" class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-indigo-300 transition-all font-bold text-sm text-slate-700 hover:text-indigo-600 text-center">{font_a} vs {font_b}</a>\n'

        sys_msg = '<span class="font-sans font-medium text-emerald-600">✨ System font. No HTML import required!</span>'
        html_a = imp_a if imp_a else sys_msg
        html_b = imp_b if imp_b else sys_msg

        safe_ha = html_a.replace("'", "\\'").replace('"', '&quot;')
        safe_hb = html_b.replace("'", "\\'").replace('"', '&quot;')

        vs_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{font_a} vs {font_b} | Side-by-Side Comparison</title>
    <meta name="description" content="Compare {font_a} and {font_b} web fonts side-by-side. Test legibility and generate CSS HTML code instantly.">
    {GA_CODE}
    <script src="{TAILWIND}"></script>
    {imp_a}
    {imp_b}
</head>
<body class="bg-slate-50 min-h-screen flex flex-col selection:bg-indigo-200 selection:text-indigo-900">
{header_html}
    <main class="flex-grow w-full py-16 md:py-24">
        <h1 class="text-center text-4xl font-black">{font_a} vs {font_b}</h1>
    </main>
</body>
</html>"""
        with open(f"compare/{slug}.html", 'w', encoding='utf-8') as f: f.write(vs_html)
        sitemap += f"  <url><loc>{DOMAIN}/compare/{slug}.html</loc><changefreq>monthly</changefreq><priority>0.9</priority></url>\n"

    # 4. FIX ORPHAN PAGES: INJECT THE LINKS INTO font-vs-font-comparison-tool.html
    if os.path.exists('font-vs-font-comparison-tool.html'):
        with open('font-vs-font-comparison-tool.html', 'r', encoding='utf-8') as f:
            tool_page_content = f.read()

        # Regex dynamically finds the grid in your HTML and completely rewrites the inner links
        pattern = r'(<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">)(.*?)(</div>\s*</div>\s*</section>)'
        updated_tool_content = re.sub(pattern, rf'\1\n{comparison_grid_links}                \3', tool_page_content, flags=re.DOTALL)

        with open('font-vs-font-comparison-tool.html', 'w', encoding='utf-8') as f:
            f.write(updated_tool_content)
        print("✅ SEO Architecture Fixed: Injected comparison links into main tool page.")
    else:
        print("⚠️ Warning: font-vs-font-comparison-tool.html not found to inject links.")

    sitemap += '</urlset>'
    with open('sitemap.xml', 'w', encoding='utf-8') as f: f.write(sitemap)
    print("✅ Build Successful: Created pages and sitemap.")

except Exception as e:
    print(f"❌ Generation Error: {e}")

sys.exit(0)
