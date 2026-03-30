import os
import json
import datetime
from google import genai
import tweepy

# 1. SETUP & CONSTANTS
DOMAIN = "https://htmlfonts.com"
TAILWIND = "https://cdn.tailwindcss.com"
GFONTS = "https://fonts.googleapis.com/css2"

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

    # Sync Archives
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

    # 2. CONTENT DEFINITIONS (All 60 Items)
    top_guides = [
        ("how-to-change-font-size-in-html", "How to Change Font Size in HTML", "Learn to use the CSS font-size property with px, rem, and em units.", "font-size: 16px;"),
        ("how-to-add-google-fonts-to-html", "How to Add Google Fonts to HTML", "Step-by-step guide to embedding external fonts via the link tag.", "<link href='...' rel='stylesheet'>"),
        ("how-to-change-font-color-in-html", "How to Change Font Color in HTML", "Use CSS hex codes and RGB values to style your web typography.", "color: #4f46e5;"),
        ("how-to-bold-text-in-html", "How to Bold Text in HTML", "Master the font-weight property for stronger visual hierarchy.", "font-weight: 800;"),
        ("how-to-center-text-in-html", "How to Center Text in HTML", "The best ways to align text using CSS text-align and flexbox.", "text-align: center;"),
        ("what-is-the-best-font-for-reading", "The Best Fonts for On-Screen Reading", "Why high x-height fonts like Inter and Roboto lead the industry.", "font-family: 'Inter', sans-serif;"),
        ("how-to-use-custom-fonts-in-css", "How to Use Custom Fonts in CSS", "Tutorial on @font-face for self-hosting your own font files.", "@font-face { font-family: 'MyFont'; src: url('...'); }"),
        ("how-to-add-text-shadow-in-css", "How to Add Text Shadow in CSS", "Create depth with the text-shadow property and rgba colors.", "text-shadow: 2px 2px 5px rgba(0,0,0,0.1);"),
        ("how-to-import-local-fonts", "How to Import Local Fonts in HTML", "Using system-ui and locally installed typefaces for speed.", "font-family: system-ui, sans-serif;"),
        ("how-to-underline-text-in-css", "How to Underline Text in CSS", "Beyond the u tag: modern text-decoration styling.", "text-decoration: underline;"),
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
        ("how-to-import-adobe-fonts", "How to Import Adobe Typekit Fonts", "Integrating Creative Cloud fonts into your web project.", "<script src='...typekit...'></script>"),
        ("what-is-x-height-typography", "Understanding X-Height in Typography", "How vertical proportions affect font legibility on web.", "/* Concept Guide */"),
        ("best-serif-fonts-for-minimalist-web", "Best Serif Fonts for Minimalism", "Top serif choices for modern, clean web interfaces.", "font-family: 'Lora', serif;"),
        ("how-to-add-font-fallback-stacks", "Creating Bulletproof Font Stacks", "How to ensure your site looks good even if fonts fail.", "font-family: 'Inter', Arial, sans-serif;")
    ]

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

    # Generate Individual 30 Guide Articles
    guides_cards_html = ""
    for slug, title, desc, code in top_guides:
        safe_code = code.replace('<', '&lt;').replace('>', '&gt;')
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>{title} | htmlfonts Guides</title>
    <meta name="description" content="{desc}">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <script src="{TAILWIND}"></script>
    <style>body {{ font-family: system-ui, sans-serif; }}</style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col selection:bg-indigo-200">
    <header class="bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 h-16 flex items-center px-6">
        <div class="max-w-7xl mx-auto w-full flex justify-between items-center">
            <a href="/" class="font-black text-2xl group"><span class="text-indigo-600">html</span>fonts</a>
            <nav class="hidden md:flex space-x-8 text-xs font-bold uppercase tracking-widest text-slate-500">
                <a href="/" class="hover:text-indigo-600 transition">Directory</a>
                <a href="/font-vs-font-comparison-tool.html" class="hover:text-indigo-600 transition">Font VS Font</a>
                <a href="/editors-desk.html" class="hover:text-indigo-600 transition">Editor's Desk</a>
                <a href="/html-css-font-guides.html" class="hover:text-indigo-600 transition">Guides</a>
            </nav>
        </div>
    </header>
    <main class="flex-grow py-16 px-6">
        <div class="max-w-3xl mx-auto">
            <a href="/html-css-font-guides.html" class="text-indigo-600 font-bold uppercase tracking-widest text-xs">&larr; Back to Guides</a>
            <article class="bg-white p-10 mt-8 rounded-3xl shadow-lg border border-slate-200">
                <h1 class="text-4xl font-black mb-4 tracking-tight text-slate-900">{title}</h1>
                <p class="text-xl text-slate-600 mb-8">{desc}</p>
                <div class="bg-slate-900 p-6 rounded-xl overflow-x-auto">
                    <code class="text-indigo-300 font-mono text-sm whitespace-pre">{safe_code}</code>
                </div>
            </article>
        </div>
    </main>
    <footer class="bg-white border-t py-12 text-center text-xs font-bold text-slate-500 uppercase tracking-widest">
        <p>&copy; {datetime.datetime.now().year} htmlfonts</p>
    </footer>
