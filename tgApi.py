from conf import BOT_TOKEN, CHANNEL_ID
from requests import post
from time import sleep
import logging

baseUrl = f"https://api.telegram.org/bot{BOT_TOKEN}/"

def _sendMessage(content:str, parseMode="HTML"):
    return post(baseUrl + "sendMessage", json={"chat_id": CHANNEL_ID, "text": content, "parse_mode": parseMode}).json()

def _deleteMessage(msgId:int):
    return post(baseUrl + "deleteMessage", json={"chat_id": CHANNEL_ID, "message_id": msgId}).json()

def _editMessage(msgId:int, content:str, parseMode="HTML"):
    return post(baseUrl + "editMessageText", json={"chat_id": CHANNEL_ID, "message_id": msgId, "text": content, "parse_mode": parseMode}).json()


def checkResp(func, args:tuple, scope:str, info:str):
    for _ in range(3): # Max 2 retries for the rate limit .-.
        try:
            resp = func(*args)
            if not resp["ok"]: 
                if resp["error_code"] == 429:
                    time = resp["parameters"]["retry_after"]
                    logging.warning(f"(RATE LIMITED) Unable to {scope} ({time}s)")
                    sleep(time)
                    continue
                else: 
                    logging.error("Unable to", scope, info)
                    return False
            else: 
                return resp
        except: 
            logging.error("Unable to", scope, info)
            return False


def sendMessage(content:str, parseMode="HTML"):
    _content = content.replace("\n", "\\n")
    return checkResp(_sendMessage, (content, parseMode), "send message", f"(content: `{_content}`)")

def deleteMessage(msgId:int):
    return checkResp(_deleteMessage, (msgId,), "delete message", f"(msgId: {msgId})")

def editMessage(msgId:int, content:str, parseMode="HTML"):
    _content = content.replace("\n", "\\n")
    return checkResp(_editMessage, (msgId, content, parseMode), "edit message", f"(msgId: {msgId}, content: `{_content}`)")
