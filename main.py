from threading import Thread
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler

import commons
from tgBot import start, notFound, sub, unsub
from webhook import runLoop
from conf import BOT_TOKEN


if __name__ == "__main__":
    commons.subs = commons.Subs()
    tgBot = ApplicationBuilder().token(BOT_TOKEN).build()
    commons.tgBot = tgBot.bot
    
    
    tgBot.add_handler(CommandHandler('start', start))
    tgBot.add_handler(CommandHandler('sub', sub))
    tgBot.add_handler(CommandHandler('unsub', unsub))
    tgBot.add_handler(MessageHandler(filters.TEXT, notFound)) # Text and other commands
    
    # Run loop and bot
    Thread(target=runLoop, daemon=True).start()
    tgBot.run_polling()
