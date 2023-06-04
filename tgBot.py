from telegram import Update
from telegram.ext import ContextTypes

import commons

async def reply(text:str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def getUserId(update: Update):
    return update.effective_user.id

def isSubbed(update: Update):
    return str(getUserId(update)) in commons.subs.subs


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply("Hello there! " + ("Scrivi /sub per iscriverti" if isSubbed(update) else "Sei già iscritto, scrivi /unsub se vuoi disiscriverti"), update, context)


async def sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if isSubbed(update):
        await reply("Sei già iscritto! Scrivi /unsub per disiscriverti", update, context)
    else:
        commons.subs.sub(getUserId(update))
        await reply("Ora che sei iscritto, riceverai una notifica ogni volta che una circolare verrà pubblicata\nScrivi /unsub per disiscriverti", update, context)

async def unsub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if isSubbed(update):
        commons.subs.unsub(getUserId(update))
        await reply("Non riceverai più notifiche\nScrivi /sub per riiscriverti", update, context)
    else:
        await reply("Non sei già iscritto! Scrivi /sub per iscriverti e venire avvisato ogni volta che esce una circolare", update, context)

async def notFound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply("Mi spiace ma conosco solo i comandi /sub, /unsub e /last :(", update, context)
