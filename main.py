import streamlit as st
from datetime import datetime, timedelta
import requests
import re
import subprocess
import time
import os
import threading

from src.regear import RegearAgent
from src.guild_members import GuildMembersAgent
from src.raw_items import RawItemsAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Agents
regear_agent = RegearAgent()
guild_members_agent = GuildMembersAgent()
raw_items_agent = RawItemsAgent()

# Hide Streamlit default navigation sidebar
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)


# Sidebar navigation (custom)
st.sidebar.title("導航")
page = st.sidebar.radio("選擇頁面", ["首頁", "補裝整理"])


# Start Discord bot as a background process
def start_discord_bot():
    """Start Discord bot as a separate process if not running."""
    discord_bot_path = "src/discord_bot.py"
    
    try:
        process = subprocess.Popen(["python", discord_bot_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # Allow time for bot startup
        return process
    except Exception as e:
        print(f"Error starting Discord bot: {e}")
        return None


# Run the bot on a separate thread
bot_thread = threading.Thread(target=start_discord_bot, daemon=True)
bot_thread.start()


if page == "首頁":
    st.title("WP 補裝系統 v3.0")

    # Time selection inputs
    st.subheader("選擇開始與結束時間")

    # Get current UTC time
    now_utc = datetime.utcnow()

    # Use Streamlit session state to keep track of selected times
    if "start_time" not in st.session_state:
        st.session_state.start_time = (now_utc - timedelta(hours=1)).time()
    if "end_time" not in st.session_state:
        st.session_state.end_time = now_utc.time()

    # Start time selection
    start_date = st.date_input("開始日期", value=now_utc.date())
    start_time = st.time_input("開始時間(UTC)", value=st.session_state.start_time)

    # End time selection
    end_date = st.date_input("結束日期", value=now_utc.date())
    end_time = st.time_input("結束時間(UTC)", value=st.session_state.end_time)

    # Update session state when user selects new time
    if start_time != st.session_state.start_time:
        st.session_state.start_time = start_time
    if end_time != st.session_state.end_time:
        st.session_state.end_time = end_time

    # Combine date and time into datetime object
    start_datetime = datetime.combine(start_date, st.session_state.start_time)
    end_datetime = datetime.combine(end_date, st.session_state.end_time)

    # Button to trigger the regear process
    if st.button("統計"):
        with st.spinner("統計中，請稍等!"):
            try:
                regear_agent.regear(start_datetime, end_datetime)  # Pass selected times
                st.success("統計成功!")
            except Exception as e:
                st.error(f"錯誤: {e}")

    st.subheader("更新公會成員")
    if st.button("更新成員"):
        with st.spinner("更新中，請稍等!"):
            try:
                guild_members_agent.update_members()
                st.success("更新成功!")
            except Exception as e:
                st.error(f"錯誤: {e}")

    st.subheader("更新物品")
    if st.button("更新"):
        with st.spinner("更新中，請稍等!"):
            try:
                raw_items_agent.update_raw_items()
                st.success("更新成功!")
            except Exception as e:
                st.error(f"錯誤: {e}")

elif page == "補裝整理":
    st.title("補裝整理 🔄")
    
    # Input Discord URL
    discord_url = st.text_input("Enter Discord Thread URL:", "")

    if st.button("Read Messages"):
        # Extract thread ID from URL
        match = re.search(r"discord\.com/channels/\d+/(\d+)", discord_url)
        thread_id = match.group(1) if match else None

        if thread_id:
            response = requests.get(f"http://127.0.0.1:8000/read_messages/{thread_id}")

            if response.status_code == 200:
                messages = response.json().get("messages", [])
                
                if not messages:
                    st.warning("No messages found in this thread.")
                else:
                    # Function to extract sorting key
                    def extract_number(nickname):
                        if not nickname:  # If no nickname, send to last
                            return (float('inf'), float('inf'))
                        
                        match = re.search(r"【(\d+)-(\d+)】", nickname)
                        return tuple(map(int, match.groups())) if match else (float('inf') - 1, float('inf') - 1)

                    # Sort messages: those with numbers first, then those without
                    messages.sort(key=lambda msg: extract_number(msg.get('nickname', '')))

                    # Display sorted messages
                    for msg in messages:
                        st.write(f"**Username:** {msg['username']}")
                        nickname_display = msg['nickname'] if msg['nickname'] else "No Nickname"
                        st.write(f"**Nickname:** {nickname_display}")
                        st.write(f"**Message:** {msg['content']}")

                        # Display images if available
                        if msg["image_urls"]:
                            for img_url in msg["image_urls"]:
                                st.image(img_url, use_column_width=True)

                        st.markdown("---")  # Separator for readability

            else:
                st.error("Error fetching messages.")
        else:
            st.error("Invalid URL. Please enter a correct Discord thread URL.")
