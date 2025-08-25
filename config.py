"""Configuration pour l'EPG Ligue1+"""

# API Configuration
LIGUE1_API_BASE = "https://ma-api.ligue1.fr"
LIGUE1_API_ENDPOINT = "/championships-daily-calendars/matches"

# EPG Configuration
CHANNEL_ID = "Ligue1Plus"
CHANNEL_NAME = "Ligue 1+"
TIMEZONE = "Europe/Paris"

# Broadcaster filtering
TARGET_BROADCASTER = "L1+"

# Output configuration
EPG_OUTPUT_FILE = "ligue1_epg.xml"

# Default match duration in minutes (if end time not available)
DEFAULT_MATCH_DURATION = 120
