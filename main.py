from requests import get
from requests.exceptions import ConnectionError
from conf import BASE_URL, CHECK_EVERY
import tgApi
from db import Database
from time import sleep, perf_counter

db = Database("data.db", "schema.sql")

def processRows(rows:list[str]):
    for row in rows:
        t = row.rstrip().split('</td><td style="text-align:center">')
        yield (
            int(t[0][8:]), 
            t[1][15:].removeprefix("<td>").split("</td>")[0]
        )


def sendMsg(num:int, content:str):
    resp = tgApi.sendMessage(f"Nuova circolare! ({num})\n\n{content}")
    if not resp: return

    db.addMsg(num, resp["result"]["message_id"], content)
    print("[LOOP] SEND", (num, content))

def deleteMsg(num:int):
    if not tgApi.deleteMessage(db.getMsgId(num)): return

    db.deleteMsg(num)
    print("[LOOP] DELETE", num)

def editMsg(num:int, msgId:int, content:str):
    if not tgApi.editMessage(msgId, f"Nuova circolare! ({num})\n\n{content}"): return

    db.editMsg(num, content)
    print("[LOOP] EDIT", (num, content))



if __name__ == "__main__":
    url = BASE_URL + "/visualizzaCircolare.php"
    href = '<a href="' + url

    while 1:
        try:
            print("[INFO] Running sync..")
            oldTime = perf_counter() 
            res = get(BASE_URL + "/visCircolari.php")
            res.encoding = res.apparent_encoding
            
            # Isolate and then process each row
            rows = {r[0]: r[1] for r in reversed(list(processRows(
                res.text.split("<tbody >")[1].split("</tbody>")[0].strip()
                    .replace('<a href=""></a>', "").replace("<br>", "").replace('<td class="sopra">', "")
                    .replace("\n", "").replace("\r", "")[:-11].replace("visualizzaCircolare.php", url)
                    .split(" </td></tr>")
            )))}

            # Find messages that are no longer on the website
            for num in db.getAllNums().difference(rows.keys()):
                deleteMsg(num)

            # New or changed messages
            oldMessages = db.getAllMessages()
            for num, content in rows.items():
                try: oldMsg = oldMessages[num]
                except: # It's NEW! Send a new message and add it to the db
                    sendMsg(num, content)
                    continue

                if oldMsg[1] != content: # The msg content has been changed
                    if not (oldMsg[1].startswith(href) and content.startswith(href) and oldMsg[1].split('=">', 1)[1] == content.split('=">', 1)[1]):
                        editMsg(num, oldMsg[0], content) # The link changes every time you reload the page. I have no words
        
            currentTime = perf_counter()
            print(f"[INFO] Sync completed in {round(currentTime - oldTime, 2)}s | Next sync in {CHECK_EVERY}s..")
            sleep(CHECK_EVERY)
        except ConnectionError as e:
            print("[ERROR] No internet connection. Retrying in 10s..")
            sleep(10)
