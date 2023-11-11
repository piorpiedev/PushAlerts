from sqlite3 import connect
from os import path as osPath
from contextlib import closing

class Database:

    def __init__(self, path:str, schemaPath:str):
        created = not osPath.exists(path)
        if created: 
            with open(path, "w"): pass

        self.conn = connect(path, isolation_level=None)
        if created and schemaPath:
            with open(schemaPath) as f: 
                with closing(self.conn.cursor()) as cur:
                    for query in f.read().split(";"): # Run Each query from the schema file
                        query = query.replace("\n", "").replace("  ", "").strip()
                        if query: cur.execute(query + ";")
    
    def runQuery(self, query, *args):
        with closing(self.conn.cursor()) as cur:
            cur.execute(query, args)



    def addMsg(self, num:int, msgId:int, content:str, attachments:str):
        self.runQuery("INSERT INTO messages (num, msgId, content, attachments) values (?, ?, ?, ?)", num, msgId, content, attachments)
        return self

    def deleteMsg(self, num:int):
        self.runQuery("DELETE FROM messages WHERE num = ?", (num, ))
        return self
    
    def editMsg(self, num:int, content:str, attachments:str):
        self.runQuery("UPDATE messages SET content = ?, attachments = ? WHERE num = ?", content, num, attachments)
        return self


    def getMsgId(self, num:int):
        with closing(self.conn.cursor()) as cur:
            return cur.execute("SELECT msgId FROM messages WHERE num = ?", (num, )).fetchone()
    
    def getAllNums(self):
        with closing(self.conn.cursor()) as cur:
            return {i[0] for i in cur.execute("SELECT num FROM messages").fetchall()}

    def getAllMessages(self):
        with closing(self.conn.cursor()) as cur:
            return {num: (msgId, content, attachments) for num, msgId, content, attachments in cur.execute("SELECT * FROM messages").fetchall()}
