import os
import logging

if os.path.exists("lConf.py"):
    from lConf import BOT_TOKEN, BASE_URL, CHANNEL_ID, CHECK_EVERY, LOGGING_LEVEL
else:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    BASE_URL = os.environ["BASE_URL"]
    CHANNEL_ID = os.environ["CHANNEL_ID"]
    CHECK_EVERY = os.environ["CHECK_EVERY"]
    LOGGING_LEVEL = os.environ["LOGGING_LEVEL"]

LOGGING_LEVEL = logging._nameToLevel[LOGGING_LEVEL]
