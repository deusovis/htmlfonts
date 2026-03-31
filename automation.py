import os
import json
import datetime
import sys
import math
import html
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

client_gemini = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

# LOAD CACHES TO PROTECT API RATE LIMITS & ENABLE INCREMENTAL BUILDS
CACHE_FILE = 'seo_descriptions_cache.json'
PROFILE_CACHE_FILE = 'font_profiles_cache.json'

seo_cache = {}
profile_cache = {}

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r', encoding='utf-8') as f: seo_cache = json.load(f)
if os.path.exists(PROFILE_CACHE_FILE):
    with open(PROFILE_CACHE_FILE, 'r', encoding='utf-8') as f: profile_cache = json.load(f)

def save_cache():
    with open(CACHE_FILE, 'w', encoding='utf-8') as f: json.dump(seo_cache, f, indent=4)
def save_profile_cache():
    with open(PROFILE_CACHE_FILE, 'w', encoding='utf-8') as f: json.dump(profile_cache, f, indent=4)

seo_prompt = """Generate a high-value JSON object for a web typography expert blog. 
Target Keywords: CSS typography, UI design, web fonts, user experience. 
Keys MUST exactly match: "title", "slug", "tweet", "tip", "css_snippet".
Return ONLY raw JSON."""

# 2. FULL DATA ARRAYS
master_fonts = [
    {"name": "Abril Fatface", "css": "'Abril Fatface', display", "link": "Abril+Fatface", "type": "Display"},
    {"name": "Amatic SC", "css": "'Amatic SC', cursive", "link": "Amatic+SC:wght@400;700", "type": "Handwriting"},
    {"name": "Anton", "css": "'Anton', sans-serif", "link": "Anton", "type": "Sans-Serif"},
    {"name": "Arial", "css": "Arial, Helvetica, sans-serif", "link": None, "type": "Sans-Serif"},
    {"name": "Arvo", "css": "'Arvo', serif", "link": "Arvo:wght@400;700", "type": "Serif"},
    {"name": "Bangers", "css": "'Bangers', display", "link": "Bangers", "type": "Display"},
    {"name": "Barlow", "css": "'Barlow', sans-serif", "link": "Barlow:wght@400;500;700", "type": "Sans-Serif"},
    {"name": "Bebas Neue", "css": "'Bebas Neue', sans-serif", "link": "Bebas+Neue", "type": "Sans-Serif"},
    {"name": "Bitter", "css": "'Bitter', serif", "link": "Bitter:wght@400;600;700", "type": "Serif"},
    {"name": "Caveat", "css": "'Caveat', cursive", "link": "Caveat:wght@400;500;600;700", "type": "Handwriting"},
    {"name": "Cinzel", "css": "'Cinzel', serif", "link": "Cinzel:wght@400;500;600;700;800", "type": "Serif"},
    {"name": "Comfortaa", "css": "'Comfortaa', display", "link": "Comfortaa:wght@400;500;600;700", "type": "Display"},
    {"name": "Cormorant", "css": "'Cormorant', serif", "link": "Cormorant:wght@400;600;700", "type": "Serif"},
    {"name": "Courier New", "css": "'Courier New', Courier, monospace", "link": None, "type": "Monospace"},
    {"name": "Crimson Pro", "css": "'Crimson Pro', serif", "link": "Crimson+Pro:wght@400;600;700", "type": "Serif"},
    {"name": "Crimson Text", "css": "'Crimson Text', serif", "link": "Crimson+Text:wght@400;600;700", "type": "Serif"},
    {"name": "Dancing Script", "css": "'Dancing Script', cursive", "link": "Dancing+Script:wght@400;500;600;700", "type": "Handwriting"},
    {"name": "DM Sans", "css": "'DM Sans', sans-serif", "link": "DM+Sans:wght@400;500;700", "type": "Sans-Serif"},
    {"name": "EB Garamond", "css": "'EB Garamond', serif", "link": "EB+Garamond:wght@400;600;700", "type": "Serif"},
    {"name": "Fira Code", "css": "'Fira Code', monospace", "link": "Fira+Code:wght@400;500;600;700", "type": "Monospace"},
    {"name": "Fira Sans", "css": "'Fira Sans', sans-serif", "link": "Fira+Sans:wght@400;500;700", "type": "Sans-Serif"},
    {"name": "Fredoka One", "css": "'Fredoka One', display", "link": "Fredoka+One", "type": "Display"},
    {"name": "Georgia", "css": "Georgia, serif", "link": None, "type": "Serif"},
    {"name": "Great Vibes", "css": "'Great Vibes', cursive", "link": "Great+Vibes", "type": "Handwriting"},
    {"name": "Heebo", "css": "'Heebo', sans-serif", "link": "Heebo:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Helvetica", "css": "Helvetica, Arial, sans-serif", "link": None, "type": "Sans-Serif"},
    {"name": "IBM Plex Mono", "css": "'IBM Plex Mono', monospace", "link": "IBM+Plex+Mono:wght@400;500;600;700", "type": "Monospace"},
    {"name": "Inconsolata", "css": "'Inconsolata', monospace", "link": "Inconsolata:wght@400;500;700", "type": "Monospace"},
    {"name": "Indie Flower", "css": "'Indie Flower', cursive", "link": "Indie+Flower", "type": "Handwriting"},
    {"name": "Inter", "css": "'Inter', sans-serif", "link": "Inter:wght@400;600;800;900", "type": "Sans-Serif"},
    {"name": "JetBrains Mono", "css": "'JetBrains Mono', monospace", "link": "JetBrains+Mono:wght@400;500;700;800", "type": "Monospace"},
    {"name": "Josefin Slab", "css": "'Josefin Slab', serif", "link": "Josefin+Slab:wght@400;600;700", "type": "Serif"},
    {"name": "Karla", "css": "'Karla', sans-serif", "link": "Karla:wght@400;700", "type": "Sans-Serif"},
    {"name": "Lato", "css": "'Lato', sans-serif", "link": "Lato:wght@400;700;900", "type": "Sans-Serif"},
    {"name": "Lexend", "css": "'Lexend', sans-serif", "link": "Lexend:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Libre Baskerville", "css": "'Libre Baskerville', serif", "link": "Libre+Baskerville:wght@400;700", "type": "Serif"},
    {"name": "Lobster", "css": "'Lobster', display", "link": "Lobster", "type": "Display"},
    {"name": "Lora", "css": "'Lora', serif", "link": "Lora:wght@400;500;600;700", "type": "Serif"},
    {"name": "Merriweather", "css": "'Merriweather', serif", "link": "Merriweather:wght@400;700;900", "type": "Serif"},
    {"name": "Montserrat", "css": "'Montserrat', sans-serif", "link": "Montserrat:wght@400;600;700;900", "type": "Sans-Serif"},
    {"name": "Mukta", "css": "'Mukta', sans-serif", "link": "Mukta:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Noto Sans", "css": "'Noto Sans', sans-serif", "link": "Noto+Sans:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Noto Serif", "css": "'Noto Serif', serif", "link": "Noto+Serif:wght@400;600;700", "type": "Serif"},
    {"name": "Nunito", "css": "'Nunito', sans-serif", "link": "Nunito:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Open Sans", "css": "'Open Sans', sans-serif", "link": "Open+Sans:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Oswald", "css": "'Oswald', sans-serif", "link": "Oswald:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Outfit", "css": "'Outfit', sans-serif", "link": "Outfit:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Pacifico", "css": "'Pacifico', cursive", "link": "Pacifico", "type": "Handwriting"},
    {"name": "Playfair Display", "css": "'Playfair Display', serif", "link": "Playfair+Display:wght@400;600;700;800", "type": "Serif"},
    {"name": "Poppins", "css": "'Poppins', sans-serif", "link": "Poppins:wght@400;600;700;800", "type": "Sans-Serif"},
    {"name": "PT Mono", "css": "'PT Mono', monospace", "link": "PT+Mono", "type": "Monospace"},
    {"name": "PT Sans", "css": "'PT Sans', sans-serif", "link": "PT+Sans:wght@400;700", "type": "Sans-Serif"},
    {"name": "PT Serif", "css": "'PT Serif', serif", "link": "PT+Serif:wght@400;700", "type": "Serif"},
    {"name": "Public Sans", "css": "'Public Sans', sans-serif", "link": "Public+Sans:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Quicksand", "css": "'Quicksand', sans-serif", "link": "Quicksand:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Raleway", "css": "'Raleway', sans-serif", "link": "Raleway:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Righteous", "css": "'Righteous', display", "link": "Righteous", "type": "Display"},
    {"name": "Roboto", "css": "'Roboto', sans-serif", "link": "Roboto:wght@400;500;700", "type": "Sans-Serif"},
    {"name": "Roboto Mono", "css": "'Roboto Mono', monospace", "link": "Roboto+Mono:wght@400;500;600;700", "type": "Monospace"},
    {"name": "Rokkitt", "css": "'Rokkitt', serif", "link": "Rokkitt:wght@400;600;700", "type": "Serif"},
    {"name": "Rubik", "css": "'Rubik', sans-serif", "link": "Rubik:wght@400;500;700", "type": "Sans-Serif"},
    {"name": "Satisfy", "css": "'Satisfy', cursive", "link": "Satisfy", "type": "Handwriting"},
    {"name": "Shadows Into Light", "css": "'Shadows Into Light', cursive", "link": "Shadows+Into+Light", "type": "Handwriting"},
    {"name": "Source Code Pro", "css": "'Source Code Pro', monospace", "link": "Source+Code+Pro:wght@400;500;600;700", "type": "Monospace"},
    {"name": "Space Grotesk", "css": "'Space Grotesk', sans-serif", "link": "Space+Grotesk:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Space Mono", "css": "'Space Mono', monospace", "link": "Space+Mono:wght@400;700", "type": "Monospace"},
    {"name": "Teko", "css": "'Teko', sans-serif", "link": "Teko:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Times New Roman", "css": "'Times New Roman', Times, serif", "link": None, "type": "Serif"},
    {"name": "Ubuntu", "css": "'Ubuntu', sans-serif", "link": "Ubuntu:wght@400;500;700", "type": "Sans-Serif"},
    {"name": "Ubuntu Mono", "css": "'Ubuntu Mono', monospace", "link": "Ubuntu+Mono:wght@400;700", "type": "Monospace"},
    {"name": "Verdana", "css": "Verdana, Geneva, sans-serif", "link": None, "type": "Sans-Serif"},
    {"name": "Work Sans", "css": "'Work Sans', sans-serif", "link": "Work+Sans:wght@400;600;700", "type": "Sans-Serif"},
    {"name": "Zilla Slab", "css": "'Zilla Slab', serif", "link": "Zilla+Slab:wght@400;600;700", "type": "Serif"}
]
master_fonts.sort(key=lambda x: x['name'])

