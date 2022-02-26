import os

SERVER_HOST = os.environ.get('HOST', "0.0.0.0")
SERVER_PORT = int(os.environ.get('PORT', 5000))

BOT_API_TOKEN = "5107338273:AAE7IQ6nRotfuvdAmrbyrVws68HJMGr0j4Y"

DB_HOST = 'db-mysql-alesha-amst-do-user-9731128-0.b.db.ondigitalocean.com'
DB_PORT = 25060
DB_NAME = 'alesha'
DB_USERNAME = 'doadmin'
DB_PASSWORD = 'ons4f71is9n17hef'

DB_TABLE_ANNOUNCEMENT = 'evacuation_announcement'

WEBHOOK_URL = 'https://ua-evacuation-bot.herokuapp.com/'


PARSE_MODE = "Markdown"