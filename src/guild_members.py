import os
import json
import requests
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

class GuildMembersAgent:
    def __init__(self):
        load_dotenv()  # Load environment variables

        # Albion Online API URL for guild members
        self.guild_url = "https://gameinfo-sgp.albiononline.com/api/gameinfo/guilds/Oyx4dxj1RWGDV5Pf_o4XTg/members"

        # Google Sheets environment variables
        self.SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
        service_account_json = os.getenv("GOOGLE_SERVICE_KEY")

        if not self.SHEET_URL or not service_account_json:
            raise ValueError("Missing Google Sheets URL or service account key in environment variables!")

        # Convert JSON string back to dictionary
        service_account_info = json.loads(service_account_json)

        # 🔹 Correct OAuth Scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        self.creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)

    def update_members(self):
        # Authenticate with Google Sheets
        client = gspread.authorize(self.creds)

        # Open the spreadsheet and select the "Members" sheet
        spreadsheet = client.open_by_url(self.SHEET_URL)
        members_sheet = spreadsheet.worksheet("Members")

        # Fetch guild members data
        response = requests.get(self.guild_url)

        if response.status_code == 200:
            guild_members = response.json()

            if isinstance(guild_members, list):
                # Extract only the names and sort them alphabetically (case-insensitive)
                member_names = sorted([[member.get("Name", "Unknown")] for member in guild_members], key=lambda x: x[0].lower())

                # Clear existing data before writing new data
                members_sheet.clear()

                # Prepare data with a header
                data_to_write = [["Guild Members"]] + member_names

                # Write all member names into the sheet in one go
                members_sheet.update("A1", data_to_write)

                print(f"Successfully wrote {len(member_names)} members to Google Sheets! 🚀")
            else:
                print("Unexpected data format from API.")
        else:
            print(f"Failed to retrieve data! Status Code: {response.status_code}")
