import os
import json
import datetime
import sys
import math
import html
import re
import time
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

# LOAD SEO CACHE (This ensures we never ask Gemini twice for the same fonts)
CACHE_FILE = 'seo_descriptions_cache.json'
seo_cache = {}
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        seo_cache = json.load(f)

def save_cache():
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(seo_cache, f, indent=4)

seo_prompt = """Generate a high-value JSON object for a web typography expert blog. 
Target Keywords: CSS typography, UI design, web fonts, user experience. 
Keys MUST exactly match: "title", "slug", "tweet", "tip", "css_snippet".
Return ONLY raw JSON."""

try:
    # Daily Tip Generation (With 1-minute retry for rate limits)
    print("Generating Daily Tip...")
    for attempt in range(3):
        try:
            response = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=seo_prompt)
            raw_text = response.text.strip()
            break
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                print("API busy. Waiting 60 seconds before retrying...")
                time.sleep(60)
            else:
                raise e

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

    # 2. INCREDIBLE GUIDES DATA
    top_guides = [
        ("how-to-change-font-size-in-html", "How to Change Font Size in HTML", "Responsive Typography", "In modern web design, hard-coding pixel sizes creates accessibility issues. You should use relative units like REM or fluid functions like clamp() to dynamically scale your text.", "font-size: clamp(1rem, 2vw + 0.5rem, 1.5rem);", "Always set your root html font-size to 100% and use REMs for paragraphs."),
        ("how-to-add-google-fonts-to-html", "How to Add Google Fonts to HTML", "Performance Optimization", "Embedding external fonts requires a link tag in your document head. To ensure your page doesn't suffer from layout shifts, always include display=swap.", "<link href='[https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap)' rel='stylesheet'>", "Preconnect to the Google Fonts server to shave 100ms off your load time."),
        ("best-css-font-pairings", "Best CSS Font Pairings", "Visual Hierarchy", "The secret to beautiful UI design is pairing a highly legible Sans-Serif for body text with a high-contrast Serif or Display font for headings.", "h1 { font-family: 'Playfair Display', serif; } \np { font-family: 'Inter', sans-serif; }", "Never use more than two font families on a single project to maintain brand consistency."),
        ("how-to-change-font-color-in-html", "How to Change Font Color in HTML", "Color Theory", "Changing text color is done via the CSS color property. For modern, accessible design, ensure your text has at least a 4.5:1 contrast ratio against its background.", "color: #1e293b; /* Deep Slate */", "Avoid pure black (#000000) on pure white; use dark grays like #111827 to reduce eye strain."),
        ("how-to-bold-text-in-html", "How to Bold Text in HTML", "Font Weights", "Instead of using the outdated bold tag, use the CSS font-weight property. A weight of 400 is standard, 700 is bold, and 900 is black.", "font-weight: 700;", "Only import the font weights you actually use from Google Fonts to save bandwidth."),
        ("how-to-center-text-in-html", "How to Center Text in HTML", "Layout Alignment", "Centering text horizontally is easy with text-align, but for perfect vertical centering, Flexbox or CSS Grid is the modern standard.", ".center-box {\n  display: flex;\n  justify-content: center;\n  align-items: center;\n}", "Avoid using line-height equal to container height for multi-line text."),
        ("what-is-the-best-font-for-reading", "The Best Fonts for On-Screen Reading", "Accessibility", "Fonts with a large x-height, open counters, and distinct letterforms (like differentiating capital I and lowercase l) drastically improve reading speeds.", "font-family: 'Inter', system-ui, sans-serif;", "Test your body text at 14px; if it's hard to read, pick a different font entirely."),
        ("how-to-use-custom-fonts-in-css", "How to Use Custom Fonts in CSS", "Asset Hosting", "The @font-face rule allows you to host your own typography files. Always serve modern formats like WOFF2 for maximum compression and fast loading.", "@font-face {\n  font-family: 'MyBrandFont';\n  src: url('/fonts/myfont.woff2') format('woff2');\n  font-display: swap;\n}", "Always include a web-safe fallback stack to prevent invisible text during loading."),
        ("how-to-add-text-shadow-in-css", "How to Add Text Shadow in CSS", "Visual Depth", "Text shadows add depth and improve contrast over noisy backgrounds. The syntax takes X-offset, Y-offset, blur radius, and color.", "text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);", "Use subtle, low-opacity shadows for modern UI; harsh, solid shadows look dated."),
        ("how-to-import-local-fonts", "How to Import Local Fonts in HTML", "Performance", "To completely eliminate layout shifts and download times, you can tell CSS to use the fonts already installed on the user's operating system.", "font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;", "System fonts are the secret to achieving a perfect 100 Lighthouse performance score."),
        ("how-to-underline-text-in-css", "How to Underline Text in CSS", "Text Decoration", "The classic text-decoration property has been upgraded. You can now control the color, style, and thickness of underlines independently of the text.", "text-decoration: underline;\ntext-decoration-color: #4f46e5;\ntext-decoration-thickness: 2px;", "Use text-underline-offset to give your links a little breathing room from the line."),
        ("how-to-make-fluid-typography", "Creating Fluid Typography in CSS", "Responsive Design", "Instead of writing dozens of media queries, CSS clamp() allows your font size to smoothly scale based on the viewport width.", "font-size: clamp(1rem, 2.5vw, 2rem);", "Use fluid typography for main headings, but keep body text mostly static for readability."),
        ("rem-vs-em-css-guide", "REM vs EM: Which CSS Unit is Best?", "Relative Sizing", "EMs compound based on their parent elements, which can lead to unpredictable sizes. REMs always scale relative to the root HTML element.", "padding: 2rem;\nfont-size: 1.125rem;", "Set your browser default to 100% and use REMs for all your typography sizing."),
        ("how-to-change-line-height-in-css", "Improving Readability with Line Height", "Vertical Rhythm", "Line-height controls the vertical space between lines. The golden rule for body copy is a line-height between 1.4 and 1.6 to allow the eye to track back.", "p {\n  line-height: 1.6;\n}", "Never use fixed pixel values for line-height; always use unitless multipliers."),
        ("how-to-style-drop-caps-in-html", "How to Style Drop Caps in HTML", "Editorial Design", "You can create gorgeous, magazine-style drop caps using the ::first-letter pseudo-element without adding extra span tags to your HTML.", "p::first-letter {\n  font-size: 3.5em;\n  font-weight: bold;\n  float: left;\n}", "Ensure your drop cap aligns perfectly with the baseline of the adjacent text lines."),
        ("how-to-add-letter-spacing-in-css", "How to Adjust Letter Spacing", "Kerning & Tracking", "Letter-spacing adds horizontal space between characters. It's fantastic for uppercase headings but can destroy the legibility of lowercase body text.", "h1 {\n  text-transform: uppercase;\n  letter-spacing: 0.1em;\n}", "As font size increases, letter-spacing should generally decrease for tighter tracking."),
        ("how-to-use-variable-fonts-in-html", "How to Use Variable Fonts in HTML", "Advanced Typography", "Variable fonts contain multiple variations (weight, width, slant) in a single file, drastically reducing HTTP requests and page weight.", "font-family: 'Inter Variable';\nfont-variation-settings: 'wght' 650, 'slnt' -5;", "Check browser support before relying entirely on custom font-variation axes."),
        ("how-to-prevent-text-wrapping-css", "Preventing Text Wrapping in CSS", "UI Control", "Sometimes you need a button or badge to stay on a single line regardless of the container width. The white-space property handles this elegantly.", ".badge {\n  white-space: nowrap;\n  overflow: hidden;\n  text-overflow: ellipsis;\n}", "Always combine nowrap with text-overflow: ellipsis to handle extreme edge cases gracefully."),
        ("how-to-create-gradient-text-css", "How to Create Gradient Text in CSS", "Modern Styling", "To create a gradient text effect, you apply a background gradient, clip it to the text, and make the actual text color transparent.", "background: linear-gradient(to right, #4f46e5, #7c3aed);\n-webkit-background-clip: text;\ncolor: transparent;", "Provide a solid fallback color for older browsers that don't support background-clip."),
        ("best-fonts-for-mobile-apps", "The Best Fonts for Mobile App UI", "Interface Design", "Mobile screens require fonts with highly legible numerals, distinct geometry, and excellent rendering at small sizes (12px to 14px).", "font-family: 'Roboto', 'San Francisco', sans-serif;", "Rely on the native OS fonts for the most performant and native-feeling app experience."),
        ("how-to-load-fonts-asynchronously", "How to Load Fonts Asynchronously", "Web Vitals", "Custom fonts can block page rendering. Using font-display: swap tells the browser to show a fallback font immediately until the custom font finishes downloading.", "@font-face {\n  font-display: swap;\n}", "Preload your critical above-the-fold fonts in the HTML head to avoid flashing."),
        ("how-to-use-monospace-fonts-for-coding", "Best Monospace Fonts for Developers", "Code Aesthetics", "Monospace fonts allocate the exact same width to every character, making them essential for code editors, tabular data, and technical documentation.", "font-family: 'Fira Code', 'JetBrains Mono', monospace;", "Enable CSS font-variant-ligatures if your monospace font supports coding ligatures."),
        ("how-to-italicize-text-in-css", "How to Italicize Text in CSS", "Emphasis", "The font-style property is used to italicize text. Note that true italic uses specially drawn glyphs, while oblique just artificially slants the regular font.", "em, i {\n  font-style: italic;\n}", "Use true italics whenever the font family supports them, rather than relying on browser obliques."),
        ("how-to-change-font-weight-numerically", "Font Weight 100 to 900 Explained", "Typography Scales", "CSS font weights range from 100 (Thin) to 900 (Black). The value 400 maps to normal and 700 maps exactly to bold.", "font-weight: 600; /* Semi-Bold */", "Skip weights to create contrast. Pair a 300 Light with a 700 Bold for maximum impact."),
        ("how-to-capitalize-first-letter-css", "Capitalizing First Letters with CSS", "Text Transformation", "CSS can automatically change the casing of your text without modifying the source HTML by utilizing the text-transform property.", "text-transform: capitalize;\n/* OR */\ntext-transform: uppercase;", "Use text-transform instead of typing ALL CAPS in your HTML for better screen reader accessibility."),
        ("how-to-add-columns-to-text", "Creating Newspaper Columns in CSS", "Advanced Layout", "The CSS column-count property automatically flows your text into multiple columns, just like a newspaper, automatically balancing the height.", "p.article {\n  column-count: 2;\n  column-gap: 2rem;\n}", "Avoid using columns on mobile devices; set column-count to 1 for screens under 768px."),
        ("how-to-fix-blurry-fonts-on-browser", "How to Fix Blurry Fonts in Chrome", "Rendering Optimization", "On MacOS, you can toggle the subpixel rendering engine to make light text on dark backgrounds appear crisper and less bulky.", "-webkit-font-smoothing: antialiased;\n-moz-osx-font-smoothing: grayscale;", "Only use antialiased smoothing for light text on dark backgrounds; it hurts dark text legibility."),
        ("how-to-import-adobe-fonts", "How to Import Adobe Fonts", "Premium Typography", "Adobe Fonts are integrated using a stylesheet exactly like Google Fonts, utilizing your specific project ID in the link tag.", "<link rel='stylesheet' href='[https://use.typekit.net/your_id.css](https://use.typekit.net/your_id.css)'>", "Adobe Fonts do not support the exact same subsetting parameters via URL as Google Fonts."),
        ("what-is-x-height-typography", "Understanding X-Height in Typography", "Design Theory", "The x-height is the vertical distance between the baseline and the median line of lowercase letters. Large x-heights improve legibility at small sizes.", "/* Conceptual Design Rule */", "When pairing fonts, try to match their x-heights to create visual harmony across the interface."),
        ("how-to-add-font-fallback-stacks", "Creating Bulletproof Font Stacks", "Resilience", "A font stack is a prioritized list of fallback fonts. The browser will try each one in order until it finds one installed on the user's system.", "font-family: 'MyCustomFont', 'Helvetica Neue', Arial, sans-serif;", "Always end your CSS font stack with a generic family name like sans-serif or serif.")
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

    # UNIVERSAL HEADER TEMPLATE
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
            <button onclick="document.getElementById('mobile-menu').classList.toggle('hidden')" class="md:hidden p-2 text-slate-600 hover:text-indigo-600">
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
            </button>
        </div>
        <div id="mobile-menu" class="hidden absolute top-16 left-0 w-full bg-white border-b border-slate-200 shadow-xl z-30 px-6 py-6 space-y-4 md:hidden">
            <a href="/" class="block text-sm font-bold text-slate-700 hover:text-indigo-600">Directory</a>
            <a href="/font-vs-font-comparison-tool.html" class="block text-sm font-bold text-slate-700 hover:text-indigo-600">Font VS Font</a>
            <a href="/editors-desk.html" class="block text-sm font-bold text-slate-700 hover:text-indigo-600">Editor's Desk</a>
            <a href="/html-css-font-guides.html" class="block text-sm font-bold text-slate-700 hover:text-indigo-600">Guides</a>
        </div>
    </header>"""

    # Generate 30 INCREDIBLE Guide Articles
    guides_cards_html = ""
    for slug, title, subtitle, concept, code, protip in top_guides:
        safe_desc = html.escape(concept)
        safe_code = html.escape(code)
        
        html_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | htmlfonts Guides</title>
    <meta name="description" content="{safe_desc}">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
{GA_CODE}
    <script src="{TAILWIND}"></script>
    <style>body {{ font-family: system-ui, sans-serif; }}</style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col selection:bg-indigo-200 selection:text-indigo-900">
{header_html}
    <main class="flex-grow py-16 px-4">
        <div class="max-w-4xl mx-auto">
            <a href="/html-css-font-guides.html" class="text-indigo-600 font-bold uppercase tracking-widest text-xs hover:text-indigo-800 transition">&larr; Back to Guides Directory</a>
            
            <article class="bg-white p-8 md:p-14 mt-8 rounded-[2rem] shadow-[0_20px_50px_rgb(0,0,0,0.05)] border border-slate-100 relative overflow-hidden">
                <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-indigo-500 to-violet-500"></div>
                
                <span class="inline-block bg-indigo-50 border border-indigo-100 text-indigo-700 text-[10px] font-black px-3 py-1.5 rounded-full uppercase tracking-[0.2em] mb-4">{subtitle}</span>
                <h1 class="text-4xl md:text-5xl font-black mt-2 mb-10 tracking-tight text-slate-900 leading-tight">{title}</h1>
                
                <div class="prose prose-lg text-slate-600 max-w-none">
                    <h2 class="text-2xl font-black text-slate-800 mb-4 flex items-center gap-3">
                        <span class="text-indigo-500">01.</span> The Concept
                    </h2>
                    <p class="mb-12 text-lg leading-relaxed font-medium">{concept}</p>
                    
                    <h2 class="text-2xl font-black text-slate-800 mb-4 flex items-center gap-3">
                        <span class="text-violet-500">02.</span> Production-Ready Code
                    </h2>
                    <div class="bg-slate-50 p-6 md:p-8 rounded-2xl overflow-x-auto mb-12 border border-slate-200 shadow-sm">
                        <code class="text-slate-800 font-mono text-sm whitespace-pre block">{safe_code}</code>
                    </div>
                    
                    <div class="bg-gradient-to-r from-violet-50 to-indigo-50 border-l-4 border-indigo-500 p-8 rounded-r-2xl shadow-sm">
                        <h3 class="text-indigo-900 font-black text-xs uppercase tracking-widest mb-3 flex items-center gap-2">
                            <span>💡</span> Pro Typography Tip
                        </h3>
                        <p class="text-indigo-800 font-semibold m-0 leading-relaxed">{protip}</p>
                    </div>
                </div>
            </article>
        </div>
    </main>
    <footer class="bg-white border-t border-slate-200 py-12 text-center text-xs font-bold text-slate-500 uppercase tracking-widest mt-auto">
        <p>&copy; {datetime.datetime.now().year} htmlfonts</p>
    </footer>
</body>
</html>"""
        with open(f"article/{slug}.html", 'w', encoding='utf-8') as f: f.write(html_page)
        sitemap += f"  <url><loc>{DOMAIN}/article/{slug}.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>\n"
        
        guides_cards_html += f"""
        <a href="/article/{slug}.html" class="block bg-white p-8 rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-indigo-50 hover:border-indigo-200 hover:shadow-indigo-100/50 transition-all group relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-violet-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <span class="text-[10px] font-black text-indigo-500 uppercase tracking-widest block mb-3">{subtitle}</span>
            <h3 class="text-2xl font-black text-slate-900 group-hover:text-indigo-600 transition-colors mb-4 leading-snug">{title}</h3>
            <p class="text-slate-500 font-medium leading-relaxed">{concept[:110]}...</p>
        </a>"""

    # Generate the MASTER GUIDES Directory Page
    guides_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML & CSS Font Guides | htmlfonts</title>
    <meta name="description" content="Master web typography with our comprehensive CSS and HTML font guides.">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
{GA_CODE}
    <script src="{TAILWIND}"></script>
    <style>body {{ font-family: system-ui, sans-serif; }}</style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col font-sans selection:bg-indigo-200 selection:text-indigo-900">
{header_html}
    <main class="flex-grow py-16 px-6 max-w-7xl mx-auto w-full">
        <div class="text-center mb-16 max-w-3xl mx-auto">
            <h1 class="text-5xl md:text-6xl font-black tracking-tight mb-6"><span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Typography Guides</span></h1>
            <p class="text-xl text-slate-500 font-medium leading-relaxed">Master CSS typography and build better web interfaces with our deep-dive technical tutorials.</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {guides_cards_html}
        </div>
    </main>
    <footer class="bg-white border-t border-slate-200 py-12 text-center text-xs font-bold text-slate-500 uppercase tracking-widest mt-auto">
        <p>&copy; {datetime.datetime.now().year} htmlfonts</p>
    </footer>
</body>
</html>"""
    with open("html-css-font-guides.html", 'w', encoding='utf-8') as f: f.write(guides_page_html)

    # Generate COMPARISONS with UI matching exactly the main tool + CACHED AI DESCRIPTIONS
    comparison_grid_links = ""
    for font_a, font_b, css_a, css_b, link_a, link_b in top_comparisons:
        slug = f"{font_a.lower().replace(' ', '-')}-vs-{font_b.lower().replace(' ', '-')}"
        imp_a = f"<link href='{GFONTS}?family={link_a}&display=swap' rel='stylesheet'>" if link_a else ""
        imp_b = f"<link href='{GFONTS}?family={link_b}&display=swap' rel='stylesheet'>" if link_b else ""
        
        comparison_grid_links += f'                    <a href="/compare/{slug}.html" class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-indigo-300 transition-all font-bold text-sm text-slate-700 hover:text-indigo-600 text-center">{font_a} vs {font_b}</a>\n'

        # UPDATED: Added select-none class and your exact text for the system font message
        sys_msg = '<span class="font-sans font-medium text-emerald-400 select-none">✨ Web-safe system font. Pre-installed on all devices for zero-latency loading. No HTML import required!</span>'
        html_a = imp_a if imp_a else sys_msg
        html_b = imp_b if imp_b else sys_msg

        safe_ha = html_a.replace("'", "\\'").replace('"', '&quot;')
        safe_hb = html_b.replace("'", "\\'").replace('"', '&quot;')

        # GENERATE OR LOAD SEO DESCRIPTION
        cache_key = f"{font_a}_vs_{font_b}"
        if cache_key in seo_cache:
            print(f"Loading cached SEO description for {font_a} vs {font_b}...")
            seo_description = seo_cache[cache_key]
        else:
            print(f"Generating NEW SEO description for {font_a} vs {font_b}...")
            desc_prompt = f"You are amazing, absolutely the best SEO and Projects specialist. Please create an amazing description (short helpful history of these two font pairs and key differences between them) for these fonts: {font_a} vs {font_b}. Return ONLY raw HTML (no markdown blocks, no ```html). Structure it with an <h2 class='text-2xl font-black text-slate-900 mb-4'> for the title, and <p class='mb-4 leading-relaxed'> for the text. Use <strong> for emphasis."
            try:
                # Add a 4 second pause before asking to stay under the 15 per minute free tier limit
                time.sleep(4) 
                resp = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=desc_prompt)
                seo_description = resp.text.replace('```html', '').replace('```', '').strip()
                seo_cache[cache_key] = seo_description
                save_cache() # Save immediately so we don't lose it if it crashes later!
            except Exception as e:
                print(f"Error generating description: {e}")
                if "429" in str(e):
                    print("⚠️ Hit the rate limit. Waiting 60 seconds and trying this one again...")
                    time.sleep(60)
                    # Retry once more after waiting
                    resp = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=desc_prompt)
                    seo_description = resp.text.replace('```html', '').replace('```', '').strip()
                    seo_cache[cache_key] = seo_description
                    save_cache()
                else:
                    seo_description = f"<h2 class='text-2xl font-black text-slate-900 mb-4'>The Difference Between {font_a} and {font_b}</h2><p class='mb-4 leading-relaxed'>Compare the typography, legibility, and modern UI capabilities of {font_a} and {font_b}.</p>"

        vs_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{font_a} vs {font_b} | Side-by-Side Comparison</title>
    <meta name="description" content="Compare {font_a} and {font_b} web fonts side-by-side. Test legibility and generate CSS HTML code instantly.">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
{GA_CODE}
    <script src="{TAILWIND}"></script>
    {imp_a}
    {imp_b}
    <style>
        body {{ font-family: system-ui, sans-serif; -webkit-tap-highlight-color: transparent; }}
        .toast-active {{ opacity: 1; transform: translate(-50%, 0); transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
        .modal-active {{ opacity: 1; transform: scale(1) translateY(0); transition: all 0.2s ease-out; }}
        .comparison-text {{ transition: font-size 0.2s ease; }}
    </style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col selection:bg-indigo-200 selection:text-indigo-900">
    <div id="toast" class="fixed bottom-10 left-1/2 transform -translate-x-1/2 hidden bg-slate-900 text-white px-8 py-4 rounded-2xl shadow-2xl z-[100] text-sm font-black uppercase flex items-center gap-3">Copied! 🚀</div>
{header_html}
    <main class="flex-grow w-full py-16 md:py-24">
        <section class="max-w-7xl mx-auto px-4 sm:px-6">
            <div class="text-center mb-12">
                <a href="/font-vs-font-comparison-tool.html" class="text-indigo-600 font-bold text-xs uppercase tracking-widest hover:text-indigo-800 transition">&larr; Back to Tool</a>
                <h1 class="text-4xl md:text-5xl font-black mt-6 tracking-tight text-slate-900">{font_a} <span class="text-slate-300">vs</span> {font_b}</h1>
            </div>
            
            <div class="bg-white rounded-3xl p-6 md:p-10 shadow-[0_20px_50px_rgb(0,0,0,0.05)] border border-slate-100">
                <div class="flex flex-col md:flex-row gap-6 mb-12 items-stretch">
                    <div class="w-full md:w-2/3 bg-slate-50 border border-slate-200 rounded-2xl py-4 px-6 shadow-inner flex flex-col justify-center focus-within:ring-2 focus-within:ring-indigo-500 focus-within:bg-white transition-all">
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 px-1">Testing Playground</label>
                        <input type="text" id="vs-text" value="Optimize your UI design with fast-loading free web fonts." 
                            onfocus="if(this.value===this.defaultValue) this.value='';" 
                            onblur="if(this.value==='') {{ this.value=this.defaultValue; u(); }}"
                            oninput="u()"
                            class="w-full bg-transparent px-1 outline-none text-lg md:text-xl font-medium text-slate-800 placeholder-slate-300">
                    </div>
                    
                    <div class="w-full md:w-1/3 bg-slate-50 border border-slate-200 rounded-2xl py-4 px-6 shadow-inner flex flex-col justify-center">
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Compare Size</span>
                            <span id="vs-size-label" class="bg-indigo-100 text-indigo-700 font-black text-[10px] px-2 py-1 rounded-md">32px</span>
                        </div>
                        <input type="range" id="vs-font-size" min="12" max="120" value="32" oninput="u()" class="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600">
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-10 divide-y md:divide-y-0 md:divide-x divide-slate-100">
                    <div class="md:pr-10 pt-6 md:pt-0 flex flex-col h-full">
                        <div class="flex items-center gap-3 mb-6">
                            <span class="bg-indigo-600 text-white text-[10px] font-black px-2 py-1 rounded-md shadow-lg shadow-indigo-200 uppercase">A</span>
                            <h3 class="text-2xl font-black">{font_a}</h3>
                        </div>
                        <div class="flex-grow flex items-start pt-10 px-6 pb-6 min-h-[250px] bg-indigo-50/20 rounded-2xl border border-indigo-100/50">
                            <p id="pa" class="comparison-text text-black break-words leading-tight w-full" style="font-family: {css_a}; font-size: 32px;">Optimize your UI design with fast-loading free web fonts.</p>
                        </div>
                        <button onclick="openModal('a')" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-black uppercase tracking-widest py-4 rounded-xl transition shadow-xl shadow-indigo-100 mt-8 group">
                            GET CODE FOR FONT A <span class="inline-block transition-transform group-hover:translate-x-1">&rarr;</span>
                        </button>
                    </div>

                    <div class="md:pl-10 pt-10 md:pt-0 flex flex-col h-full">
                        <div class="flex items-center gap-3 mb-6">
                            <span class="bg-violet-600 text-white text-[10px] font-black px-2 py-1 rounded-md shadow-lg shadow-violet-200 uppercase">B</span>
                            <h3 class="text-2xl font-black">{font_b}</h3>
                        </div>
                        <div class="flex-grow flex items-start pt-10 px-6 pb-6 min-h-[250px] bg-violet-50/20 rounded-2xl border border-violet-100/50">
                            <p id="pb" class="comparison-text text-black break-words leading-tight w-full" style="font-family: {css_b}; font-size: 32px;">Optimize your UI design with fast-loading free web fonts.</p>
                        </div>
                        <button onclick="openModal('b')" class="w-full bg-violet-600 hover:bg-violet-700 text-white text-xs font-black uppercase tracking-widest py-4 rounded-xl transition shadow-xl shadow-violet-100 mt-8 group">
                            GET CODE FOR FONT B <span class="inline-block transition-transform group-hover:translate-x-1">&rarr;</span>
                        </button>
                    </div>
                </div>
            </div>

            <div class="mt-12 bg-white p-8 md:p-12 rounded-3xl shadow-[0_20px_50px_rgb(0,0,0,0.05)] border border-slate-100 text-slate-600">
                {seo_description}
            </div>

        </section>
    </main>
    
    <div id="code-modal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-xl p-8 relative modal-enter" id="modal-content">
            <button onclick="closeModal('code-modal')" class="absolute top-6 right-6 text-slate-400 hover:text-slate-900 bg-slate-50 rounded-full p-2">✕</button>
            <h3 class="text-3xl font-black text-slate-900 tracking-tighter mb-8" id="modal-font-name">Font Detail</h3>
            <div class="space-y-6">
                <div>
                    <label class="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2" id="modal-html-label">1. Add to HTML Head</label>
                    <div class="bg-slate-900 rounded-xl p-4 relative group">
                        <code id="modal-html" class="text-xs text-indigo-300 font-mono break-all block"></code>
                        <button id="copy-html-btn" onclick="copyElementText('modal-html')" class="absolute top-3 right-3 text-[10px] font-bold text-white bg-indigo-600 px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition shadow-md">COPY HTML</button>
                    </div>
                </div>
                <div>
                    <label class="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2">2. Apply CSS Rule</label>
                    <div class="bg-slate-900 rounded-xl p-4 relative group border-2 border-indigo-500/30">
                        <code id="modal-css" class="text-xs font-mono text-indigo-300 block"></code>
                        <button onclick="copyElementText('modal-css')" class="absolute top-3 right-3 text-[10px] font-bold text-white bg-indigo-600 px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition shadow-md">COPY CSS</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="bg-white border-t border-slate-200 py-12 text-center text-xs font-bold text-slate-500 uppercase tracking-widest mt-auto">
        <p>&copy; {datetime.datetime.now().year} htmlfonts</p>
    </footer>
    
    <script>
        const fontData = {{
            'a': {{ name: "{font_a}", css: "{css_a}", html: '{safe_ha}' }},
            'b': {{ name: "{font_b}", css: "{css_b}", html: '{safe_hb}' }}
        }};

        function u() {{ 
            const v = document.getElementById('vs-text').value || 'Optimize your UI design with fast-loading free web fonts.'; 
            const sz = document.getElementById('vs-font-size').value;
            document.getElementById('vs-size-label').innerText = sz + 'px';
            
            const pa = document.getElementById('pa');
            pa.innerText = v;
            pa.style.fontSize = sz + 'px';
            
            const pb = document.getElementById('pb');
            pb.innerText = v;
            pb.style.fontSize = sz + 'px';
        }} 
        
        function openModal(side) {{
            const data = fontData[side];
            document.getElementById('modal-font-name').innerText = data.name;
            const htmlCode = document.getElementById('modal-html');
            const copyBtn = document.getElementById('copy-html-btn');
            const htmlLabel = document.getElementById('modal-html-label');
            
            // UPDATED: Label ALWAYS stays as "1. Add to HTML Head"
            htmlLabel.innerText = "1. Add to HTML Head";
            
            // UPDATED: Check for the exact new text you provided
            if (data.html.includes('Web-safe system font')) {{
                htmlCode.innerHTML = data.html; 
                htmlCode.className = "text-xs block";
                copyBtn.style.display = 'none';
            }} else {{
                htmlCode.textContent = data.html; 
                htmlCode.className = "text-xs font-mono text-indigo-300 break-all block";
                copyBtn.style.display = 'block';
            }}
            
            document.getElementById('modal-css').innerText = `font-family: ${{data.css}};`;
            document.getElementById('code-modal').classList.remove('hidden');
            setTimeout(() => document.getElementById('modal-content').classList.add('modal-active'), 10);
        }}
        
        function closeModal(id) {{ document.getElementById('modal-content').classList.remove('modal-active'); setTimeout(() => document.getElementById(id).classList.add('hidden'), 200); }}
        
        function triggerToast(msg = "Copied! 🚀") {{
            const t = document.getElementById('toast'); 
            t.classList.remove('hidden'); setTimeout(() => t.classList.add('toast-active'), 10);
            setTimeout(() => {{ t.classList.remove('toast-active'); setTimeout(() => t.classList.add('hidden'), 300); }}, 3000);
        }}
        
        function copyElementText(id) {{
            const txt = document.getElementById(id).textContent;
            navigator.clipboard.writeText(txt).then(() => triggerToast()).catch(() => {{
                const el = document.createElement('textarea'); el.value = txt; document.body.appendChild(el);
                el.select(); document.execCommand('copy'); document.body.removeChild(el); triggerToast();
            }});
        }}
    </script>
</body>
</html>"""
        with open(f"compare/{slug}.html", 'w', encoding='utf-8') as f: f.write(vs_html)
        sitemap += f"  <url><loc>{DOMAIN}/compare/{slug}.html</loc><changefreq>monthly</changefreq><priority>0.9</priority></url>\n"

    # Generate Today's Editor's Desk Tip Article
    tip_safe_desc = html.escape(str(new_data.get('tip', '')))
    tip_safe_code = html.escape(str(new_data.get('css_snippet', '')))
    
    tip_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{new_data['title']} | Editor's Desk</title>
    <meta name="description" content="{tip_safe_desc}">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
{GA_CODE}
    <script src="{TAILWIND}"></script>
    <style>body {{ font-family: system-ui, sans-serif; }}</style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col font-sans selection:bg-indigo-200 selection:text-indigo-900">
{header_html}
    <main class="flex-grow py-16 px-4">
        <div class="max-w-4xl mx-auto">
            <a href="/editors-desk.html" class="text-indigo-600 font-bold uppercase tracking-widest text-xs hover:text-indigo-800 transition">&larr; Back to Archive</a>
            <article class="bg-white p-8 md:p-14 mt-8 rounded-[2rem] shadow-[0_20px_50px_rgb(0,0,0,0.05)] border border-slate-100 relative overflow-hidden">
                <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-indigo-500 to-violet-500"></div>
                <span class="inline-block bg-indigo-50 border border-indigo-100 text-indigo-700 text-[10px] font-black px-3 py-1.5 rounded-full uppercase tracking-[0.2em] mb-4">{new_data['date']}</span>
                <h1 class="text-4xl md:text-5xl font-black mt-2 mb-8 tracking-tight text-slate-900 leading-tight">{new_data['title']}</h1>
                <p class="text-xl text-slate-600 mb-10 font-medium leading-relaxed">{new_data['tip']}</p>
                <div class="bg-slate-50 p-6 md:p-8 rounded-2xl overflow-x-auto border border-slate-200 shadow-sm">
                    <pre class="text-slate-800 font-mono text-sm whitespace-pre block"><code>{tip_safe_code}</code></pre>
                </div>
            </article>
        </div>
    </main>
    <footer class="bg-white border-t border-slate-200 py-12 text-center text-xs font-bold text-slate-500 uppercase tracking-widest mt-auto">
        <p>&copy; {datetime.datetime.now().year} htmlfonts</p>
    </footer>
</body>
</html>"""
    with open(f"article/{new_data['slug']}.html", 'w', encoding='utf-8') as f: f.write(tip_html)
    sitemap += f"  <url><loc>{DOMAIN}/article/{new_data['slug']}.html</loc><priority>0.7</priority></url>\n"

    # BUILD THE PAGINATED ARCHIVE (editors-desk.html)
    items_per_page = 10
    total_items = len(history)
    total_pages = max(1, math.ceil(total_items / items_per_page))

    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_items = history[start_idx:end_idx]

        archive_cards = ""
        for item in page_items:
            archive_cards += f"""
            <a href="/article/{item['slug']}.html" class="block bg-white p-8 rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-indigo-50 hover:border-indigo-200 hover:shadow-indigo-100/50 transition-all group relative overflow-hidden">
                <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-violet-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <span class="text-[10px] font-black text-indigo-500 uppercase tracking-widest block mb-3">{item['date']}</span>
                <h3 class="text-2xl font-black text-slate-900 group-hover:text-indigo-600 transition-colors mb-3">{item['title']}</h3>
                <p class="text-slate-500 font-medium leading-relaxed">{item['tip']}</p>
            </a>"""

        # Build Pagination Controls
        pagination_html = '<div class="flex justify-center flex-wrap gap-2 mt-12">'
        for p in range(1, total_pages + 1):
            page_link = "editors-desk.html" if p == 1 else f"editors-desk-{p}.html"
            active_class = "bg-indigo-600 text-white shadow-md" if p == page_num else "bg-white text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 border border-slate-200"
            pagination_html += f'<a href="/{page_link}" class="w-10 h-10 flex items-center justify-center rounded-xl font-bold {active_class} transition-all">{p}</a>'
        pagination_html += '</div>'

        # Generate HTML for this specific page
        archive_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editor's Desk Archive - Page {page_num} | htmlfonts</title>
    <meta name="description" content="Daily CSS typography tips and web design insights. Page {page_num}.">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
{GA_CODE}
    <script src="{TAILWIND}"></script>
    <style>body {{ font-family: system-ui, sans-serif; }}</style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col font-sans selection:bg-indigo-200 selection:text-indigo-900">
{header_html}
    <main class="flex-grow py-16 px-6 max-w-4xl mx-auto w-full">
        <div class="text-center mb-16">
            <h1 class="text-5xl md:text-6xl font-black tracking-tight mb-6"><span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Editor's Desk</span></h1>
            <p class="text-xl text-slate-500 font-medium leading-relaxed">Every CSS typography tip, design trick, and code snippet we've ever published.</p>
        </div>
        <div class="space-y-6">{archive_cards}</div>
        {pagination_html if total_pages > 1 else ""}
    </main>
    <footer class="bg-white border-t border-slate-200 py-12 text-center text-xs font-bold text-slate-500 uppercase tracking-widest mt-auto">
        <p>&copy; {datetime.datetime.now().year} htmlfonts</p>
    </footer>
</body>
</html>"""
        
        file_name = "editors-desk.html" if page_num == 1 else f"editors-desk-{page_num}.html"
        with open(file_name, 'w', encoding='utf-8') as f: f.write(archive_html)
        sitemap += f"  <url><loc>{DOMAIN}/{file_name}</loc><changefreq>daily</changefreq><priority>0.8</priority></url>\n"

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
    print(f"✅ Build Successful: Created Guides, Comparisons, and {total_pages} Paginated Editor Archive pages.")

except Exception as e:
    print(f"❌ Generation Error: {e}")
    sys.exit(0)

# 5. POST TO X (Twitter)
try:
    print("Attempting to authenticate with X.com...")
    client_x = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
    )
    
    tweet_text = f"{new_data['tweet']}\n\nRead Tip: {DOMAIN}/article/{new_data['slug']}.html #webdesign #typography"
    print(f"Tweeting: {tweet_text}")
    
    response = client_x.create_tweet(text=tweet_text)
    print(f"✅ X Post Successful. Status ID: {response.data['id']}")

except Exception as e:
    print(f"❌ X Post Failed: {e}")

sys.exit(0)
