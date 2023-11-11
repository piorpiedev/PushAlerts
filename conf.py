import os

if os.path.exists("lConf.py"):
    from lConf import BOT_TOKEN, BASE_URL, CHANNEL_ID, CHECK_EVERY
else:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    BASE_URL = os.environ["BASE_URL"]
    CHANNEL_ID = os.environ["CHANNEL_ID"]
    CHECK_EVERY = os.environ["CHECK_EVERY"]
