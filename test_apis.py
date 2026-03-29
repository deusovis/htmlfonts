import os
import google.generativeai as genai
import tweepy

def test_gemini():
    print("--- Testing Gemini API ---")
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'Gemini is online and ready for htmlfonts.com'")
        print(f"Response: {response.text.strip()}")
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
        # We will post a timestamped test tweet
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = client.create_tweet(text=f"Test tweet from htmlfonts.com at {timestamp} 🚀 #SEO2026")
        print(f"Tweet posted! ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"X API Error: {e}")
        return False

if __name__ == "__main__":
    gemini_status = test_gemini()
    x_status = test_x()
    
    if gemini_status and x_status:
        print("\n✅ ALL SYSTEMS GO! Your secrets are correctly configured.")
    else:
        print("\n❌ CONNECTION FAILED. Check your GitHub Secrets and API permissions.")
        exit(1)
