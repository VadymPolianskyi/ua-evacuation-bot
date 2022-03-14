import os

SERVER_HOST = os.environ.get('HOST', "0.0.0.0")
SERVER_PORT = int(os.environ.get('PORT', 5000))

BOT_API_TOKEN = "5067855111:AAHmQTKVHPqeA8ARM4jJuLopaG_OG2L5LPc"

DB_HOST = 'db-mysql-alesha-amst-do-user-9731128-0.b.db.ondigitalocean.com'
DB_PORT = 25060
DB_NAME = 'alesha'
DB_USERNAME = 'doadmin'
DB_PASSWORD = 'ons4f71is9n17hef'

WEBHOOK_URL = 'https://ua-evacuation-bot.herokuapp.com/'
PARSE_MODE = "Markdown"

DB_TABLE_ANNOUNCEMENT = 'evacuation_announcement_test'
DB_TABLE_BLOCKED_USER = 'evacuation_black_list'
DB_TABLE_CITY = 'evacuation_city'
DB_TABLE_USER = 'evacuation_user'

LOG_LEVEL = 'DEBUG'

NOTIFICATIONS_INTERVAL = 30
