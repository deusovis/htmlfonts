import os
import datetime
from google import genai
import tweepy

def test_gemini():
    print("--- Testing Gemini API (2026 SDK) ---")
    try:
        # Use the NEW client-based initialization
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents="Say 'Gemini 2026 is active'"
        )
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
        # Note: 402 error usually happens here if credits are empty
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = client.create_tweet(text=f"API Test for htmlfonts.com at {timestamp}")
        print(f"Tweet posted! ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"X API Error: {e}")
        if "402" in str(e):
            print("💡 TIP: Your X Free Tier credits are exhausted or your region requires a subscription.")
        return False

if __name__ == "__main__":
    gemini_status = test_gemini()
    x_status = test_x()
    
    if gemini_status and x_status:
        print("\n✅ ALL SYSTEMS GO!")
    else:
        print("\n❌ SYSTEM CHECK FAILED.")
        exit(1)
