# watchdog.py
from mod import run_bot
import time
import logging
from keep_alive import keep_alive
import bot
print(bot.__file__) # Imports run_bot from bot.py
logging.basicConfig(level=logging.INFO)


run_bot()

keep_alive()

while True:
    try:
        run_bot()
    except Exception as e:
        logging.error(f"❌ Bot crashed: {e}")
        time.sleep(5)
        print("🔁 Restarting bot...")
        # Wait before restarting