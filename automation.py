import os
import json
import datetime
from google import genai
import tweepy

# 1. Setup Gemini
client_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. Daily Tip Generation
seo_prompt = """Generate a JSON object for htmlfonts.com. Target Keywords: Web Typography, CSS design. Keys MUST exactly match: "title", "slug", "tweet", "tip", "css_snippet"."""

try:
    response = client_gemini.models.generate_content(model='gemini-2.5-flash', contents=seo_prompt)
    raw_text = response.text.strip()
    if raw_text.startswith("```json"): 
        raw_text = raw_text[7:-3].strip()
    new_data = json.loads(raw_text)
    new_data["date"] = datetime.datetime.now().strftime("%B %d, %Y")
    
    # Save daily tip page
    os.makedirs('tips', exist_ok=True)
    with open(f"tips/{new_data['slug']}.html", 'w', encoding='utf-8') as f:
        f.write(f"<!DOCTYPE html><html><head><title>{new_data['title']} | htmlfonts.com</title><script src='[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)'></script></head><body class='bg-slate-50 p-6 md:p-12'><div class='max-w-3xl mx-auto'><a href='/' class='text-indigo-600 font-bold uppercase'>&larr; Back to Directory</a><h1 class='text-4xl font-bold mt-8'>{new_data['title']}</h1><p class='mt-4 text-lg text-slate-700'>{new_data['tip']}</p></div></body></html>")

    # Update Archives
    history = []
    if os.path.exists('history.json'):
        with open('history.json', 'r') as f: history = json.load(f)
    history.insert(0, new_data)
    with open('history.json', 'w') as f: json.dump(history, f, indent=4)
    with open('content.json', 'w') as f: json.dump(new_data, f, indent=4)

    # --- PROGRAMMATIC "VS" PAGE GENERATOR ---
    print("Generating SEO Comparison Pages...")
    os.makedirs('compare', exist_ok=True)
    
    # High-Volume Search Comparisons
    top_comparisons = [
        ("Arial", "Helvetica"), ("Inter", "Roboto"), ("Playfair Display", "Merriweather"),
        ("Open Sans", "Lato"), ("Montserrat", "Raleway"), ("Fira Code", "JetBrains Mono"),
        ("Oswald", "Bebas Neue"), ("Ubuntu", "Quicksand"), ("Lora", "PT Serif"), ("Nunito", "Poppins"),
        ("Roboto", "Open Sans"), ("Lato", "Montserrat"), ("Rubik", "Karla"), ("Outfit", "Lexend")
    ]
    
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="[http://www.sitemaps.org/schemas/sitemap/0.9](http://www.sitemaps.org/schemas/sitemap/0.9)">\n'
    sitemap += '  <url><loc>[https://htmlfonts.com/](https://htmlfonts.com/)</loc><priority>1.0</priority></url>\n'
    
    for font_a, font_b in top_comparisons:
        slug = f"{font_a.lower().replace(' ', '-')}-vs-{font_b.lower().replace(' ', '-')}"
        vs_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>{font_a} vs {font_b} | Best Web Fonts Comparison</title>
    <meta name="description" content="Compare {font_a} and {font_b} side by side. Find the perfect CSS typography for your next web design project.">
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
</head>
<body class="bg-slate-50 p-10 text-center">
    <a href="/#vs-tool" class="text-indigo-600 font-bold uppercase">&larr; Back to Font VS Font</a>
    <h1 class="text-5xl font-black mt-10">{font_a} vs {font_b}</h1>
    <p class="text-xl text-slate-500 mt-4">Discover which typeface fits your UI design best using our live comparison tool on the homepage.</p>
</body>
</html>"""
        with open(f"compare/{slug}.html", 'w', encoding='utf-8') as f:
            f.write(vs_html)
        sitemap += f"  <url><loc>[https://htmlfonts.com/compare/](https://htmlfonts.com/compare/){slug}.html</loc><priority>0.9</priority></url>\n"

    # Add tips to sitemap
    for item in history:
        if 'slug' in item: sitemap += f"  <url><loc>[https://htmlfonts.com/tips/](https://htmlfonts.com/tips/){item['slug']}.html</loc><priority>0.8</priority></url>\n"
    
    sitemap += '</urlset>'
    with open('sitemap.xml', 'w') as f: f.write(sitemap)
    print("✅ System update complete.")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# 3. Post to X
try:
    client_x = tweepy.Client(consumer_key=os.environ["X_API_KEY"], consumer_secret=os.environ["X_API_SECRET"], access_token=os.environ["X_ACCESS_TOKEN"], access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"])
    client_x.create_tweet(text=f"{new_data['tweet']}\n\nRead more: [https://htmlfonts.com/tips/](https://htmlfonts.com/tips/){new_data['slug']}.html")
except Exception as e: 
    print(f"⚠️ X Error: {e}")
