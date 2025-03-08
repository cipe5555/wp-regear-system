import os
import time
import subprocess
import requests
import re
from dotenv import load_dotenv

load_dotenv()


class RegearSortingAgent:
    """Handles the Discord bot and API server lifecycle"""

    def __init__(self):
        self.discord_bot_path = "src/discord_bot.py"
        self.fastapi_url = "http://127.0.0.1:5000/docs"

    def start_fastapi(self):
        """Start FastAPI server if not running"""
        try:
            response = requests.get(self.fastapi_url)
            if response.status_code == 200:
                print("FastAPI server is already running!")
                return
        except requests.exceptions.ConnectionError:
            print("FastAPI server not found, starting now...")

        # Start FastAPI (which runs the Discord bot) in a subprocess
        process = subprocess.Popen(["python", self.discord_bot_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)  # Allow time for the server to start

    @staticmethod
    def extract_thread_id(url):
        """Extract thread ID from Discord URL"""
        match = re.search(r"discord\.com/channels/\d+/(\d+)", url)
        return match.group(1) if match else None
