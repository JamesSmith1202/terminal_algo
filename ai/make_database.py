#Author: James Smith
#Github: JamesSmith1202

import svr_lib
import json
import math
import os
import progressbar
import sqlite3, hashlib, os, subprocess  #enable control of an sqlite database

ALGOS_TO_DOWNLOAD = 10
DATABASE_NAME = "replays"

global f
f = os.path.abspath(os.path.dirname(__file__)) + "/data/{}.db".format(DATABASE_NAME)

# returns json of replay
def get_replay(match_id):
    path = "/game/replayexpanded/{}".format(match_id)
    content = svr_lib.get_page_content(path)
    return json.loads(json.dumps(content))

#returns the top 'algos' algos in json
def get_top_algos(algos):
    print("Started: Getting top algo IDs...")
    algos_per_page = 10
    pages_needed = int(math.ceil(algos / 10))
    top_algo_ids = svr_lib.get_leaderboard_ids(pages_needed)
    print("Finished: Top algo IDs acquired")
    return top_algo_ids

#returns dictionary of all winning matches for an algo
def get_winning_match_ids(algo_id):
    winningMatches = []
    matches = svr_lib.get_algos_matches(algo_id)
    for match in matches:
        if match['winning_algo']['id'] == algo_id:
            winningMatches.append(match['id'])
    return winningMatches

def generate_database():
    print("Started: Generating SQL database...")
    os.system("sudo mkdir {0} ; sudo chmod 0777 {0}".format("data"))
    db = sqlite3.connect(f) #creates db if doesnt exist, and connect
    c=db.cursor() #facilitates b ops
    c.execute("CREATE TABLE IF NOT EXISTS replays(algo_id INTEGER, replay BLOB)") #create user table
    db.commit() #save changes
    db.close()
    print("Finished: SQL database generated")

def insert_replay(algo_id, replay):
    db = sqlite3.connect(f)
    c = db.cursor()
    c.execute("INSERT INTO replays VALUES(%d, '%s')" % (algo_id, replay))
    db.commit()
    db.close()

    #downloads winning replays as a SQL database
def download_winning_replays():
    
    generate_database()
    
    top_algos = get_top_algos(ALGOS_TO_DOWNLOAD)

    print("Started: Gathering winning match IDs")
    replays_to_download = 0
    winning_match_ids = {}
    for algo_name in top_algos:
        algo_id = top_algos[algo_name]
        winning_match_ids[algo_id] = get_winning_match_ids(algo_id)
        replays_to_download += len(winning_match_ids[algo_id])
    print("Finished: Winning match IDs gathered")

    print("Started: Downloading replays to database...")
    i = 0
    bar = progressbar.ProgressBar(maxval=replays_to_download, widgets=[progressbar.Bar(u"\u2588", '[', ']'), ' ', progressbar.Timer(), ' ', progressbar.ETA() , ' ', progressbar.Percentage()])
    bar.start()
    for algo_name in top_algos:
        algo_id = top_algos[algo_name]
        for match_id in winning_match_ids[algo_id]:
            insert_replay(algo_id, get_replay(match_id))
            i += 1
            bar.update(i)
    bar.finish()
    print("Finished: database is under './database/{}".format(DATABASE_NAME))

if __name__ == '__main__':
    print(f)
    download_winning_replays()