import streamlit as st
import requests
import re

st.title("Discord Forum Reader")

# Input Discord URL
discord_url = st.text_input("Enter Discord Thread URL:", "")

def extract_thread_id(url):
    """Extract thread ID from Discord URL"""
    match = re.search(r"discord\.com/channels/\d+/(\d+)", url)
    return match.group(1) if match else None

if st.button("Read Messages"):
    thread_id = extract_thread_id(discord_url)
    
    if thread_id:
        response = requests.get(f"http://127.0.0.1:8000/read_messages/{thread_id}")
        if response.status_code == 200:
            messages = response.json().get("messages", [])
            for msg in messages:
                st.write(f"**Username:** {msg['username']}")
                if msg['nickname']:
                    st.write(f"**Nickname:** {msg['nickname']}")
                st.write(f"**Message:** {msg['content']}")
                st.write(f"**Timestamp:** {msg['timestamp']}")

                # Display images if available
                if msg["image_urls"]:
                    for img_url in msg["image_urls"]:
                        st.image(img_url, caption="Attached Image", use_column_width=True)

                st.markdown("---")  # Add a separator for readability

        else:
            st.error("Error fetching messages")
    else:
        st.error("Invalid URL. Please enter a correct Discord thread URL.")
