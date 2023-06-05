from re import search
from requests import get
from time import sleep
import asyncio

import commons
from conf import BASE_URL

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
    return f"<a href=\"{BASE_URL}/" + search(r'<a href="(visualizzaCircolare\.php\?ID_circolare=.*?">.*?<\/a>)', raw).groups()[0]


async def sendAlert(newId:str, lastHmtl:str):
    print(f"Nuova circolare! ({newId})")
    for userId in commons.subs.subs:
        try:
            await commons.tgBot.send_message(int(userId), 
                f"Nuova circolare! ({newId})\n\n{lastHmtl}", parse_mode="HTML")
            await asyncio.sleep(1)
        except: pass

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
