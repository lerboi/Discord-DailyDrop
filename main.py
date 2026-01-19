import requests
import os
import sys

# Configuration from Environment Variables
API_URL = "https://anione.me/api/discord/generate-daily-drop"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_DAILY_DROP_KEY = os.getenv("DISCORD_DAILY_DROP_KEY")  # CHANGED

def trigger_daily_drop():
    headers = {
        "x-discord-daily-drop-key": DISCORD_DAILY_DROP_KEY,  # CHANGED
        "Content-Type": "application/json"
    }
    
    try:
        # 1. Fetch the new code
        response = requests.post(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        promo_code = data.get("code")
        
        if not promo_code:
            print("Error: API returned success but no code.")
            return

        # 2. Construct the Auto-Redeem Link
        redeem_link = f"https://www.anione.me/en/Profile?tab=redeem&code={promo_code}"

        # 3. Format the Discord Payload
        payload = {
            "username": "Anione Rewards",
            "avatar_url": "https://anione.me/logo.png",
            "content": "@everyone", # Triggers the notification
            "embeds": [{
                "title": "🎁 TODAY'S DAILY DROP IS LIVE! 🎁",
                "description": (
                    "New day, new tokens! Unlock more uncensored AI roleplay and "
                    "high-quality image generations on **www.anione.me**."
                ),
                "color": 16711935,
                "fields": [
                    {
                        "name": "🎫 Code",
                        "value": f"``` {promo_code} ```",
                        "inline": False
                    },
                    {
                        "name": "⚡ Quick Redeem",
                        "value": f"**[Click here to redeem your code!]({redeem_link})**",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Code expires in 24 hours. Don't miss out!"
                }
            }]
        }

        # 4. Send to Discord
        webhook_response = requests.post(WEBHOOK_URL, json=payload)
        
        if webhook_response.status_code == 204:
            print(f"Successfully posted code: {promo_code}")
        else:
            print(f"Failed to post to Discord: {webhook_response.text}")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    trigger_daily_drop()
