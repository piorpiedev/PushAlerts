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

def urlSafeDifferent(s1:str, s2:str):
    return s1 != s2 and not (s1.startswith(hrefView) and s2.startswith(hrefView) and s1.split('=">', 1)[1] == s2.split('=">', 1)[1])

#formatMgs = lambda num, content, attachments: f"Nuova circolare! ({num})\n\n{content}" + (f"\n\nAttachments: {attachments}" if attachments else "")
def formatMgs(num, content, attachments): 
    return f"Nuova circolare! ({num})\n\n{content}" + (f"\n\nAttachments:\n{attachments}" if attachments else "")


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
        
        yield num, t[0], None if len(attachments) == 0 else (" • " + "\n • ".join(attachments))


def sendMsg(num:int, content:str, attachments:str):
    resp = tgApi.sendMessage(formatMgs(num, content, attachments))
    if not resp: return

    db.addMsg(num, resp["result"]["message_id"], content, attachments)
    print("[LOOP] SEND", (num, content, attachments))

def deleteMsg(num:int):
    if not tgApi.deleteMessage(db.getMsgId(num)): return

    db.deleteMsg(num)
    print("[LOOP] DELETE", num)

def editMsg(num:int, msgId:int, content:str, attachments:str):
    if not tgApi.editMessage(msgId, formatMgs(num, content, attachments)): return

    db.editMsg(num, content, attachments)
    print("[LOOP] EDIT", (num, content, attachments))



if __name__ == "__main__":
    while 1:
        try:
            print("[INFO] Running sync..")
            oldTime = perf_counter() 
            res = get(BASE_URL + "/visCircolari.php")
            res.encoding = res.apparent_encoding
            
            # Isolate and then process each row
            rows = {r[0]: (r[1], r[2]) for r in reversed(list(processRows(
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
            for num, data in rows.items():
                content = data[0]
                attachments = data[1]

                try: oldMsg = oldMessages[num]
                except: # It's NEW! Send a new message and add it to the db
                    sendMsg(num, content, attachments)
                    continue

                # The msg content or attachments has been changed
                if (urlSafeDifferent(oldMsg[1], content) or urlSafeDifferent(oldMsg[2], attachments)): 
                    editMsg(num, oldMsg[0], content, attachments) # The link changes every time you reload the page. I have no words
        
            currentTime = perf_counter()
            print(f"[INFO] Sync completed in {str(round(currentTime - oldTime, 2)).rjust(4, '0')}s | Next sync in {CHECK_EVERY}s..")
            sleep(CHECK_EVERY)
        except ConnectionError as e:
            print("[ERROR] No internet connection. Retrying in 10s..")
            sleep(10)