</body>
</html>"""
        with open(f"article/{slug}.html", 'w', encoding='utf-8') as f: f.write(html)
        sitemap += f"  <url><loc>{DOMAIN}/article/{slug}.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>\n"
        
        guides_cards_html += f"""
        <a href="/article/{slug}.html" class="block bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:shadow-xl hover:border-indigo-300 transition-all group">
            <h3 class="text-xl font-black text-slate-900 group-hover:text-indigo-600 transition-colors">{title}</h3>
            <p class="text-slate-500 mt-2 font-medium leading-relaxed">{desc}</p>
        </a>"""

    # Generate the MASTER GUIDES Directory Page
    guides_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>HTML & CSS Font Guides | htmlfonts</title>
    <meta name="description" content="Master web typography with our comprehensive CSS and HTML font guides.">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <script src="{TAILWIND}"></script>
    <style>body {{ font-family: system-ui, sans-serif; }}</style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col font-sans selection:bg-indigo-200">
    <header class="bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 h-16 flex items-center px-6">
        <div class="max-w-7xl mx-auto w-full flex justify-between items-center">
            <a href="/" class="font-black text-2xl"><span class="text-indigo-600">html</span>fonts</a>
            <nav class="hidden md:flex space-x-8 text-xs font-bold uppercase tracking-widest text-slate-500">
                <a href="/">Directory</a>
                <a href="/font-vs-font-comparison-tool.html">Font VS Font</a>
                <a href="/editors-desk.html">Editor's Desk</a>
                <a href="/html-css-font-guides.html" class="text-indigo-600">Guides</a>
            </nav>
        </div>
    </header>
    <main class="flex-grow py-16 px-6 max-w-5xl mx-auto w-full">
        <h1 class="text-5xl font-black tracking-tight text-slate-900 mb-4">Typography Guides</h1>
        <p class="text-xl text-slate-500 mb-12">Master CSS typography with our 30 essential guides.</p>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {guides_cards_html}
        </div>
    </main>
    <footer class="bg-white border-t py-12 text-center text-xs font-bold text-slate-500 uppercase tracking-widest">
        <p>&copy; {datetime.datetime.now().year} htmlfonts</p>
    </footer>
</body>
</html>"""
    with open("html-css-font-guides.html", 'w', encoding='utf-8') as f: f.write(guides_page_html)

    # Generate Comparisons
    for font_a, font_b, css_a, css_b, link_a, link_b in top_comparisons:
        slug = f"{font_a.lower().replace(' ', '-')}-vs-{font_b.lower().replace(' ', '-')}"
        imp_a = f"<link href='{GFONTS}?family={link_a}&display=swap' rel='stylesheet'>" if link_a else ""
        imp_b = f"<link href='{GFONTS}?family={link_b}&display=swap' rel='stylesheet'>" if link_b else ""
        safe_a = imp_a.replace('<', '&lt;').replace('>', '&gt;')
        safe_b = imp_b.replace('<', '&lt;').replace('>', '&gt;')
        sys_msg = '<span class="font-sans font-medium text-emerald-400">✨ Web-safe system font. Pre-installed on all devices for zero-latency loading. No HTML import required!</span>'
        html_a = safe_a if safe_a else sys_msg
        html_b = safe_b if safe_b else sys_msg

        # FIX: Clean button variables extracted OUTSIDE the f-string block
        btn_ha = '<button onclick="c(\'ha\')" class="absolute top-2 right-2 bg-indigo-600 text-white px-2 py-1 rounded text-[10px] opacity-0 group-hover:opacity-100 transition">COPY</button>' if link_a else ''
        btn_hb = '<button onclick="c(\'hb\')" class="absolute top-2 right-2 bg-indigo-600 text-white px-2 py-1 rounded text-[10px] opacity-0 group-hover:opacity-100 transition">COPY</button>' if link_b else ''
        
        btn_ca = '<button onclick="c(\'ca\')" class="absolute top-2 right-2 bg-indigo-600 text-white px-2 py-1 rounded text-[10px] opacity-0 group-hover:opacity-100 transition">COPY</button>'
        btn_cb = '<button onclick="c(\'cb\')" class="absolute top-2 right-2 bg-indigo-600 text-white px-2 py-1 rounded text-[10px] opacity-0 group-hover:opacity-100 transition">COPY</button>'

        vs_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{font_a} vs {font_b} | Side-by-Side Comparison</title>
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <script src="{TAILWIND}"></script>
    {imp_a}
    {imp_b}
    <style>body {{ font-family: system-ui, sans-serif; }} .toast-active {{ opacity: 1; transform: translate(-50%, 0); transition: all 0.3s; }}</style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col selection:bg-indigo-200">
    <div id="toast" class="fixed bottom-10 left-1/2 transform -translate-x-1/2 hidden bg-slate-900 text-white px-8 py-4 rounded-2xl shadow-2xl z-[100] text-sm font-black uppercase">Copied! 🚀</div>
    <header class="bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 h-16 flex items-center px-6">
        <div class="max-w-7xl mx-auto w-full flex justify-between items-center">
            <a href="/" class="font-black text-2xl group"><span class="text-indigo-600">html</span>fonts</a>
            <nav class="hidden md:flex space-x-8 text-xs font-bold uppercase tracking-widest text-slate-500">
                <a href="/" class="hover:text-indigo-600 transition">Directory</a>
                <a href="/font-vs-font-comparison-tool.html" class="hover:text-indigo-600 transition">Font VS Font</a>
                <a href="/editors-desk.html" class="hover:text-indigo-600 transition">Editor's Desk</a>
                <a href="/html-css-font-guides.html" class="hover:text-indigo-600 transition">Guides</a>
            </nav>
        </div>
    </header>
    <main class="flex-grow py-16 px-4">
        <div class="max-w-6xl mx-auto w-full">
            <div class="text-center mb-12">
                <a href="/font-vs-font-comparison-tool.html" class="text-indigo-600 font-bold text-xs uppercase tracking-widest">&larr; Back to Tool</a>
                <h1 class="text-5xl font-black mt-6 tracking-tight text-slate-900">{font_a} <span class="text-slate-300">vs</span> {font_b}</h1>
            </div>
            <div class="bg-white rounded-3xl p-10 shadow-2xl border border-slate-200/60">
                <input type="text" id="vs-text" value="Optimize your UI design with fast-loading fonts." onfocus="if(this.value==='Optimize your UI design with fast-loading fonts.') this.value=''" onblur="if(this.value==='') this.value='Optimize your UI design with fast-loading fonts.'" oninput="u()" class="w-full mb-10 px-6 py-4 bg-slate-50 border rounded-xl text-xl text-center font-medium shadow-inner outline-none focus:ring-2 focus:ring-indigo-500 transition-all">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-10 divide-y md:divide-y-0 md:divide-x divide-slate-100">
                    <div>
                        <div class="flex items-center gap-2 mb-6">
                            <span class="bg-indigo-600 text-white text-[10px] font-black px-2 py-1 rounded">A</span>
                            <h3 class="text-2xl font-black">{font_a}</h3>
                        </div>
                        <div class="bg-indigo-50/20 p-6 rounded-2xl border border-indigo-100/50 min-h-[200px] flex items-center">
                            <p id="pa" class="text-5xl leading-tight text-indigo-900 w-full" style="font-family: {css_a};">Optimize your UI design with fast-loading fonts.</p>
                        </div>
                        <div class="mt-8 bg-slate-900 p-4 rounded-xl relative group text-left">
                            <code id="ha" class="text-xs text-indigo-300 font-mono block">{html_a}</code>
                            {btn_ha}
                        </div>
                        <div class="mt-4 bg-slate-900 p-4 rounded-xl relative group text-left">
                            <code id="ca" class="text-xs text-indigo-300 font-mono">font-family: {css_a};</code>
                            {btn_ca}
                        </div>
                    </div>
                    <div>
                        <div class="flex items-center gap-2 mb-6 md:ml-10">
                            <span class="bg-violet-600 text-white text-[10px] font-black px-2 py-1 rounded">B</span>
                            <h3 class="text-2xl font-black">{font_b}</h3>
                        </div>
                        <div class="md:ml-10 bg-violet-50/20 p-6 rounded-2xl border border-violet-100/50 min-h-[200px] flex items-center">
                            <p id="pb" class="text-5xl leading-tight text-violet-900 w-full" style="font-family: {css_b};">Optimize your UI design with fast-loading fonts.</p>
                        </div>
                        <div class="md:ml-10 mt-8 bg-slate-900 p-4 rounded-xl relative group text-left">
                            <code id="hb" class="text-xs text-indigo-300 font-mono block">{html_b}</code>
                            {btn_hb}
                        </div>
                        <div class="md:ml-10 mt-4 bg-slate-900 p-4 rounded-xl relative group text-left">
                            <code id="cb" class="text-xs text-indigo-300 font-mono">font-family: {css_b};</code>
                            {btn_cb}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
    <footer class="bg-white border-t py-12 text-center text-xs font-bold text-slate-500 uppercase tracking-widest">
        <p>&copy; {datetime.datetime.now().year} htmlfonts</p>
    </footer>
    <script>
        function u() {{ 
            const v = document.getElementById('vs-text').value; 
            document.getElementById('pa').innerText = v; 
            document.getElementById('pb').innerText = v; 
        }} 
        function c(id) {{ 
            const t = document.getElementById(id).textContent; 
            navigator.clipboard.writeText(t).then(() => {{ 
                const ts = document.getElementById('toast'); 
                ts.classList.remove('hidden'); 
                setTimeout(() => ts.classList.add('toast-active'), 10); 
                setTimeout(() => {{ 
                    ts.classList.remove('toast-active'); 
                    setTimeout(() => ts.classList.add('hidden'), 300); 
                }}, 3000); 
            }}); 
        }}
    </script>
