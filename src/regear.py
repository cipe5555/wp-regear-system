import requests
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil import parser
from collections import defaultdict
import os
from dotenv import load_dotenv
import json

class RegearAgent:
    def __init__(self):
        load_dotenv()
        # Define quality mapping
        self.QUALITY_MAP = {
            "1": "無",
            "2": "鉄",
            "3": "銅",
            "4": "銀",
            "5": "金"
        }
        # Google Sheets setup
        # self.SHEET_URL = "https://docs.google.com/spreadsheets/d/1rhxPhkpm9IQMmfEF6lVknEGJMGSHirWy80pszJ4DuZg/edit?gid=1946161692#gid=1946161692"
        # self.SERVICE_ACCOUNT_FILE = "credential/service_account.json"

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
    
    def regear(self, start_time, end_time):
        # Authenticate with Google Sheets
        # scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # creds = ServiceAccountCredentials.from_json_keyfile_name(self.SERVICE_ACCOUNT_FILE, scope)

        client = gspread.authorize(self.creds)

        # Open the sheets
        spreadsheet = client.open_by_url(self.SHEET_URL)
        members_data_sheet = spreadsheet.worksheet("Members")
        raw_data_sheet = spreadsheet.worksheet("Raw")
        raw_items_sheet = spreadsheet.worksheet("RawItems")
        statistics_sheet = spreadsheet.worksheet("Statistics")

        # Load item name mappings from "RawItems"
        raw_items_data = raw_items_sheet.get_all_records()
        item_name_map = {row["Unique Item Name"]: row["Base Item Name"] for row in raw_items_data if row["Unique Item Name"]}

        # Fetch player names from "Form Data" sheet
        form_data = members_data_sheet.get_all_records()
        player_names = {
            str(row["Guild Members"]).strip().lower()
            for row in form_data 
            if isinstance(row.get("Guild Members"), str) and row["Guild Members"].strip()
        }


        # Ensure "Raw" sheet has a header
        header = [
            "Timestamp", "Name", "Main Hand", "Off Hand", "Head", "Armor", "Shoes", "Cape", "Mount"
        ]
        if not raw_data_sheet.get_all_values():
            raw_data_sheet.append_row(header)

        # Initialize dictionary for item statistics
        item_counts = defaultdict(int)

        # Function to extract item details and count occurrences
        def get_item_details(item):
            if not item:
                return "None"
            
            unique_name = item.get("Type", "None")
            quality = str(item.get("Quality", "0"))
            quality_label = self.QUALITY_MAP.get(quality, "none")

            match = re.match(r"(T\d+)_?(.*?)(@\d+)?$", unique_name)
            if match:
                tier, base_name, level_suffix = match.groups()
                level = f".{level_suffix[1:]}" if level_suffix else ""

                localized_name = item_name_map.get(unique_name, base_name)
                item_full_name = f"{localized_name}{tier}{level} - {quality_label}"
                
                # Update item count
                item_counts[item_full_name] += 1
                
                return item_full_name
            else:
                localized_name = item_name_map.get(unique_name, "")
                item_full_name = f"{localized_name} - {quality_label}"

                item_counts[item_full_name] += 1

                return item_full_name


            return f"{unique_name} - {quality_label}"

        # Guild members API URL
        guild_url = "https://gameinfo-sgp.albiononline.com/api/gameinfo/guilds/Oyx4dxj1RWGDV5Pf_o4XTg/members"
        response = requests.get(guild_url)

        if response.status_code == 200:
            guild_data = response.json()
            if isinstance(guild_data, list):
                new_rows = []

                for player in guild_data:
                    name = player.get("Name", "").strip()
                    player_id = player.get("Id", "")

                    if name.lower() in player_names:
                        print(f"Processing player: {name}")
                        deaths_url = f"https://gameinfo-sgp.albiononline.com/api/gameinfo/players/{player_id}/deaths"
                        deaths_response = requests.get(deaths_url)

                        if deaths_response.status_code == 200:
                            deaths_data = deaths_response.json()

                            for death in deaths_data:
                                timestamp_str = death.get("TimeStamp", "")
                                timestamp = parser.isoparse(timestamp_str).replace(tzinfo=None)

                                if start_time <= timestamp <= end_time:
                                    victim = death.get("Victim", {})
                                    equipment = victim.get("Equipment", {})

                                    new_rows.append([
                                        timestamp_str,
                                        name,
                                        get_item_details(equipment.get("MainHand")),
                                        get_item_details(equipment.get("OffHand")),
                                        get_item_details(equipment.get("Head")),
                                        get_item_details(equipment.get("Armor")),
                                        get_item_details(equipment.get("Shoes")),
                                        get_item_details(equipment.get("Cape")),
                                        get_item_details(equipment.get("Mount"))
                                    ])
                        else:
                            print(f"Error fetching death history for {name} (Status Code: {deaths_response.status_code})")

                # Batch write all new rows at once
                if new_rows:
                    raw_data_sheet.append_rows(new_rows)
                    print(f"{len(new_rows)} rows added to 'Raw' sheet.")
            else:
                print("Unexpected response format")
        else:
            print(f"Error: Unable to fetch data (Status Code: {response.status_code})")

        # Write statistics to "Statistics" sheet in a batch
        statistics_sheet.clear()  # Clear existing data
        statistics_sheet.append_row(["Item Name", "Count"])

        # Dictionary to store combined item counts (ignoring quality levels)
        combined_counts = defaultdict(int)

        # Process item counts
        for item_name, count in item_counts.items():
            if any(q in item_name for q in ["無", "鉄"]):  # Skip filtered items
                continue

            # Extract base name (removing quality suffix)
            base_name = re.sub(r" - .*", "", item_name)  # Removes " - QualityLabel"
            combined_counts[base_name] += count  # Combine counts

        # Convert to sorted list and write in batch
        sorted_statistics_data = sorted(combined_counts.items())  # Sort by item name

        if sorted_statistics_data:
            statistics_sheet.append_rows(sorted_statistics_data)

        print("Statistics updated successfully!")
