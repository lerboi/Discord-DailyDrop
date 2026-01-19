import requests
import os
import sys
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration from Environment Variables
API_URL = "https://anione.me/api/discord/generate-daily-drop"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_DAILY_DROP_KEY = os.getenv("DISCORD_DAILY_DROP_KEY")

# Option 1: Use a publicly hosted image URL
# AVATAR_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/momo4.png"

# Option 2: Use a CDN or image hosting service
# AVATAR_URL = "https://your-cdn.com/path/to/momo4.png"

# Option 3: Remove avatar_url (Discord will use default webhook avatar)
AVATAR_URL = None  # Set to None to omit, or provide a public URL

def validate_config() -> bool:
    """Validate required environment variables are set."""
    if not WEBHOOK_URL:
        logger.error("DISCORD_WEBHOOK_URL environment variable is not set")
        return False
    
    if not DISCORD_DAILY_DROP_KEY:
        logger.error("DISCORD_DAILY_DROP_KEY environment variable is not set")
        return False
    
    logger.info("Configuration validated successfully")
    return True

def fetch_promo_code() -> Optional[str]:
    """Fetch promo code from API."""
    headers = {
        "x-discord-daily-drop-key": DISCORD_DAILY_DROP_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"Fetching promo code from {API_URL}")
        response = requests.post(API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        promo_code = data.get("code")
        
        if not promo_code:
            logger.error("API returned success but no code was found in response")
            logger.debug(f"API response: {data}")
            return None
        
        logger.info(f"Successfully fetched promo code: {promo_code}")
        return promo_code
        
    except requests.exceptions.Timeout:
        logger.error(f"Request to {API_URL} timed out after 10 seconds")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error while fetching promo code: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error while fetching promo code: {e}")
        logger.error(f"Response status: {e.response.status_code}")
        logger.error(f"Response body: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Unexpected error while fetching promo code: {e}")
        return None
    except ValueError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return None

def send_discord_webhook(promo_code: str) -> bool:
    """Send promo code to Discord webhook."""
    redeem_link = f"https://www.anione.me/en/Profile?tab=redeem&code={promo_code}"
    
    payload = {
        "username": "Momo Yaoyorozu",
        "content": "@everyone",
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
    
    # Add avatar_url only if configured
    if AVATAR_URL:
        payload["avatar_url"] = AVATAR_URL
    
    try:
        logger.info(f"Sending promo code to Discord webhook")
        webhook_response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        
        if webhook_response.status_code == 204:
            logger.info(f"✓ Successfully posted promo code to Discord: {promo_code}")
            return True
        else:
            logger.error(f"Discord webhook returned unexpected status: {webhook_response.status_code}")
            logger.error(f"Response: {webhook_response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"Discord webhook request timed out after 10 seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error while posting to Discord: {e}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error posting to Discord webhook: {e}")
        return False

def trigger_daily_drop() -> int:
    """
    Main function to trigger daily drop.
    Returns 0 on success, 1 on failure.
    """
    logger.info("=" * 50)
    logger.info("Starting Daily Drop Trigger")
    logger.info("=" * 50)
    
    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed")
        return 1
    
    # Fetch promo code
    promo_code = fetch_promo_code()
    if not promo_code:
        logger.error("Failed to fetch promo code")
        return 1
    
    # Send to Discord
    success = send_discord_webhook(promo_code)
    if not success:
        logger.error("Failed to send to Discord webhook")
        return 1
    
    logger.info("=" * 50)
    logger.info("Daily Drop Trigger Completed Successfully")
    logger.info("=" * 50)
    return 0

if __name__ == "__main__":
    exit_code = trigger_daily_drop()
    sys.exit(exit_code)
