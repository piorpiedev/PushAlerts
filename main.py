from requests import get
from requests.exceptions import ConnectionError
from conf import BASE_URL, CHECK_EVERY
import tgApi
from db import Database
from time import sleep, perf_counter

db = Database("data.db", "schema.sql")
url = BASE_URL + "/visualizzaCircolare.php"
baseHref = '<a href="'
href = baseHref + BASE_URL + "/"
hrefView = baseHref + url


def isUrl(s:str):
    return s.startswith("http://") or s.startswith("https://")


def processRows(rows:list[str]):
    for row in rows:
        t = row.rstrip().split('</td><td style="text-align:center">')
        num = int(t[0][8:])
        
        t = t[1][15:].removeprefix("<td>").split("</td>")
        attachments = t[1].removeprefix("<td>").replace("</a>  <a", "</a>\n<a").split("\n")

        for i, attachment in enumerate(attachments):

            # Starts with an html link
            if attachment.startswith(baseHref):
                if not isUrl(attachment.removeprefix(baseHref)):
                    attachments[i] = attachment.replace(baseHref, href) # Fix local url (/page)

            # Just text and is NOT an URL
            elif not isUrl(attachment):
                del attachments[i]
        
        yield num, t[0] if len(attachments) == 0 else (t[0] + "\n\nAttachments:\n • " + "\n • ".join(attachments))


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

                # The msg content has been changed
                if (oldMsg[1] != content and not (oldMsg[1].startswith(hrefView) and content.startswith(hrefView) and 
                    oldMsg[1].split('=">', 1)[1] == content.split('=">', 1)[1])): # The link changes each time you reload the page. I have no words
                    editMsg(num, oldMsg[0], content) 
        
            currentTime = perf_counter()
            print(f"[INFO] Sync completed in {str(round(currentTime - oldTime, 2)).ljust(4, '0')}s | Next sync in {CHECK_EVERY}s..")
            sleep(CHECK_EVERY)
        except ConnectionError as e:
            print("[ERROR] No internet connection. Retrying in 10s..")
            sleep(10)
