import os
from typing import Sequence
from urllib.parse import urljoin

token = os.getenv("TOKEN")
apiurl = os.getenv("API_URL", "http://aitg-backend")
logpath = os.getenv("LOGPATH", "/logs")
if not os.path.exists(logpath):
    os.makedirs(logpath)
debugfile = os.getenv("DEBUGFILE", "debug.log")
debugfile = os.path.join(logpath, debugfile)
errorfile = os.getenv("ERRORFILE", "error.log")
errorfile = os.path.join(logpath, errorfile)
devs = [int(sid) for sid in os.getenv("DEVS", "").split(",") if sid.isdigit()]
dev_servers: Sequence[int] = [
    int(sid) for sid in os.getenv("DEV_SERVERS", "").split(",") if sid.isdigit()
]
localization_path = os.getenv("LOCALIZATION_PATH", "./locales")
app_root = os.getenv("BOT_URL_ROOT", "/")
app_port = int(os.getenv("BOT_PORT", 80))
support_server_id = int(os.getenv("SUPPORT_SERVER_ID", 0))
support_forum_id = int(os.getenv("SUPPORT_FORUM_ID", 0))
support_dev_role_id = int(os.getenv("SUPPORT_DEV_ROLE_ID", 0))

# =================================EXTERNAL URL RELATED=================================
clanbaseurl = os.getenv("CLANBASE_URL", "https://warthunder.com/en/community/claninfo/")
warthunderbaseurl = os.getenv(
    "WARTHUNDER_BASE_URL", "https://warthunder.com/en/community/community/"
)
