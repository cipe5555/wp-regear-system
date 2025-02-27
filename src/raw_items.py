import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
import json
import os

from dotenv import load_dotenv

# https://github.com/ao-data/ao-bin-dumps/tree/master

class RawItemsAgent:
    def __init__(self):
        load_dotenv()
        
        # Google Sheets credentials file
        # self.SHEET_URL = "https://docs.google.com/spreadsheets/d/1rhxPhkpm9IQMmfEF6lVknEGJMGSHirWy80pszJ4DuZg/edit?gid=1946161692#gid=1946161692"
        # self.SERVICE_ACCOUNT_FILE = 'credential/service_account.json'

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


    def update_raw_items(self):
        # Authenticate and connect to Google Sheets
        # scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # creds = ServiceAccountCredentials.from_json_keyfile_name(self.SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(self.creds)

        # Open the spreadsheet and target sheet
        spreadsheet = client.open_by_url(self.SHEET_URL)
        target_data_sheet = spreadsheet.worksheet("RawItems")  # Destination sheet

        # Load JSON data
        item_file = 'assets/items.json'
        with open(item_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Prefix mapping to tier numbers
        PREFIX_MAP = {
            "初學者": "T1",
            "新手級": "T2",
            "學徒級": "T3",
            "老手級": "T4",
            "專家級": "T5",
            "大師級": "T6",
            "宗師級": "T7",
            "禪師級": "T8"
        }

        rows_to_write = [["Tier", "Base Item Name", "Localized Names (ZH-TW)", "Localized Names (ZH-CN)", "Localized Names (EN-US)", "Item Description", "Unique Item Name"]]  # Add headers

        if data and isinstance(data, list):
            for item in data:
                item_map = item.get("LocalizationNameVariable", "Key not found")
                unique_item_name = item.get("UniqueName", "")

                localized_names = item.get("LocalizedNames")
                if isinstance(localized_names, dict):
                    item_name_tw = localized_names.get("ZH-TW", "None")
                    item_name_zh = localized_names.get("ZH-CN", "None")
                    item_name_en = localized_names.get("EN-US", "None")
                else:
                    item_name_tw, item_name_zh, item_name_en = "None", "None", "None"

                # Get item description in English
                item_desc = item.get("LocalizedDescriptions")
                item_desc_en = item_desc.get("EN-US", "None") if isinstance(item_desc, dict) else "None"

                # Extract tier and base item name
                tier = "Unknown"
                base_name = item_name_tw  # Default to full name if no match is found

                for prefix, tier_num in PREFIX_MAP.items():
                    if item_name_tw.startswith(prefix):
                        tier = tier_num
                        base_name = item_name_tw[len(prefix):].strip()  # Remove the prefix
                        break  # Stop after the first match

                # Apply filters:
                # - Must contain "Equipment Item"
                # - Must NOT contain "Decorative" or "Gatherer"
                # - Must have at least one valid item name
                if (
                    "Decorative" not in item_desc_en and
                    "Gatherer" not in item_desc_en and
                    "Bag" not in item_name_en and
                    "Satchel" not in item_name_en and
                    any(name != "None" for name in [item_name_tw, item_name_zh, item_name_en])):

                    rows_to_write.append([
                        tier,  # Tier mapping
                        base_name,  # Base item name without prefix
                        item_name_tw,
                        item_name_zh,
                        item_name_en,
                        item_desc_en,
                        unique_item_name
                    ])

        # Clear the existing sheet
        target_data_sheet.clear()

        # Write new data to the sheet
        target_data_sheet.update(rows_to_write)

        print("Filtered and mapped data successfully written to Google Sheets! 🚀")
