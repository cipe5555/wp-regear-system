import streamlit as st
from datetime import datetime, timedelta
from src.regear import RegearAgent
from src.guild_members import GuildMembersAgent
from src.raw_items import RawItemsAgent

# Initialize Agents
regear_agent = RegearAgent()
guild_members_agent = GuildMembersAgent()
raw_items_agent = RawItemsAgent()

# Streamlit UI
st.title("WP 補裝系統v2.0")

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