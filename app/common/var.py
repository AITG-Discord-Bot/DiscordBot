import os
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
devs = os.getenv("DEVS", "").split(",")
devs = [int(dev) for dev in devs if dev.isdigit()]
dev_server = int(os.getenv("DEV_SERVER"))
localization_path = os.getenv("LOCALIZATION_PATH", "./locales")
app_root = os.getenv("BOT_URL_ROOT", "/")
app_port = int(os.getenv("BOT_PORT", 80))

# =================================EXTERNAL URL RELATED=================================
clanbaseurl = os.getenv("CLANBASE_URL", "https://warthunder.com/en/community/claninfo/")
