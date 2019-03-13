#Author: James Smith
#Github: JamesSmith1202

import svr_lib
import json
import math
import os
import db_builder
import progressbar

ALGOS_TO_DOWNLOAD = 10
DATABASE_NAME = "replays"

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

#returns a dictionary of replays
def get_winning_replays():
    print("Started: Getting winning replays...")
    replay_dict = {}
    top_algos = get_top_algos(ALGOS_TO_DOWNLOAD)

    print("Started: Gathering winning match IDs")
    replays_to_download = 0
    winning_match_ids = {}
    for algo_id in top_algos:
        winning_match_ids[algo_id] = get_winning_match_ids(top_algos[algo_id])
        replays_to_download += len(winning_match_ids[algo_id])
    print("Finished: Winning match IDs gathered")

    print("Started: Downloading replays...")
    i = 0
    bar = progressbar.ProgressBar(maxval=replays_to_download, widgets=[progressbar.Bar(u"\u2588", '[', ']'), ' ', progressbar.Timer(), ' ', progressbar.ETA() , ' ', progressbar.Percentage()])
    bar.start()
    for algo_id in top_algos:
        winning_replays = []
        for match_id in winning_match_ids[algo_id]:
            winning_replays.append(get_replay(match_id))
            i += 1
            bar.update(i)
        replay_dict[top_algos[algo_id]] = winning_replays
    bar.finish()
    print("Finished: Replays downloaded")
    
    print("Finished: Replays are held in RAM")
    return replay_dict

#downloads winning replays as a SQL database
def download_winning_replays():
    print("Started: Downloading winning replays from top players...")
    replays = get_winning_replays()
    path = "/database"
    os.system("sudo mkdir {}".format(path))
    db_builder.generate_database()
    bar = progressbar.ProgressBar(maxval=len(replays), widgets=[progressbar.Bar(u"\u2588", '[', ']'), ' ', progressbar.Timer(), ' ', progressbar.ETA() , ' ', progressbar.Percentage()])
    bar.start()
    insert_success = db_builder.insert_replays(replays, bar)
    bar.finish()
    if not insert_success:
        print("Finished: Inserting into database failed")
    else:
        print("Finished: database is under './database/{}".format(DATABASE_NAME))
    return insert_success

if __name__ == '__main__':
    download_winning_replays()