top_guides = [
    ("how-to-change-font-size-in-html", "How to Change Font Size in HTML", "Responsive Typography", "In modern web design, hard-coding pixel sizes creates accessibility issues. You should use relative units like REM or fluid functions like clamp() to dynamically scale your text.", "font-size: clamp(1rem, 2vw + 0.5rem, 1.5rem);", "Always set your root html font-size to 100% and use REMs for paragraphs."),
    ("how-to-add-google-fonts-to-html", "How to Add Google Fonts to HTML", "Performance Optimization", "Embedding external fonts requires a link tag in your document head. To ensure your page doesn't suffer from layout shifts, always include display=swap.", "<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap' rel='stylesheet'>", "Preconnect to the Google Fonts server to shave 100ms off your load time."),
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
    ("how-to-import-adobe-fonts", "How to Import Adobe Fonts", "Premium Typography", "Adobe Fonts are integrated using a stylesheet exactly like Google Fonts, utilizing your specific project ID in the link tag.", "<link rel='stylesheet' href='https://use.typekit.net/your_id.css'>", "Adobe Fonts do not support the exact same subsetting parameters via URL as Google Fonts."),
    ("what-is-x-height-typography", "Understanding X-Height in Typography", "Design Theory", "The x-height is the vertical distance between the baseline and the median line of lowercase letters. Large x-heights improve legibility at small sizes.", "/* Conceptual Design Rule */", "When pairing fonts, try to match their x-heights to create visual harmony across the interface."),
    ("how-to-add-font-fallback-stacks", "Creating Bulletproof Font Stacks", "Resilience", "A font stack is a prioritized list of fallback fonts. The browser will try each one in order until it finds one installed on the user's system.", "font-family: 'MyCustomFont', 'Helvetica Neue', Arial, sans-serif;", "Always end your CSS font stack with a generic family name like sans-serif or serif.")
]

# PERFECTLY FIXED: All 30 entries now have exactly 6 arguments.
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

footer_html = f"""    <footer class="bg-white border-t border-slate-200 py-16 mt-auto">
        <div class="max-w-7xl mx-auto px-6 text-center">
            <p class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">&copy; {datetime.datetime.now().year} htmlfonts. All rights reserved.</p>
            <a href="https://x.com/HtmlFonts" target="_blank" class="text-xs font-bold text-indigo-500 hover:text-indigo-600 uppercase tracking-widest transition">Follow @HtmlFonts</a>
        </div>
    </footer>"""