</body>
</html>"""
        with open(f"compare/{slug}.html", 'w', encoding='utf-8') as f: f.write(vs_html)
        sitemap += f"  <url><loc>{DOMAIN}/compare/{slug}.html</loc><changefreq>monthly</changefreq><priority>0.9</priority></url>\n"

    # Generate Today's Editor's Desk Tip Article
    tip_safe_code = new_data['css_snippet'].replace('<', '&lt;').replace('>', '&gt;')
    tip_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>{new_data['title']} | Editor's Desk</title>
    <meta name="description" content="{new_data['tip']}">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <script src="{TAILWIND}"></script>
    <style>body {{ font-family: system-ui, sans-serif; }}</style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col font-sans selection:bg-indigo-200">
    <header class="bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 h-16 flex items-center px-6">
        <div class="max-w-7xl mx-auto w-full flex justify-between items-center">
            <a href="/" class="font-black text-2xl"><span class="text-indigo-600">html</span>fonts</a>
            <nav class="hidden md:flex space-x-8 text-xs font-bold uppercase tracking-widest text-slate-500">
                <a href="/">Directory</a>
                <a href="/font-vs-font-comparison-tool.html">Font VS Font</a>
                <a href="/editors-desk.html" class="text-indigo-600">Editor's Desk</a>
                <a href="/html-css-font-guides.html">Guides</a>
            </nav>
        </div>
    </header>
    <main class="flex-grow py-16 px-6">
        <div class="max-w-3xl mx-auto">
            <a href="/editors-desk.html" class="text-indigo-600 font-bold uppercase tracking-widest text-xs">&larr; Back to Archive</a>
            <article class="bg-white p-10 mt-8 rounded-3xl shadow-lg border border-slate-200">
                <span class="text-indigo-600 text-xs font-black uppercase tracking-widest">{new_data['date']}</span>
                <h1 class="text-4xl font-black mt-2 mb-4 tracking-tight text-slate-900">{new_data['title']}</h1>
                <p class="text-xl text-slate-600 mb-8 font-medium leading-relaxed">{new_data['tip']}</p>
                <div class="bg-slate-900 p-8 rounded-2xl overflow-x-auto border border-slate-800">
                    <pre class="text-indigo-300 font-mono text-sm"><code>{tip_safe_code}</code></pre>
                </div>
            </article>
        </div>
    </main>
    <footer class="bg-white border-t py-12 text-center text-xs font-bold text-slate-500 uppercase tracking-widest">
        <p>&copy; {datetime.datetime.now().year} htmlfonts</p>
    </footer>
</body>
</html>"""
    with open(f"article/{new_data['slug']}.html", 'w', encoding='utf-8') as f: f.write(tip_html)
    sitemap += f"  <url><loc>{DOMAIN}/article/{new_data['slug']}.html</loc><priority>0.7</priority></url>\n"

    # BUILD THE ARCHIVE PAGE (editors-desk.html)
    archive_cards = ""
    for item in history:
        archive_cards += f"""
        <a href="/article/{item['slug']}.html" class="block bg-white p-8 rounded-3xl shadow-sm border border-slate-200 hover:shadow-xl hover:border-indigo-300 transition-all group">
            <span class="text-xs font-black text-indigo-600 uppercase tracking-widest">{item['date']}</span>
            <h3 class="text-2xl font-black text-slate-900 mt-2 group-hover:text-indigo-600 transition-colors">{item['title']}</h3>
            <p class="text-slate-500 mt-3 font-medium leading-relaxed">{item['tip']}</p>
        </a>"""
    
    archive_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>Editor's Desk Archive | htmlfonts</title>
    <meta name="description" content="Daily CSS typography tips and web design insights.">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <script src="{TAILWIND}"></script>
    <style>body {{ font-family: system-ui, sans-serif; }}</style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col font-sans selection:bg-indigo-200">
    <header class="bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 h-16 flex items-center px-6">
        <div class="max-w-7xl mx-auto w-full flex justify-between items-center">
            <a href="/" class="font-black text-2xl"><span class="text-indigo-600">html</span>fonts</a>
            <nav class="hidden md:flex space-x-8 text-xs font-bold uppercase tracking-widest text-slate-500">
                <a href="/">Directory</a>
                <a href="/font-vs-font-comparison-tool.html">Font VS Font</a>
                <a href="/editors-desk.html" class="text-indigo-600">Editor's Desk</a>
                <a href="/html-css-font-guides.html">Guides</a>
            </nav>
        </div>
    </header>
    <main class="flex-grow py-16 px-6 max-w-4xl mx-auto w-full">
        <h1 class="text-5xl font-black tracking-tight text-slate-900 mb-4">Editor's Desk Archive</h1>
        <p class="text-xl text-slate-500 mb-12">Every tip, snippet, and typography insight we've ever published.</p>
        <div class="space-y-6">{archive_cards}</div>
    </main>
    <footer class="bg-white border-t py-12 text-center text-xs font-bold text-slate-500 uppercase tracking-widest">
        <p>&copy; {datetime.datetime.now().year} htmlfonts</p>
    </footer>
</body>
</html>"""
    with open("editors-desk.html", 'w', encoding='utf-8') as f: f.write(archive_html)

    sitemap += '</urlset>'
    with open('sitemap.xml', 'w', encoding='utf-8') as f: f.write(sitemap)
    print(f"✅ Build Successful: Created Guides, Comparisons, and Editor Archive.")

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
    
    tweet_text = f"{new_data['tweet']}\n\nRead Tip: {DOMAIN}/article/{new_data['slug']}.html #webdesign #typography"
    client_x.create_tweet(text=tweet_text)
    print("✅ X Post Successful.")
except Exception as e:
    print(f"❌ X Post Failed: {e}")
