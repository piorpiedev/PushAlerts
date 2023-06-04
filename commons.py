from telegram.ext import ExtBot

class Subs:
    def __init__(self):
        self.load()


    def sub(self, id:int):
        _l = len(self.subs)
        self.subs.add(str(id))
        
        if len(self.subs) != _l: # Make that the list has actually been updated, before updating the file
            self.update()
        
    def unsub(self, id:int):
        self.subs.remove(str(id))
        self.update()


    def load(self):
        with open("subs.txt", "r") as f:
            t = f.read()
        self.subs = set() if t == "" else set(t.split("\n"))

    def update(self):
        with open("subs.txt", "w") as f:
            f.write("\n".join(self.subs))

subs:Subs = None
tgBot:ExtBot = None
