import requests
import time
import json
from datetime import datetime

# --- Configuration ---
WEBHOOK_URL = ""  # Get this from your Discord Channel Settings -> Integrations -> Webhooks
TARGET_URL = "/"         # Replace with the website/server URL you want to monitor
CHECK_INTERVAL_SECONDS = 60                   # How often to check the status (e.g., every 60 seconds)
# ---------------------

def send_discord_notification(status, message):
    """Sends an embedded message to the Discord webhook."""
    
    # Customize the embed color and title based on the status
    if status == "UP":
        color = 65280  # Green
        title = "🟢 Service UP"
    else:
        color = 16711680  # Red
        title = "🔴 Service DOWN"

    data = {
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "Website Monitor Script"
                }
            }
        ]
    }

    try:
        response = requests.post(WEBHOOK_URL, json=data)
        response.raise_for_status() # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error sending Discord message: {e}")

def check_website_status(url):
    """Checks the status of the target URL."""
    try:
        # Use a HEAD request, which is usually faster as it doesn't download the body
        response = requests.head(url, timeout=10)
        # Check for a successful status code (2xx or 3xx)
        if 200 <= response.status_code < 400:
            return "UP", f"Status Code: {response.status_code}"
        else:
            return "DOWN", f"Status Code: {response.status_code}"
    except requests.exceptions.Timeout:
        return "DOWN", "Timeout occurred. The server took too long to respond."
    except requests.exceptions.ConnectionError:
        return "DOWN", "Connection Error. Could not connect to the server."
    except requests.exceptions.RequestException as e:
        return "DOWN", f"An unexpected error occurred: {e}"

def main():
    last_status = None
    print(f"Starting monitoring of {TARGET_URL}. Checking every {CHECK_INTERVAL_SECONDS} seconds...")
    
    while True:
        current_status, reason = check_website_status(TARGET_URL)
        
        # Only send a notification if the status has changed
        if current_status != last_status:
            print(f"Status changed to {current_status}. Sending notification.")
            
            if last_status is not None: # Avoid sending a notification on the very first check
                message = f"The website **{TARGET_URL}** is now **{current_status}**!\nReason: `{reason}`"
                send_discord_notification(current_status, message)
            
            last_status = current_status
        else:
            print(f"Status remains {current_status} at {datetime.now().strftime('%H:%M:%S')}")

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    # To keep this script running continuously, you would typically run it on a server 
    # (like a VPS or cloud service) or use a tool like 'screen' or 'nohup'.
    main()
