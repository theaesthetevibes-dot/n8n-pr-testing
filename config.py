"""
Configuration settings for the FastAPI application
"""

# Google Sheets Configuration
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vT6WRqFeaid1f92FULolN8o9ZEqAbx5reF6-7LWZ0304z1eENEIevFNPiAmBdSQLA/pub?gid=267631187&single=true&output=csv"
)

# CSV File Paths
SCRIPT_MASTER_PATH = "api-scrip-master-detailed.csv"
SCRIPT_MASTER_PATH_2 = "api-scrip-master.csv"
DETAILED_SCRIPT_MASTER_PATH = r"C:\Users\kisha\Projects\Trading\Holding Dashboard\api-scrip-master-detailed.csv"

# Dhan API Configuration
DHAN_BASE_URL = "https://api.dhan.co/v2"

# ETF List
ETF_LIST = ["HDFCSML250", "SMALLCAP", "MOSMALL250", "SML100CASE", "METALIETF", "PSUBNKBEES", "PHARMABEES"]

# Exchange Segment Mappings
EXCHANGE_SEGMENTS = {
    "NSE": "NSE",
    "BSE": "BSE",
    "MCX": "MCX",
    "NSE_FNO": "NSE_FNO",
    "MCX_COMM": "MCX_COMM",
    "NSE_EQ": "NSE_EQ"
}

# Application Settings
APP_TITLE = "Dhan Holdings Dashboard"
APP_VERSION = "2.0.0"

# User Credentials (Predefined for now)
AUTHORIZED_USERS = {
    "Kishan": "1721",
    "Rushi": "1122",
    "Harshit": "3344"
}
