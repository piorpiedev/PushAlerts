import os

if os.path.exists("lConf.py"):
    from lConf import BOT_TOKEN, BASE_URL
else:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    BASE_URL = os.environ["BASE_URL"]
