#Author: James Smith
#Github: JamesSmith1202

import sqlite3, hashlib, os, subprocess  #enable control of an sqlite database

f = None

def generate_database(name = "db"):
    basedir = os.path.abspath(os.path.dirname(__file__))
    f = basedir + "data/{}.db".format(name)  
    db=sqlite3.connect(f) #creates db if doesnt exist, and connect
    c=db.cursor() #facilitates b ops
    c.execute("CREATE TABLE IF NOT EXISTS replays(algo_id INTEGER, replay BLOB)") #create user table
    db.commit() #save changes
    db.close()

def insert_replays(replays, bar):
    status = True
    if f == None:
        print("Database not generated")
        status = False
    db = sqlite3.connect(f)
    c = db.cursor()
    i = 0
    for algo_id in replays:
        for replay in replays[algo_id]:
            c.execute("INSERT INTO replays VALUES(%d, '%s')" % (algo_id, replay))
        i += 1
        bar.update(i)
    db.commit()
    db.close()    
    return status