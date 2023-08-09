from re import search
from requests import get, post
from time import sleep
import asyncio

import commons
from conf import BASE_URL, BOT_TOKEN

class LastId:
    def __init__(self):
        self.load()

    def load(self):
        with open("last.txt", "r") as f:
            self.lastId = f.read()
        
    def update(self, newId:str):
        self.lastId = newId
        with open("last.txt", "w") as f:
            f.write(newId)


def getLastId(raw:str):
    return search(r"<tbody(?:| )>(?:\n.*?)+<tr><td>(\d+)", raw).groups()[0]

def getLastHmtl(raw:str):
    # Get last non-null entry (html[1] or just the title[0])
    r = next(x for x in reversed(
        search(r"<\/td><td(?:>(.*?)| class=\"sopra\">(<a href=\"visualizzaCircolare\.php\?ID_circolare=.*?\">.*?<\/a>))<\/td>", raw, flags=16).groups()) if x)
    return "<a href=\"" + BASE_URL + "/" + r[9:] if r and r.startswith("<a href=\"visualizzaCircolare.php?") else r

def sendAPIMsg(chat_id:str, msg:str, parse_mode = ""):
    return post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode={parse_mode}")

async def sendAlert(newId:str, lastHmtl:str):
    print(f"Nuova circolare! ({newId})")
    for userId in commons.subs.subs:
        try: sendAPIMsg(userId, f"Nuova circolare! ({newId})\n\n{lastHmtl}", "HTML")
        except: pass
        sleep(.5)

def runLoop():
    lastId = LastId()
    lastId.load()
    
    while 1:
        try:
            r = get(BASE_URL + "/visCircolari.php").text
            newId = getLastId(r)
            if newId != lastId.lastId:        
                lastId.update(newId)
                asyncio.run(sendAlert(newId, getLastHmtl(r)))
        except Exception as e:
            print("Exception in the \"webhook\" loop: " + str(e))
        sleep(300)
