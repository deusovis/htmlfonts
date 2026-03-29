import os
import sys
# Force a clean path check for the new SDK
try:
    from google import genai
    print("✅ Namespace check: google.genai found.")
except ImportError:
    print("❌ Namespace check: google.genai NOT found. Trying fallback install...")
    os.system('pip install google-genai')
    from google import genai

import tweepy

def test_gemini():
    print("--- Testing Gemini API ---")
    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents="Confirm site status for htmlfonts.com"
        )
        print(f"Gemini Success: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"Gemini Error: {e}")
        return False

def test_x():
    print("\n--- Testing X API ---")
    try:
        client = tweepy.Client(
            consumer_key=os.environ["X_API_KEY"],
            consumer_secret=os.environ["X_API_SECRET"],
            access_token=os.environ["X_ACCESS_TOKEN"],
            access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
        )
        # We try a simple user check instead of a post to save credits
        user = client.get_me()
        print(f"X Connection Success: Connected as @{user.data.username}")
        return True
    except Exception as e:
        if "402" in str(e):
            print("⚠️ X Connection: Keys valid, but BALANCE IS ZERO (402 Payment Required).")
            return True # We mark as true because the KEYS work, just need credits.
        print(f"X API Error: {e}")
        return False

if __name__ == "__main__":
    g_ok = test_gemini()
    x_ok = test_x()
    if g_ok and x_ok:
        print("\n🚀 CONFIGURATION VERIFIED.")
    else:
        sys.exit(1)