try:
    api_exhausted = False
    
    os.makedirs('compare', exist_ok=True)
    os.makedirs('article', exist_ok=True)
    os.makedirs('font', exist_ok=True)
    
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += f'  <url><loc>{DOMAIN}/</loc><priority>1.0</priority></url>\n'
    sitemap += f'  <url><loc>{DOMAIN}/font-vs-font-comparison-tool.html</loc><priority>0.9</priority></url>\n'
    sitemap += f'  <url><loc>{DOMAIN}/editors-desk.html</loc><priority>0.9</priority></url>\n'
    sitemap += f'  <url><loc>{DOMAIN}/html-css-font-guides.html</loc><priority>0.9</priority></url>\n'

    print("Generating Daily Tip...")
    raw_text = ""
    for attempt in range(3):
        try:
            if not os.environ.get("GEMINI_API_KEY"): break
            response = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=seo_prompt)
            raw_text = response.text.strip()
            break
        except Exception as e:
            err_str = str(e)
            if "429" in err_str:
                if "GenerateRequestsPerDay" in err_str or "limit: 20" in err_str:
                    print("🚨 Daily API limit hit during Daily Tip!")
                    api_exhausted = True
                    break
                elif attempt < 2:
                    print("API busy. Waiting 65s...")
                    time.sleep(65)
                else:
                    api_exhausted = True
            else:
                break

    if raw_text and raw_text.startswith('```json'):
        raw_text = raw_text.replace('```json', '').replace('```', '').strip()
        
    try:
        new_data = json.loads(raw_text) if raw_text else {}
    except:
        new_data = {}
        
    if not new_data or "title" not in new_data:
        new_data = {
            "title": f"Typography Tip {datetime.datetime.now().strftime('%b %d')}",
            "slug": f"typography-tip-{int(time.time())}",
            "tweet": "Check out today's CSS typography tip! #webdesign #css",
            "tip": "To maintain a clean vertical rhythm, always use unitless line-heights in your CSS.",
            "css_snippet": "body {\n  line-height: 1.5;\n}"
        }
        
    new_data["date"] = datetime.datetime.now().strftime("%B %d, %Y")

    history = []
    if os.path.exists('history.json'):
        with open('history.json', 'r', encoding='utf-8') as f: 
            history = json.load(f)
    history.insert(0, new_data)
    
    with open('history.json', 'w', encoding='utf-8') as f: json.dump(history, f, indent=4)
    with open('content.json', 'w', encoding='utf-8') as f: json.dump(new_data, f, indent=4)

    # 3. BUILD INDIVIDUAL SEO FONT PAGES & DIRECTORY CARDS
    directory_grid_html = ""

    for font in master_fonts:
        f_name = font["name"]
        slug = f_name.lower().replace(' ', '-')
        f_css = font["css"]
        f_type = font["type"]
        f_link = f"<link href='{GFONTS}?family={font['link']}&display=swap' rel='stylesheet'>" if font["link"] else ""
        f_url = f"{GFONTS}?family={font['link']}&display=swap" if font["link"] else ""
        
        safe_name = html.escape(f_name, quote=True)
        safe_css = html.escape(f_css, quote=True)
        safe_url = html.escape(f_url, quote=True)
        
        directory_grid_html += f"""
        <div class="font-card bg-white p-8 rounded-3xl border border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all group flex flex-col justify-between overflow-hidden relative min-h-[220px] cursor-pointer" 
             data-font-link="{f_url}"
             data-font-name="{safe_name}"
             data-font-css="{safe_css}"
             data-font-url="{safe_url}"
             data-font-slug="{slug}">
            <div class="absolute top-0 left-0 w-full h-1 bg-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div class="flex-grow flex flex-col">
                <div class="flex justify-between items-center mb-4 shrink-0">
                    <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest group-hover:text-indigo-500 transition-colors">{f_type}</span>
                    <span class="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{f_name}</span>
                </div>
                <p class="font-preview-text text-4xl text-slate-900 break-words leading-tight flex-grow flex items-center" style="font-family: {f_css};" data-default="{f_name}">{f_name}</p>
            </div>
            <div class="mt-8 flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-widest shrink-0 relative z-10">
                <a href="/font/{slug}.html" class="hover:text-indigo-600 transition-colors flex items-center gap-1 group/link z-20 relative">
                    <span>Learn More</span> <span class="text-indigo-500 group-hover/link:translate-x-1 transition-transform">&rarr;</span>
                </a>
                <span class="text-[10px] font-bold bg-slate-50 text-slate-400 px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">&lt;/&gt; Get Code</span>
            </div>
        </div>"""

        ai_content = f"<p class='text-lg text-slate-700 leading-[1.8] mb-8'>Explore the typography, history, and optimal usage of {f_name}. Check back later for the complete expert design breakdown.</p>"

        if slug in profile_cache:
            ai_content = profile_cache[slug]
        elif api_exhausted or not os.environ.get("GEMINI_API_KEY"):
            pass
        else:
            prompt = f"""You are a master editorial web designer and expert UI typographer. Write a highly engaging, magazine-style educational article about the '{f_name}' web font specifically targeting the most searched Google queries.
            
            Your response must include:
            1. The fascinating history and origin of the {f_name} typeface.
            2. Key geometric and design characteristics (e.g., x-height, kerning, counters).
            3. UI design best practices and optimal use cases (headings vs body, mobile vs web).
            4. The absolute best 3 CSS font pairings for {f_name} (provide real CSS examples).

            Return ONLY RAW HTML. You MUST use these EXACT Tailwind classes to ensure a world-class reading experience (DO NOT use markdown):
            
            - Main Section Titles (H2): <h2 class="text-2xl md:text-3xl font-black text-slate-900 mt-16 mb-6 tracking-tight flex items-center gap-4"><span class="w-8 h-1 bg-indigo-500 rounded-full inline-block"></span>
            - Sub Titles (H3): <h3 class="text-xl font-bold text-slate-800 mt-10 mb-4 tracking-tight">
            - Paragraphs: <p class="text-lg text-slate-700 leading-[1.8] mb-8">
            - Emphasized terms: <strong class="font-black text-indigo-900 bg-indigo-50 px-1.5 py-0.5 rounded">
            - Bullet Lists: <ul class="list-none space-y-4 mb-10 pl-0"> (For each item use: <li class="flex items-start gap-3 text-lg text-slate-700 leading-[1.8]"><svg class="w-6 h-6 text-indigo-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg> <span>...</span></li>)
            - Code Blocks (CRITICAL): <pre class="bg-slate-900 text-indigo-200 p-6 rounded-2xl overflow-x-auto font-mono text-sm mb-10 shadow-xl border border-slate-800 leading-relaxed"><code class="text-emerald-400">
            - Blockquotes: <blockquote class="border-l-4 border-indigo-500 bg-indigo-50/50 p-6 md:p-8 rounded-r-2xl text-xl italic font-medium text-slate-800 mb-10 shadow-sm">
            """
            
            for attempt in range(3):
                try:
                    time.sleep(6)
                    resp = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    ai_content = resp.text.replace('```html', '').replace('```', '').strip()
                    profile_cache[slug] = ai_content
                    save_profile_cache()
                    break
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str:
                        if "GenerateRequestsPerDay" in err_str or "limit: 20" in err_str:
                            api_exhausted = True
                            break
                        elif attempt < 2:
                            time.sleep(65)
                        else:
                            api_exhausted = True
                    else:
                        break

        font_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{f_name} Font: History, Pairings, & Best Uses | htmlfonts</title>
    <meta name="description" content="Discover the history, design characteristics, best use cases, and perfect CSS pairings for the {f_name} web font.">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
{GA_CODE}
    <script src="{TAILWIND}"></script>
    {f_link}
    <style>body {{ font-family: system-ui, sans-serif; }}</style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col font-sans selection:bg-indigo-200 selection:text-indigo-900">
{header_html}

    <div class="bg-white border-b border-slate-200 overflow-hidden relative">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-50/50 via-white to-white"></div>
        <div class="max-w-7xl mx-auto px-6 pt-10 pb-12 md:pt-12 md:pb-16 relative z-10 text-center">
            <a href="/" class="text-indigo-600 font-bold uppercase tracking-widest text-xs hover:text-indigo-800 transition inline-block mb-6">&larr; Back to Directory</a>
            <h1 class="text-6xl md:text-8xl font-black tracking-tight mb-4 break-words text-slate-900" style="font-family: {f_css};">
                {f_name}
            </h1>
            <p class="text-lg text-slate-500 font-medium leading-relaxed max-w-2xl mx-auto mt-4 mb-8">The complete typography profile, history, and usage guide.</p>
        </div>
    </div>

    <main class="flex-grow py-16 px-4 md:px-6 w-full">
        <article class="max-w-3xl mx-auto">
            {ai_content}
        </article>
    </main>
{footer_html}
</body>
</html>"""
        with open(f"font/{slug}.html", 'w', encoding='utf-8') as f: f.write(font_page_html)
        sitemap += f"  <url><loc>{DOMAIN}/font/{slug}.html</loc><changefreq>monthly</changefreq><priority>0.9</priority></url>\n"

    # 4. BUILD THE HOME PAGE (INDEX.HTML)
    print("Generating new Home Page (index.html)...")
    
    home_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>htmlfonts | The Ultimate Web Typography Directory</title>
    <meta name="description" content="Discover, compare, and master web typography. The ultimate directory of CSS fonts, side-by-side comparison tools, and expert design guides.">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
{GA_CODE}
    <script src="{TAILWIND}"></script>
    <link rel="preconnect" href="[https://fonts.googleapis.com](https://fonts.googleapis.com)">
    <link rel="preconnect" href="[https://fonts.gstatic.com](https://fonts.gstatic.com)" crossorigin>
    <link href="[https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Playfair+Display:wght@700;900&family=Roboto:wght@400;700&family=Montserrat:wght@700;900&family=Oswald:wght@700&family=Fira+Code:wght@400;700&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Playfair+Display:wght@700;900&family=Roboto:wght@400;700&family=Montserrat:wght@700;900&family=Oswald:wght@700&family=Fira+Code:wght@400;700&display=swap)" rel="stylesheet">
    <style>
        body {{ font-family: system-ui, sans-serif; }}
        .custom-scrollbar::-webkit-scrollbar {{ width: 6px; }}
        .custom-scrollbar::-webkit-scrollbar-track {{ background: #f8fafc; border-radius: 8px; }}
        .custom-scrollbar::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 8px; }}
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {{ background: #94a3b8; }}
    </style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col font-sans selection:bg-indigo-200 selection:text-indigo-900">
    <div id="toast" class="fixed bottom-10 left-1/2 transform -translate-x-1/2 hidden bg-slate-900 text-white px-8 py-4 rounded-2xl shadow-2xl z-[100] text-sm font-black uppercase flex items-center gap-3 transition-all duration-300 opacity-0 translate-y-4">Copied! 🚀</div>
{header_html}
    
    <div class="bg-white border-b border-slate-200 overflow-hidden relative">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-50/50 via-white to-white"></div>
        <div class="max-w-7xl mx-auto px-6 pt-10 pb-12 md:pt-12 md:pb-16 relative z-10 text-center">
            <span class="inline-block bg-indigo-50 border border-indigo-100 text-indigo-700 text-[10px] font-black px-4 py-2 rounded-full uppercase tracking-[0.2em] mb-4 shadow-sm">Most Popular</span>
            <h1 class="text-4xl md:text-5xl font-black tracking-tight text-slate-900 mb-4">
                Free Web <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Fonts.</span>
            </h1>
            <p class="text-lg text-slate-500 font-medium leading-relaxed max-w-2xl mx-auto mt-4 mb-8">The ultimate hub for UI designers and developers. Compare fonts side-by-side, explore typeface history, and learn CSS typography.</p>
            <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
                <a href="/font-vs-font-comparison-tool.html" class="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs uppercase tracking-widest px-6 py-3.5 rounded-xl transition shadow-lg shadow-indigo-200 hover:-translate-y-1">Open Comparison Tool</a>
                <a href="/html-css-font-guides.html" class="w-full sm:w-auto bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 font-bold text-xs uppercase tracking-widest px-6 py-3.5 rounded-xl transition shadow-sm hover:shadow-md hover:-translate-y-1">Read The Guides</a>
            </div>
        </div>
    </div>

    <main class="flex-grow pt-10 pb-24 px-4 md:px-6 max-w-7xl mx-auto w-full">
        <div class="mb-8">
            <div class="w-full max-w-md bg-white border border-slate-200 rounded-2xl py-3 px-4 shadow-sm flex items-center gap-3 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-indigo-500 transition-all relative">
                <svg class="w-5 h-5 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                <input type="text" id="global-preview-input" placeholder="Type here to preview all fonts..." class="w-full bg-transparent outline-none text-base font-medium text-slate-800 placeholder-slate-400">
            </div>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {directory_grid_html}
        </div>
    </main>

    <div id="code-modal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4 transition-opacity duration-300 opacity-0">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-xl p-8 relative transform scale-95 transition-all duration-300 flex flex-col max-h-[90vh]" id="modal-content">
            <button onclick="closeModal('code-modal')" class="absolute top-6 right-6 text-slate-400 hover:text-slate-900 bg-slate-50 hover:bg-slate-100 rounded-full p-2 transition z-10">✕</button>
            
            <div class="mb-6 pr-8">
                <span class="inline-block bg-indigo-50 text-indigo-600 text-[9px] font-black px-2 py-1 rounded uppercase tracking-widest mb-2">Quick Install</span>
                <h3 class="text-3xl md:text-4xl font-black text-slate-900 tracking-tighter" id="modal-font-name">Font Detail</h3>
            </div>

            <div class="space-y-5 overflow-y-auto flex-grow pr-2 custom-scrollbar">
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">1. Import Font</label>
                        <div class="flex bg-slate-100 p-1 rounded-lg">
                            <button onclick="idxToggleImport('html')" id="idx-btn-html" class="text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-indigo-600 transition">HTML</button>
                            <button onclick="idxToggleImport('css')" id="idx-btn-css" class="text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition">@import</button>
                        </div>
                    </div>
                    <div class="bg-slate-900 rounded-xl p-4 relative group min-h-[70px] flex items-center">
                        <code id="modal-html" class="text-[11px] text-indigo-300 font-mono break-all block whitespace-pre-wrap w-full pr-16"></code>
                        <button id="copy-html-btn" onclick="copyElementText('modal-html')" class="absolute top-1/2 -translate-y-1/2 right-3 text-[10px] font-bold text-white bg-indigo-600 hover:bg-indigo-500 px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition shadow-md">COPY</button>
                    </div>
                </div>

                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">2. Apply CSS</label>
                        <div class="flex bg-slate-100 p-1 rounded-lg">
                            <button onclick="idxToggleCss('vanilla')" id="idx-btn-vanilla" class="text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-emerald-600 transition">Vanilla</button>
                            <button onclick="idxToggleCss('tailwind')" id="idx-btn-tailwind" class="text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition">Tailwind</button>
                        </div>
                    </div>
                    <div class="bg-slate-900 rounded-xl p-4 relative group border-2 border-emerald-500/30 min-h-[70px] flex items-center">
                        <pre class="w-full m-0"><code id="modal-css" class="text-[11px] font-mono text-emerald-400 block whitespace-pre-wrap leading-relaxed w-full pr-16"></code></pre>
                        <button onclick="copyElementText('modal-css')" class="absolute top-1/2 -translate-y-1/2 right-3 text-[10px] font-bold text-white bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition shadow-md">COPY</button>
                    </div>
                </div>
            </div>
            
            <div class="mt-6 pt-6 border-t border-slate-100 shrink-0">
                <a href="#" id="modal-read-more" class="w-full flex items-center justify-center gap-2 bg-slate-50 hover:bg-indigo-50 text-slate-700 hover:text-indigo-700 font-black text-xs uppercase tracking-widest py-4 rounded-xl transition border border-slate-200 hover:border-indigo-200 group">
                    <svg class="w-4 h-4 text-slate-400 group-hover:text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                    Read Full Font Guide
                </a>
            </div>
        </div>
    </div>

{footer_html}
    
    <script>
        const previewInput = document.getElementById('global-preview-input');
        const previewTexts = document.querySelectorAll('.font-preview-text');
        
        let idxState = {{ name: '', url: '', css: '', impMode: 'html', cssMode: 'vanilla' }};

        previewInput.addEventListener('input', (e) => {{
            const val = e.target.value;
            previewTexts.forEach(p => {{
                p.textContent = val ? val : p.getAttribute('data-default');
            }});
        }});

        const observer = new IntersectionObserver((entries, obs) => {{
            entries.forEach(entry => {{
                if(entry.isIntersecting) {{
                    const card = entry.target;
                    const fontUrl = card.getAttribute('data-font-link');
                    if(fontUrl && !document.querySelector(`link[href="${{fontUrl}}"]`)) {{
                        const link = document.createElement('link');
                        link.rel = 'stylesheet'; link.href = fontUrl;
                        document.head.appendChild(link);
                    }}
                    obs.unobserve(card); 
                }}
            }});
        }}, {{ rootMargin: '350px' }});

        document.querySelectorAll('.font-card').forEach(card => {{
            observer.observe(card);
            card.addEventListener('click', function(e) {{
                if (e.target.closest('a')) return;
                
                idxState.name = this.getAttribute('data-font-name');
                idxState.css = this.getAttribute('data-font-css');
                idxState.url = this.getAttribute('data-font-url');
                const slug = this.getAttribute('data-font-slug');
                
                document.getElementById('modal-read-more').href = `/font/${{slug}}.html`;
                
                openFontModal();
            }});
        }});

        function renderIdxModal() {{
            document.getElementById('modal-font-name').innerText = idxState.name;
            const htmlCode = document.getElementById('modal-html');
            const cssCode = document.getElementById('modal-css');
            const copyBtn = document.getElementById('copy-html-btn');
            
            // Render Import
            if (!idxState.url || idxState.url === "") {{
                htmlCode.innerHTML = '<span class="font-sans font-medium text-emerald-400 select-none">✨ System font. Pre-installed on all devices. No import required!</span>';
                copyBtn.style.display = 'none';
            }} else {{
                copyBtn.style.display = 'block';
                if (idxState.impMode === 'html') {{
                    htmlCode.textContent = `<link rel="preconnect" href="https://fonts.googleapis.com">\\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\\n<link href="${{idxState.url}}" rel="stylesheet">`;
                }} else {{
                    htmlCode.textContent = `@import url('${{idxState.url}}');`;
                }}
            }}
            
            // Render CSS
            if (idxState.cssMode === 'vanilla') {{
                cssCode.textContent = `font-family: ${{idxState.css}};`;
            }} else {{
                const safeName = idxState.name.replace(/\\s+/g, '').toLowerCase();
                cssCode.textContent = `// tailwind.config.js\\nmodule.exports = {{\\n  theme: {{\\n    extend: {{\\n      fontFamily: {{\\n        '${{safeName}}': [${{idxState.css}}]\\n      }}\\n    }}\\n  }}\\n}}`;
            }}
        }}

        function idxToggleImport(mode) {{
            idxState.impMode = mode;
            const btnHtml = document.getElementById('idx-btn-html');
            const btnCss = document.getElementById('idx-btn-css');
            if(mode === 'html') {{
                btnHtml.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-indigo-600 transition";
                btnCss.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition";
            }} else {{
                btnCss.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-indigo-600 transition";
                btnHtml.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition";
            }}
            renderIdxModal();
        }}

        function idxToggleCss(mode) {{
            idxState.cssMode = mode;
            const btnVan = document.getElementById('idx-btn-vanilla');
            const btnTw = document.getElementById('idx-btn-tailwind');
            if(mode === 'vanilla') {{
                btnVan.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-emerald-600 transition";
                btnTw.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition";
            }} else {{
                btnTw.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-emerald-600 transition";
                btnVan.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition";
            }}
            renderIdxModal();
        }}

        function openFontModal() {{
            renderIdxModal();
            const modal = document.getElementById('code-modal');
            const modalContent = document.getElementById('modal-content');
            modal.classList.remove('hidden');
            void modal.offsetWidth; 
            modal.classList.remove('opacity-0');
            modalContent.classList.remove('scale-95');
            modalContent.classList.add('scale-100');
        }}
        
        function closeModal(id) {{ 
            const modal = document.getElementById(id);
            const modalContent = document.getElementById('modal-content');
            modal.classList.add('opacity-0');
            modalContent.classList.remove('scale-100');
            modalContent.classList.add('scale-95');
            setTimeout(() => modal.classList.add('hidden'), 300); 
        }}
        
        function triggerToast() {{
            const t = document.getElementById('toast'); 
            t.classList.remove('hidden'); 
            void t.offsetWidth;
            t.classList.remove('opacity-0', 'translate-y-4');
            setTimeout(() => {{ 
                t.classList.add('opacity-0', 'translate-y-4'); 
                setTimeout(() => t.classList.add('hidden'), 300); 
            }}, 3000);
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
    with open("index.html", 'w', encoding='utf-8') as f: f.write(home_html)

    # 5. GENERATE GUIDES
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
{footer_html}
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
    <div class="bg-white border-b border-slate-200 overflow-hidden relative">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-50/50 via-white to-white"></div>
        <div class="max-w-7xl mx-auto px-6 pt-10 pb-12 md:pt-12 md:pb-16 relative z-10 text-center">
            <h1 class="text-4xl md:text-5xl font-black tracking-tight text-slate-900 mb-4">
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Font Guides</span>
            </h1>
            <p class="text-lg text-slate-500 font-medium leading-relaxed max-w-2xl mx-auto mt-4 mb-8">Master CSS typography and build better web interfaces with our deep-dive technical tutorials.</p>
        </div>
    </div>
    
    <main class="flex-grow py-12 px-6 max-w-7xl mx-auto w-full">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {guides_cards_html}
        </div>
    </main>
{footer_html}
</body>
</html>"""
    with open("html-css-font-guides.html", 'w', encoding='utf-8') as f: f.write(guides_page_html)

    # 6. GENERATE EDITOR'S DESK PAGINATION
    print("Generating Editor's Desk Pagination...")
    posts_per_page = 10
    total_pages = math.ceil(len(history) / posts_per_page) if len(history) > 0 else 1

    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * posts_per_page
        end_idx = start_idx + posts_per_page
        current_posts = history[start_idx:end_idx]

        posts_html = ""
        for post in current_posts:
            if not isinstance(post, dict): continue
            
            css_raw = post.get('css_snippet', '')
            if isinstance(css_raw, dict) or isinstance(css_raw, list): 
                css_raw = json.dumps(css_raw, indent=2)
            elif not isinstance(css_raw, str): 
                css_raw = str(css_raw)
            safe_css = html.escape(css_raw)
            
            title_raw = post.get('title', 'Typography Tip')
            if not isinstance(title_raw, str): title_raw = str(title_raw)
            
            tip_raw = post.get('tip', '')
            if not isinstance(tip_raw, str): tip_raw = str(tip_raw)
            
            date_raw = post.get('date', 'Recent')
            if not isinstance(date_raw, str): date_raw = str(date_raw)
            
            posts_html += f"""
            <article class="bg-white p-8 md:p-10 rounded-[2rem] shadow-sm border border-slate-200 mb-8 relative overflow-hidden group">
                <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-violet-500 opacity-50 group-hover:opacity-100 transition-opacity"></div>
                <div class="flex items-center justify-between mb-4">
                    <span class="text-[10px] font-black text-indigo-500 uppercase tracking-widest">{date_raw}</span>
                </div>
                <h2 class="text-2xl font-black text-slate-900 mb-4 leading-snug">{title_raw}</h2>
                <p class="text-slate-600 font-medium leading-relaxed mb-6">{tip_raw}</p>
                <div class="bg-slate-900 rounded-xl p-4 relative">
                    <pre class="w-full m-0 overflow-x-auto custom-scrollbar"><code class="text-[11px] md:text-xs font-mono text-emerald-400 block whitespace-pre-wrap">{safe_css}</code></pre>
                </div>
            </article>"""

        # Pagination Controls
        prev_link = ""
        next_link = ""
        
        if page_num > 1:
            prev_url = "editors-desk.html" if page_num == 2 else f"editors-desk-{page_num-1}.html"
            prev_link = f'<a href="/{prev_url}" class="bg-white border border-slate-200 text-slate-700 hover:border-indigo-300 hover:text-indigo-600 font-bold text-xs uppercase tracking-widest px-6 py-3 rounded-xl transition shadow-sm">&larr; Newer Posts</a>'
        else:
            prev_link = '<div></div>'
            
        if page_num < total_pages:
            next_url = f"editors-desk-{page_num+1}.html"
            next_link = f'<a href="/{next_url}" class="bg-white border border-slate-200 text-slate-700 hover:border-indigo-300 hover:text-indigo-600 font-bold text-xs uppercase tracking-widest px-6 py-3 rounded-xl transition shadow-sm">Older Posts &rarr;</a>'
        else:
            next_link = '<div></div>'

        pagination_html = f"""
        <div class="flex items-center justify-between mt-12 pt-8 border-t border-slate-200">
            {prev_link}
            <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Page {page_num} of {total_pages}</span>
            {next_link}
        </div>"""

        file_name = "editors-desk.html" if page_num == 1 else f"editors-desk-{page_num}.html"

        editors_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editor's Desk - Page {page_num} | htmlfonts</title>
    <meta name="description" content="Daily CSS typography tips, UI design tricks, and code snippets.">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
{GA_CODE}
    <script src="{TAILWIND}"></script>
    <style>
        body {{ font-family: system-ui, sans-serif; }}
        .custom-scrollbar::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        .custom-scrollbar::-webkit-scrollbar-track {{ background: #0f172a; border-radius: 8px; }}
        .custom-scrollbar::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 8px; }}
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
    </style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col selection:bg-indigo-200 selection:text-indigo-900">
{header_html}
    <div class="bg-white border-b border-slate-200 overflow-hidden relative">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-50/50 via-white to-white"></div>
        <div class="max-w-7xl mx-auto px-6 pt-10 pb-12 md:pt-12 md:pb-16 relative z-10 text-center">
            <span class="inline-block bg-indigo-50 border border-indigo-100 text-indigo-700 text-[10px] font-black px-4 py-2 rounded-full uppercase tracking-[0.2em] mb-4 shadow-sm">Daily Updates</span>
            <h1 class="text-4xl md:text-5xl font-black tracking-tight text-slate-900 mb-4">
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Editor's Desk</span>
            </h1>
            <p class="text-lg text-slate-500 font-medium leading-relaxed max-w-2xl mx-auto mt-4 mb-8">Bite-sized CSS typography tips, UI design tricks, and code snippets delivered daily.</p>
        </div>
    </div>
    
    <main class="flex-grow py-12 px-6 max-w-3xl mx-auto w-full">
        {posts_html}
        {pagination_html}
    </main>
{footer_html}
</body>
</html>"""
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(editors_page_html)
        
        sitemap += f"  <url><loc>{DOMAIN}/{file_name}</loc><changefreq>daily</changefreq><priority>0.9</priority></url>\n"

    # 7. GENERATE COMPARISONS
    print("Generating Font Comparisons...")
    
    # Pre-generate the "Most Searched Comparisons" grid links BEFORE building the individual pages
    comparison_grid_links = ""
    for font_a, font_b, css_a, css_b, link_a, link_b in top_comparisons:
        slug = f"{font_a.lower().replace(' ', '-')}-vs-{font_b.lower().replace(' ', '-')}"
        comparison_grid_links += f'                <a href="/compare/{slug}.html" class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-indigo-300 transition-all font-bold text-sm text-slate-700 hover:text-indigo-600 text-center">{font_a} vs {font_b}</a>\n'

    for font_a, font_b, css_a, css_b, link_a, link_b in top_comparisons:
        type_a = next((f['type'] for f in master_fonts if f['name'] == font_a), 'Sans-Serif')
        type_b = next((f['type'] for f in master_fonts if f['name'] == font_b), 'Sans-Serif')

        slug = f"{font_a.lower().replace(' ', '-')}-vs-{font_b.lower().replace(' ', '-')}"
        imp_a = f"<link href='{GFONTS}?family={link_a}&display=swap' rel='stylesheet'>" if link_a else ""
        imp_b = f"<link href='{GFONTS}?family={link_b}&display=swap' rel='stylesheet'>" if link_b else ""

        sys_msg = '<span class="font-sans font-medium text-emerald-400 select-none">✨ Web-safe system font. Pre-installed on all devices for zero-latency loading. No HTML import required!</span>'
        html_a = imp_a if imp_a else sys_msg
        html_b = imp_b if imp_b else sys_msg

        safe_ha = html_a.replace("'", "\\'").replace('"', '&quot;')
        safe_hb = html_b.replace("'", "\\'").replace('"', '&quot;')
        safe_link_a = link_a if link_a else ""
        safe_link_b = link_b if link_b else ""

        cache_key = f"{font_a}_vs_{font_b}"
        seo_description = f"<h2 class='text-2xl font-black text-slate-900 mb-4'>The Difference Between {font_a} and {font_b}</h2><p class='mb-4 leading-relaxed'>Compare the typography of {font_a} and {font_b}.</p>"
        
        if cache_key in seo_cache:
            seo_description = seo_cache[cache_key]
        elif api_exhausted or not os.environ.get("GEMINI_API_KEY"):
            pass 
        else:
            print(f"Generating comparison description: {font_a} vs {font_b}...")
            desc_prompt = f"""You are a master SEO copywriter and expert UI typographer. Write an incredible, highly engaging comparison between {font_a} vs {font_b} specifically targeting the most searched Google queries (e.g., '{font_a} vs {font_b} differences', 'which is better {font_a} or {font_b}?', '{font_a} vs {font_b} history'). 

            Your response must include:
            1. A fascinating short history of both fonts.
            2. The key geometric and design differences.
            3. A legibility analysis for web and mobile UI.
            4. The best use cases for each font.

            Return ONLY raw HTML. Structure it with an <h2 class='text-2xl font-black text-slate-900 mb-6'> for the main title, <h3 class='text-xl font-bold text-slate-800 mt-8 mb-4'> for section subtitles, and <p class='mb-5 text-slate-600 leading-relaxed'> for the paragraphs. Do not use markdown blocks."""
            
            for attempt in range(3):
                try:
                    time.sleep(6) 
                    resp = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=desc_prompt)
                    seo_description = resp.text.replace('```html', '').replace('```', '').strip()
                    seo_cache[cache_key] = seo_description
                    save_cache()
                    print(f"✅ Success: {font_a} vs {font_b}")
                    break
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str:
                        if "GenerateRequestsPerDay" in err_str or "limit: 20" in err_str:
                            print(f"🚨 Daily Limit Reached during {font_a} vs {font_b}! Stopping API calls.")
                            api_exhausted = True
                            break
                        elif attempt < 2:
                            print(f"⏳ Rate limit hit. Waiting 65 seconds...")
                            time.sleep(65)
                        else:
                            api_exhausted = True
                    else:
                        break

        vs_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
        .comparison-text {{ transition: font-size 0.2s ease, font-weight 0.2s ease, line-height 0.2s ease, letter-spacing 0.2s ease; }}
        option {{ background-color: #ffffff; color: #0f172a; }}
    </style>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen flex flex-col font-sans selection:bg-indigo-200 selection:text-indigo-900">
    <div id="toast" class="fixed bottom-10 left-1/2 transform -translate-x-1/2 hidden bg-emerald-500 text-white px-8 py-4 rounded-2xl shadow-2xl z-[100] text-sm font-black uppercase flex items-center gap-3">
        <span>CSS Code Copied! 🚀</span>
    </div>
{header_html}
    <div class="bg-white border-b border-slate-200 overflow-hidden relative">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-50/50 via-white to-white"></div>
        <div class="max-w-7xl mx-auto px-6 pt-10 pb-12 md:pt-12 md:pb-16 relative z-10 text-center">
            <h1 class="text-4xl md:text-5xl font-black tracking-tight text-slate-900 mb-4">
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">{font_a} vs {font_b}</span>
            </h1>
            <p class="text-lg text-slate-500 font-medium leading-relaxed max-w-2xl mx-auto mt-4 mb-8">Compare legibility and design aesthetics side-by-side.</p>
        </div>
    </div>
    
    <main class="flex-grow w-full pb-24 px-6 max-w-7xl mx-auto relative z-20 -mt-8 md:-mt-12">
        <div class="text-center mb-8 max-w-3xl mx-auto">
            <a href="/font-vs-font-comparison-tool.html" class="text-indigo-600 font-bold text-xs uppercase tracking-widest hover:text-indigo-800 transition">&larr; Back to Full Tool</a>
        </div>
        
        <div class="bg-white rounded-3xl p-4 md:p-8 shadow-xl border border-slate-200/60 mb-6 md:mb-10">
            
            <div class="mb-8">
                <label class="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3">Testing Copy</label>
                <input type="text" id="vs-text" value="Optimize your UI design with fast-loading free web fonts." 
                    onfocus="if(this.value==='Optimize your UI design with fast-loading free web fonts.') this.value='';" 
                    onblur="if(this.value==='') {{ this.value='Optimize your UI design with fast-loading free web fonts.'; u(); }}"
                    oninput="u()"
                    class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 md:px-5 md:py-4 outline-none text-base md:text-lg font-medium text-slate-800 focus:ring-2 focus:ring-indigo-500 transition-all">
                
                <div class="flex flex-wrap gap-2 mt-3">
                    <button onclick="setTxt('Optimize your UI design with fast-loading free web fonts.')" class="bg-slate-100 hover:bg-slate-200 text-slate-600 text-[10px] font-bold px-3 py-1.5 rounded-lg uppercase tracking-wider transition">UI Copy</button>
                    <button onclick="setTxt('The quick brown fox jumps over the lazy dog.')" class="bg-slate-100 hover:bg-slate-200 text-slate-600 text-[10px] font-bold px-3 py-1.5 rounded-lg uppercase tracking-wider transition">Pangram</button>
                    <button onclick="setTxt('ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz')" class="bg-slate-100 hover:bg-slate-200 text-slate-600 text-[10px] font-bold px-3 py-1.5 rounded-lg uppercase tracking-wider transition">Alphabet</button>
                    <button onclick="setTxt('0123456789 !@#$%^&*()_+-=[]{{}}|;:,.<>?/')" class="bg-slate-100 hover:bg-slate-200 text-slate-600 text-[10px] font-bold px-3 py-1.5 rounded-lg uppercase tracking-wider transition">Characters</button>
                </div>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 md:gap-4">
                <div class="bg-slate-50 rounded-xl p-3 md:p-4 border border-slate-100">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Size</span>
                        <span id="lbl-size" class="text-indigo-600 font-bold text-xs">32px</span>
                    </div>
                    <input type="range" id="vs-font-size" min="12" max="120" value="32" oninput="u()" class="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600">
                </div>
                
                <div class="bg-slate-50 rounded-xl p-3 md:p-4 border border-slate-100">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Line Height</span>
                        <span id="lbl-lh" class="text-indigo-600 font-bold text-xs">1.5</span>
                    </div>
                    <input type="range" id="vs-lh" min="1.0" max="2.5" step="0.1" value="1.5" oninput="u()" class="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600">
                </div>

                <div class="bg-slate-50 rounded-xl p-3 md:p-4 border border-slate-100">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Tracking</span>
                        <span id="lbl-ls" class="text-indigo-600 font-bold text-xs">0em</span>
                    </div>
                    <input type="range" id="vs-ls" min="-0.10" max="0.30" step="0.01" value="0" oninput="u()" class="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600">
                </div>

                <div class="flex items-center justify-center bg-slate-50 rounded-xl p-3 md:p-4 border border-slate-100 cursor-pointer hover:bg-slate-100 transition" onclick="toggleDarkMode()">
                    <div class="flex flex-col items-center">
                        <svg class="w-5 h-5 text-slate-600 mb-1" id="icon-light" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>
                        <span id="lbl-dark" class="text-[10px] font-black text-slate-500 uppercase tracking-widest text-center">Dark Mode</span>
                    </div>
                </div>

                <div id="btn-xray" class="col-span-2 md:col-span-1 flex items-center justify-center bg-slate-50 rounded-xl p-3 md:p-4 border border-slate-100 cursor-pointer hover:bg-slate-100 transition relative overflow-hidden" onclick="toggleXRay()">
                    <div class="flex flex-col items-center z-10 relative">
                        <svg class="w-5 h-5 text-slate-600 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                        <span id="lbl-xray" class="text-[10px] font-black text-slate-500 uppercase tracking-widest text-center">X-Ray Off</span>
                    </div>
                </div>
            </div>
        </div>

        <div id="xray-arena" class="hidden relative w-full min-h-[250px] md:min-h-[400px] bg-white rounded-3xl border border-slate-200 shadow-inner overflow-hidden mb-10 p-6 md:p-10 flex items-center justify-center transition-colors">
            <div class="absolute inset-0 bg-[radial-gradient(#e2e8f0_1px,transparent_1px)] [background-size:16px_16px] opacity-50 pointer-events-none" id="xray-bg-pattern"></div>
            <div class="relative w-full max-w-4xl flex justify-center text-center items-center z-10">
                <p id="xray-preview-a" class="absolute comparison-text break-words w-full top-1/2 -translate-y-1/2 left-0"></p>
                <p id="xray-preview-b" class="absolute comparison-text break-words w-full top-1/2 -translate-y-1/2 left-0"></p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8 transition-all items-start" id="compare-grid">
            <div class="bg-white p-4 md:p-6 rounded-[2rem] shadow-sm border border-slate-200 flex flex-col transition-colors" id="panel-a">
                <div class="flex flex-col sm:flex-row gap-2 mb-4 md:mb-6 items-center justify-between">
                    <div class="flex items-center">
                        <span class="bg-indigo-600 text-white text-[10px] font-black px-2 py-1 rounded-md shadow-lg shadow-indigo-200 uppercase mr-3">A</span>
                        <h3 id="title-a" class="text-2xl font-black text-slate-800 transition-colors">{font_a}</h3>
                    </div>
                    <select id="vs-weight-a" onchange="u()" class="w-full sm:w-32 bg-slate-50 px-4 py-3 rounded-xl border border-slate-200 font-bold text-slate-600 text-sm outline-none cursor-pointer hover:border-slate-300 transition-colors"></select>
                </div>
                <div id="wrap-a" class="w-full flex items-center p-4 md:p-6 min-h-[100px] bg-indigo-50/20 rounded-2xl border border-indigo-100/50 transition-colors overflow-hidden relative">
                    <p id="vs-preview-a" class="comparison-text break-words w-full text-slate-900"></p>
                </div>
                <button onclick="openModalFromVS('a')" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-black uppercase tracking-widest py-3 md:py-4 rounded-xl transition shadow-lg shadow-indigo-200 mt-4 md:mt-6 group flex justify-center items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                    Copy HTML / CSS
                </button>
            </div>

            <div class="bg-white p-4 md:p-6 rounded-[2rem] shadow-sm border border-slate-200 flex flex-col transition-colors" id="panel-b">
                <div class="flex flex-col sm:flex-row gap-2 mb-4 md:mb-6 items-center justify-between">
                    <div class="flex items-center">
                        <span class="bg-violet-600 text-white text-[10px] font-black px-2 py-1 rounded-md shadow-lg shadow-violet-200 uppercase mr-3">B</span>
                        <h3 id="title-b" class="text-2xl font-black text-slate-800 transition-colors">{font_b}</h3>
                    </div>
                    <select id="vs-weight-b" onchange="u()" class="w-full sm:w-32 bg-slate-50 px-4 py-3 rounded-xl border border-slate-200 font-bold text-slate-600 text-sm outline-none cursor-pointer hover:border-slate-300 transition-colors"></select>
                </div>
                <div id="wrap-b" class="w-full flex items-center p-4 md:p-6 min-h-[100px] bg-violet-50/20 rounded-2xl border border-violet-100/50 transition-colors overflow-hidden relative">
                    <p id="vs-preview-b" class="comparison-text break-words w-full text-slate-900"></p>
                </div>
                <button onclick="openModalFromVS('b')" class="w-full bg-violet-600 hover:bg-violet-700 text-white text-xs font-black uppercase tracking-widest py-3 md:py-4 rounded-xl transition shadow-lg shadow-violet-100 mt-4 md:mt-6 group flex justify-center items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                    Copy HTML / CSS
                </button>
            </div>
        </div>

        <div class="mt-12 bg-white p-8 md:p-12 rounded-3xl shadow-[0_20px_50px_rgb(0,0,0,0.05)] border border-slate-100 text-slate-600">
            {seo_description}
        </div>
        
        <div class="border-t border-slate-200 pt-16 mt-24">
            <h2 class="text-3xl font-black text-slate-900 mb-8 text-center tracking-tight">Most Searched Comparisons</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
{comparison_grid_links}
            </div>
        </div>
    </main>
    
    <div id="code-modal" class="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4 transition-opacity duration-300 opacity-0">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-2xl p-6 md:p-8 relative transform scale-95 transition-all duration-300" id="modal-content">
            <button onclick="closeModal('code-modal')" class="absolute top-4 right-4 md:top-6 md:right-6 text-slate-400 hover:text-slate-900 bg-slate-50 hover:bg-slate-100 rounded-full p-2 transition">✕</button>
            
            <h3 class="text-2xl md:text-3xl font-black text-slate-900 tracking-tighter mb-2" id="modal-font-name">Font Detail</h3>
            <p class="text-slate-500 text-xs md:text-sm font-medium mb-6">Production-ready code generated from your slider settings.</p>
            
            <div class="space-y-6">
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">1. Import Font</label>
                        <div class="flex bg-slate-100 p-1 rounded-lg">
                            <button onclick="toggleImportMode('html')" id="btn-imp-html" class="text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-indigo-600 transition">HTML &lt;link&gt;</button>
                            <button onclick="toggleImportMode('css')" id="btn-imp-css" class="text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition">CSS @import</button>
                        </div>
                    </div>
                    <div class="bg-slate-900 rounded-xl p-4 relative group min-h-[80px] flex items-center">
                        <code id="modal-html" class="text-[11px] md:text-xs text-indigo-300 font-mono break-all block whitespace-pre-wrap"></code>
                        <button id="copy-html-btn" onclick="copyElementText('modal-html')" class="absolute top-3 right-3 text-[10px] font-bold text-white bg-indigo-600 hover:bg-indigo-500 px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition shadow-md">COPY</button>
                    </div>
                </div>

                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2">2. Apply CSS <span class="bg-emerald-500 text-white px-1.5 py-0.5 rounded-full text-[7px] hidden md:inline-block">FLUID CLAMP()</span></label>
                        <div class="flex bg-slate-100 p-1 rounded-lg">
                            <button onclick="toggleCSSMode('vanilla')" id="btn-css-vanilla" class="text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-emerald-600 transition">Vanilla CSS</button>
                            <button onclick="toggleCSSMode('tailwind')" id="btn-css-tailwind" class="text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition">Tailwind</button>
                        </div>
                    </div>
                    <div class="bg-slate-900 rounded-xl p-4 relative group border-2 border-emerald-500/30 min-h-[120px] flex items-center">
                        <pre class="w-full m-0"><code id="modal-css" class="text-[11px] md:text-xs font-mono text-emerald-400 block whitespace-pre-wrap leading-relaxed w-full"></code></pre>
                        <button onclick="copyElementText('modal-css')" class="absolute top-3 right-3 text-[10px] font-bold text-white bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition shadow-md">COPY</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

{footer_html}

    <script>
        let fontsRaw = {json.dumps(master_fonts)};
        let isDark = false;
        let isXray = false;
        let importMode = 'html'; 
        let cssMode = 'vanilla'; 
        
        let activeModalData = {{
            name: '', link: '', cssObj: '', type: '', weight: '400', 
            sz: 32, lh: '1.5', ls: '0'
        }};

        let vsData = {{ a: null, b: null }};
        const loadedFonts = new Set();
        let loadedCount = 0; 

        function getFallbackStack(type) {{
            if (type === 'Sans-Serif') return "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif";
            if (type === 'Serif') return "Georgia, Cambria, 'Times New Roman', Times, serif";
            if (type === 'Monospace') return "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace";
            return "system-ui, sans-serif"; 
        }}

        function loadFont(link, callback) {{
            if (!link || loadedFonts.has(link)) {{
                if(callback) callback();
                return;
            }}
            const el = document.createElement('link'); 
            el.rel = "stylesheet"; 
            el.href = `https://fonts.googleapis.com/css2?family=${{link}}&display=swap`;
            el.onload = () => {{ loadedFonts.add(link); if(callback) callback(); }};
            document.head.appendChild(el); 
        }}

        function setTxt(txt) {{
            document.getElementById('vs-text').value = txt;
            u();
        }}

        function toggleDarkMode() {{
            isDark = !isDark;
            const wrapA = document.getElementById('wrap-a');
            const wrapB = document.getElementById('wrap-b');
            const panelA = document.getElementById('panel-a');
            const panelB = document.getElementById('panel-b');
            const titleA = document.getElementById('title-a');
            const titleB = document.getElementById('title-b');
            const weightA = document.getElementById('vs-weight-a');
            const weightB = document.getElementById('vs-weight-b');
            const pa = document.getElementById('vs-preview-a');
            const pb = document.getElementById('vs-preview-b');
            const lbl = document.getElementById('lbl-dark');
            
            if(isDark) {{
                // Remove Light Mode Styles
                wrapA.classList.replace('bg-indigo-50/20', 'bg-slate-900');
                wrapA.classList.replace('border-indigo-100/50', 'border-slate-700');
                wrapB.classList.replace('bg-violet-50/20', 'bg-slate-900');
                wrapB.classList.replace('border-violet-100/50', 'border-slate-700');
                
                panelA.classList.replace('bg-white', 'bg-slate-800');
                panelA.classList.replace('border-slate-200', 'border-slate-700');
                panelB.classList.replace('bg-white', 'bg-slate-800');
                panelB.classList.replace('border-slate-200', 'border-slate-700');
                
                titleA.classList.replace('text-slate-800', 'text-white');
                titleB.classList.replace('text-slate-800', 'text-white');
                
                weightA.classList.replace('bg-slate-50', 'bg-slate-800');
                weightA.classList.replace('border-slate-200', 'border-slate-700');
                weightA.classList.replace('text-slate-600', 'text-white');
                
                weightB.classList.replace('bg-slate-50', 'bg-slate-800');
                weightB.classList.replace('border-slate-200', 'border-slate-700');
                weightB.classList.replace('text-slate-600', 'text-white');
                
                pa.classList.replace('text-slate-900', 'text-white');
                pb.classList.replace('text-slate-900', 'text-white');
                lbl.innerText = "Light Mode";
            }} else {{
                // Remove Dark Mode Styles
                wrapA.classList.replace('bg-slate-900', 'border-slate-700');
                wrapB.classList.replace('bg-slate-900', 'border-slate-700');
                panelA.classList.replace('bg-slate-800', 'border-slate-700');
                panelB.classList.replace('bg-slate-800', 'border-slate-700');
                
                titleA.classList.replace('text-white', 'text-slate-800');
                titleB.classList.replace('text-white', 'text-slate-800');
                
                weightA.classList.replace('bg-slate-800', 'bg-slate-50');
                weightA.classList.replace('border-slate-700', 'border-slate-200');
                weightA.classList.replace('text-white', 'text-slate-600');
                
                weightB.classList.replace('bg-slate-800', 'bg-slate-50');
                weightB.classList.replace('border-slate-700', 'border-slate-200');
                weightB.classList.replace('text-white', 'text-slate-600');
                
                pa.classList.replace('text-white', 'text-slate-900');
                pb.classList.replace('text-white', 'text-slate-900');
                lbl.innerText = "Dark Mode";
            }}
            u();
        }}
        
        function toggleXRay() {{
            isXray = !isXray;
            const grid = document.getElementById('compare-grid');
            const xrayArena = document.getElementById('xray-arena');
            const btn = document.getElementById('btn-xray');
            const lbl = document.getElementById('lbl-xray');

            if(isXray) {{
                grid.classList.add('hidden');
                xrayArena.classList.remove('hidden');
                btn.classList.add('bg-indigo-100', 'border-indigo-300');
                lbl.innerText = "X-Ray On";
            }} else {{
                grid.classList.remove('hidden');
                xrayArena.classList.add('hidden');
                btn.classList.remove('bg-indigo-100', 'border-indigo-300');
                lbl.innerText = "X-Ray Off";
            }}
            u();
        }}

        function parseWeights(link) {{
            if (!link) return ['400', '700'];
            const match = link.match(/wght@([\\d;]+)/);
            if (match) return match[1].split(';');
            return ['400']; 
        }}

        function populateWeights(selectId, fontObj) {{
            const sel = document.getElementById(selectId);
            const currentVal = sel.value; 
            sel.innerHTML = '';
            
            const weightNames = {{ '100':'Thin', '200':'ExtraLight', '300':'Light', '400':'Regular', '500':'Medium', '600':'SemiBold', '700':'Bold', '800':'ExtraBold', '900':'Black' }};
            
            const weights = parseWeights(fontObj.link);
            weights.forEach(w => {{
                let label = weightNames[w] ? `${{w}} (${{weightNames[w]}})` : w;
                sel.add(new Option(label, w));
            }});
            
            if (weights.includes(currentVal)) sel.value = currentVal;
            else if (weights.includes('400')) sel.value = '400';
            else sel.selectedIndex = 0;
        }}

        function initVSTool() {{
            const sA = document.getElementById('vs-font-a'); 
            const sB = document.getElementById('vs-font-b');
            
            fontsRaw.forEach((f, i) => {{ 
                sA.add(new Option(f.name, i)); 
                sB.add(new Option(f.name, i)); 
            }});
            
            let interIdx = fontsRaw.findIndex(f => f.name === "Inter");
            let robotoIdx = fontsRaw.findIndex(f => f.name === "Roboto");
            sA.selectedIndex = interIdx !== -1 ? interIdx : 0;
            sB.selectedIndex = robotoIdx !== -1 ? robotoIdx : 1;

            const checkAndDraw = () => {{
                loadedCount++;
                if (loadedCount >= 2) {{ u(); loadedCount = 0; }}
            }};

            sA.onchange = () => {{
                vsData.a = fontsRaw[sA.value];
                populateWeights('vs-weight-a', vsData.a);
                loadFont(vsData.a.link, () => {{ u(); }});
            }};
            
            sB.onchange = () => {{
                vsData.b = fontsRaw[sB.value];
                populateWeights('vs-weight-b', vsData.b);
                loadFont(vsData.b.link, () => {{ u(); }});
            }};
            
            // Initialization Trigger
            vsData.a = fontsRaw[sA.value];
            vsData.b = fontsRaw[sB.value];
            populateWeights('vs-weight-a', vsData.a);
            populateWeights('vs-weight-b', vsData.b);
            loadFont(vsData.a.link, checkAndDraw);
            loadFont(vsData.b.link, checkAndDraw);
        }}

        function u() {{
            if (!vsData.a || !vsData.b) return;

            const text = document.getElementById('vs-text').value;
            const sz = document.getElementById('vs-font-size').value;
            const lh = document.getElementById('vs-lh').value;
            const ls = document.getElementById('vs-ls').value;
            
            document.getElementById('lbl-size').innerText = sz + 'px';
            document.getElementById('lbl-lh').innerText = lh;
            document.getElementById('lbl-ls').innerText = ls + 'em';
            
            const wA = document.getElementById('vs-weight-a').value || '400';
            const wB = document.getElementById('vs-weight-b').value || '400';
            
            const txtColor = isDark ? '#ffffff' : '#0f172a';

            if (!isXray) {{
                const pA = document.getElementById('vs-preview-a');
                pA.style.color = txtColor;
                pA.style.fontFamily = vsData.a.css;
                pA.style.fontSize = sz + 'px';
                pA.style.fontWeight = wA;
                pA.style.lineHeight = lh;
                pA.style.letterSpacing = ls + 'em';
                pA.innerText = text;

                const pB = document.getElementById('vs-preview-b');
                pB.style.color = txtColor;
                pB.style.fontFamily = vsData.b.css;
                pB.style.fontSize = sz + 'px';
                pB.style.fontWeight = wB;
                pB.style.lineHeight = lh;
                pB.style.letterSpacing = ls + 'em';
                pB.innerText = text;
            }} 
            else {{
                const xa = document.getElementById('xray-preview-a');
                const xb = document.getElementById('xray-preview-b');
                const arena = document.getElementById('xray-arena');
                
                if (isDark) {{
                    arena.classList.replace('bg-white', 'bg-slate-900');
                    xa.style.mixBlendMode = 'screen';
                    xb.style.mixBlendMode = 'screen';
                    xa.style.color = '#0ff'; // Bright Cyan
                    xb.style.color = '#f0f'; // Bright Magenta
                }} else {{
                    arena.classList.replace('bg-slate-900', 'bg-white');
                    xa.style.mixBlendMode = 'multiply';
                    xb.style.mixBlendMode = 'multiply';
                    xa.style.color = '#0ea5e9'; // Sky
                    xb.style.color = '#f43f5e'; // Rose
                }}

                xa.style.fontFamily = vsData.a.css;
                xa.style.fontSize = sz + 'px';
                xa.style.fontWeight = wA;
                xa.style.lineHeight = lh;
                xa.style.letterSpacing = ls + 'em';
                xa.innerText = text;

                xb.style.fontFamily = vsData.b.css;
                xb.style.fontSize = sz + 'px';
                xb.style.fontWeight = wB;
                xb.style.lineHeight = lh;
                xb.style.letterSpacing = ls + 'em';
                xb.innerText = text;
            }}
        }}

        function updateModalDisplay() {{
            const htmlCode = document.getElementById('modal-html');
            if (activeModalData.link) {{
                if (importMode === 'html') {{
                    htmlCode.textContent = `<link rel="preconnect" href="https://fonts.googleapis.com">\\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\\n<link href="https://fonts.googleapis.com/css2?family=${{activeModalData.link}}&display=swap" rel="stylesheet">`;
                }} else {{
                    htmlCode.textContent = `@import url('https://fonts.googleapis.com/css2?family=${{activeModalData.link}}&display=swap');`;
                }}
                document.getElementById('copy-html-btn').style.display = 'block';
            }} else {{
                htmlCode.innerHTML = `<span class="font-sans font-medium text-emerald-400 select-none">✨ System Font. No import required!</span>`;
                document.getElementById('copy-html-btn').style.display = 'none';
            }}

            const fontStack = `"${{activeModalData.name}}", ${{getFallbackStack(activeModalData.type)}}`;
            const cssEl = document.getElementById('modal-css');
            
            let minSize = Math.max(12, Math.round(activeModalData.sz * 0.6));
            let remMin = (minSize / 16).toFixed(3).replace(/\\.?0+$/, '');
            let remMax = (activeModalData.sz / 16).toFixed(3).replace(/\\.?0+$/, '');
            let fluidClamp = `clamp(${{remMin}}rem, 2vw + 0.5rem, ${{remMax}}rem)`;

            if (cssMode === 'vanilla') {{
                let cssBlock = `.pro-text {{\n`;
                cssBlock += `  font-family: ${{fontStack}};\n`;
                cssBlock += `  font-weight: ${{activeModalData.weight}};\n`;
                cssBlock += `  font-size: ${{fluidClamp}};\n`;
                cssBlock += `  line-height: ${{activeModalData.lh}};\n`;
                if (activeModalData.ls !== "0" && activeModalData.ls !== "0.00") cssBlock += `  letter-spacing: ${{activeModalData.ls}}em;\n`;
                cssBlock += `}}`;
                cssEl.textContent = cssBlock;
            }} else {{
                let safeName = activeModalData.name.replace(/\\s+/g, '-').toLowerCase();
                let twStr = `font-['${{activeModalData.name}}'] font-[${{activeModalData.weight}}] text-[${{fluidClamp}}] leading-[${{activeModalData.lh}}]`;
                if (activeModalData.ls !== "0" && activeModalData.ls !== "0.00") twStr += ` tracking-[${{activeModalData.ls}}em]`;
                cssEl.textContent = twStr;
            }}
        }}

        function toggleImportMode(mode) {{
            importMode = mode;
            const btnHtml = document.getElementById('btn-imp-html');
            const btnCss = document.getElementById('btn-imp-css');
            
            if (mode === 'html') {{
                btnHtml.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-indigo-600 transition";
                btnCss.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition";
            }} else {{
                btnCss.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-indigo-600 transition";
                btnHtml.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition";
            }}
            updateModalDisplay();
        }}

        function toggleCSSMode(mode) {{
            cssMode = mode;
            const btnVan = document.getElementById('btn-css-vanilla');
            const btnTw = document.getElementById('btn-css-tailwind');
            
            if (mode === 'vanilla') {{
                btnVan.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-emerald-600 transition";
                btnTw.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition";
            }} else {{
                btnTw.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded bg-white shadow-sm text-emerald-600 transition";
                btnVan.className = "text-[9px] font-black uppercase tracking-wider px-3 py-1 rounded text-slate-500 hover:text-slate-700 transition";
            }}
            updateModalDisplay();
        }}

        function openModalFromVS(side) {{ 
            const fontObj = side === 'a' ? vsData.a : vsData.b;
            
            activeModalData = {{
                name: fontObj.name,
                link: fontObj.link,
                cssObj: fontObj.css,
                type: fontObj.type,
                weight: document.getElementById(side === 'a' ? 'vs-weight-a' : 'vs-weight-b').value,
                sz: parseInt(document.getElementById('vs-font-size').value),
                lh: document.getElementById('vs-lh').value,
                ls: document.getElementById('vs-ls').value
            }};

            document.getElementById('modal-font-name').innerText = activeModalData.name + ' (' + activeModalData.weight + ')';
            
            updateModalDisplay();
            
            const modal = document.getElementById('code-modal');
            const modalContent = document.getElementById('modal-content');
            modal.classList.remove('hidden');
            void modal.offsetWidth;
            modal.classList.remove('opacity-0');
            modalContent.classList.remove('scale-95');
            modalContent.classList.add('scale-100');
        }}

        function closeModal(id) {{ 
            const modal = document.getElementById(id);
            const modalContent = document.getElementById('modal-content');
            modal.classList.add('opacity-0');
            modalContent.classList.remove('scale-100');
            modalContent.classList.add('scale-95');
            setTimeout(() => modal.classList.add('hidden'), 300); 
        }}
        
        function triggerToast(msg = "Copied! 🚀") {{
            const t = document.getElementById('toast'); 
            t.classList.remove('hidden'); 
            void t.offsetWidth;
            t.classList.remove('opacity-0', 'translate-y-4');
            setTimeout(() => {{ 
                t.classList.add('opacity-0', 'translate-y-4'); 
                setTimeout(() => t.classList.add('hidden'), 300); 
            }}, 3000);
        }}
        
        function copyElementText(id) {{
            const txt = document.getElementById(id).textContent;
            navigator.clipboard.writeText(txt).then(() => triggerToast()).catch(() => {{
                const el = document.createElement('textarea'); el.value = txt; document.body.appendChild(el);
                el.select(); document.execCommand('copy'); document.body.removeChild(el); triggerToast();
            }});
        }}

        initVSTool();
    </script>
</body>
</html>
}
