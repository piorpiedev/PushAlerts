from threading import Thread
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler
from telegram.error import NetworkError
from os import path as osPath
from time import sleep

import commons
from tgBot import start, notFound, sub, unsub
from webhook import runLoop
from conf import BOT_TOKEN

if __name__ == "__main__":
    for f in {"subs.txt", "last.txt"}:
        if not osPath.exists(f):
            with open(f, "w"): pass
    commons.subs = commons.Subs()
    
    # Run loop and bot
    Thread(target=runLoop, daemon=True).start()
    while 1:
        try:
            tgBot = ApplicationBuilder().token(BOT_TOKEN).build()
            commons.tgBot = tgBot.bot
            
            tgBot.add_handler(CommandHandler('start', start))
            tgBot.add_handler(CommandHandler('sub', sub))
            tgBot.add_handler(CommandHandler('unsub', unsub))
            tgBot.add_handler(MessageHandler(filters.TEXT, notFound)) # Text and other commands 

            tgBot.run_polling(drop_pending_updates=True, close_loop=False)
        except NetworkError as e: 
            print("[ERROR] Unable to resolve Telegram API address (No internet connection)")
            sleep(10)
