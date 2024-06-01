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



    def addMsg(self, num:int, msgId:int, content:str):
        self.runQuery("INSERT INTO messages (num, msgId, content) values (?, ?, ?)", num, msgId, content)
        return self

    def deleteMsg(self, num:int):
        self.runQuery("DELETE FROM messages WHERE num = ?", num)
        return self
    
    def editMsg(self, num:int, content:str):
        self.runQuery("UPDATE messages SET content = ? WHERE num = ?", content, num)
        return self


    def getMsgId(self, num:int):
        with closing(self.conn.cursor()) as cur:
            return cur.execute("SELECT msgId FROM messages WHERE num = ?", (num, )).fetchone()[0]
    
    def getAllNums(self):
        with closing(self.conn.cursor()) as cur:
            return {i[0] for i in cur.execute("SELECT num FROM messages").fetchall()}

    def getAllMessages(self):
        with closing(self.conn.cursor()) as cur:
            return {num: (msgId, content) for num, msgId, content in cur.execute("SELECT * FROM messages").fetchall()}
