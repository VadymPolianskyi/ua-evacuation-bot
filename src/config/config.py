import os

SERVER_HOST = os.environ.get('HOST', "0.0.0.0")
SERVER_PORT = int(os.environ.get('PORT', 5000))

BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DB_TABLE_ANNOUNCEMENT = os.getenv("DB_TABLE_ANNOUNCEMENT")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

PARSE_MODE = "Markdown"
