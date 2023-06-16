import requests
import os
import json
import datetime
import tqdm
import glob
import re

def create_folder(path):
    if not os.path.exists(path):
        
        # Create a new directory because it does not exist 
        os.makedirs(path)

date_start = "2023-06-01"
date_end = "2023-06-01" # datetime.datetime.today().strftime('%Y-%m-%d') #"2023-04-28"
# date_end seems to be upto and not including


str_game_type = "team"
#url_replays_store = r"https://storage.uk.cloud.ovh.net/v1/AUTH_10286efc0d334efd917d476d7183232e/BAR/demos/"
path_replay_files = r".\BAR_replays\\"+str_game_type+"\\"+date_start+"_"+date_end
path_output = r".\Output\\"+str_game_type
path_replay_data = path_output+"\\replay_data"

create_folder(path_replay_files)
create_folder(path_replay_data)

url_BAR_replays_api = r"https://api.bar-rts.com/replays"

limit = "1000" #per page limit
duration_min = "5"
duration_max = "999"


get_replays_preset = "&preset=team"
get_replays_filters = get_replays_preset+'&hasBots=false&endedNormally=true&date='+date_start+'&date='+date_end+'&durationRangeMins='+duration_min+'&durationRangeMins='+duration_max
get_compute_total_results = "&computeTotalResults=true"
get_replays_num_results = url_BAR_replays_api+'?page=1&limit='+limit+get_replays_filters+get_compute_total_results
num_results = requests.get(get_replays_num_results).json()["totalResults"]

with open(path_replay_data+r"\\replay_metadata_"+str_game_type+"_"+date_start+"_"+date_end+".txt","w") as f:
    f.write(get_replays_num_results)
    f.write("\n")
    f.write("num_results:"+str(num_results))

list_files_replay_data_existing = glob.glob(path_replay_data+r"\replay_data_*") # * means all if need specific format then *.csv
list_replay_data_existing = []
if len(list_files_replay_data_existing) > 0:
    path_latest_replay_data_existing = max(list_files_replay_data_existing, key=os.path.getctime) # most recent data file
    
    #list_replay_data = json.load(open(path_replay_data+r"\replay_data_"+date_start+"_"+date_end+".json"))
    list_replay_data_existing = json.load(open(path_latest_replay_data_existing))

def round_down(num, divisor):
    return num - (num%divisor)

use_existing = False
if use_existing:
    existing_pages = int(round_down(len(list_replay_data_existing),1000)/int(limit))
else:
    existing_pages = 0
    
num_pages = int(num_results/int(limit))+1
required_pages = num_pages - existing_pages

# Iterate API pages to get replay IDs
# New replays are added to front of listing - as pages are iterated, some duplicates are moved into next page before current finished
list_replays_data = []

for p in tqdm.tqdm(range(1,required_pages+1)):
    print(p,required_pages)
    get_replays_str = url_BAR_replays_api+'?page='+str(p)+'&limit='+limit+get_replays_preset+'&hasBots=false&endedNormally=true&date='+date_start+'&date='+date_end+'&durationRangeMins='+duration_min+'&durationRangeMins='+duration_max
    get_replays = requests.get(get_replays_str).json()
    list_replays_data += get_replays["data"]
    
# Get replay data using IDs
if use_existing:
    list_replay_id_existing = [f["id"] for f in list_replay_data_existing]
    list_replay_data = list_replay_data_existing.copy()
else:
    list_replay_id_existing = []
    list_replay_data = []

for replay_data in tqdm.tqdm(list_replays_data):
    str_id = replay_data["id"]
    if str_id not in list_replay_id_existing:
        get_replay_data = url_BAR_replays_api+"/"+str_id
        dict_replay_data = requests.get(get_replay_data).json()
        list_replay_data += [dict_replay_data]
        list_replay_id_existing += [str_id] # ensure duplicate is not redownloaded

# Remove duplicates
# as we were iterating through pages, new games are pushing duplicates into the next page, so downloaded twice...

list_replay_id = [f["id"] for f in list_replay_data]
list_replay_id_unique = list(set(list_replay_id))
list_replay_id_dups = [d for d in list_replay_id if list_replay_id.count(d)>1]

list_replay_data_dedup = []
list_replay_id_dedup = []
for dict_replay in list_replay_data:
    str_id = dict_replay["id"]
    if str_id not in list_replay_id_dedup:
        list_replay_id_dedup += [str_id]
        list_replay_data_dedup += [dict_replay]
        
# Save replay metadata as json

with open(path_replay_data+r"\\replay_data_"+date_start+"_"+date_end+".json", 'w') as fout:
    json.dump(list_replay_data_dedup, fout)

#%% High rated players only filter

# list_replay_data_pro_duels = []

# rating_cut_off = 30
# if rating_cut_off:
#     for replay_data in list_replay_data[:]:
#         replay_has_unskilled_player = False
#         dict_AllyTeams = replay_data["AllyTeams"]
#         for at in dict_AllyTeams:
#             list_AllyTeam_players = at["Players"]
#             for player in list_AllyTeam_players:
#                 skill_player = player["skill"]
#                 skill_player = float(re.sub(r"[\[\]]", "", skill_player))
#                 skillUncertainty_player = player["skillUncertainty"]
#                 #print(skill_player,skillUncertainty_player)
#                 if skill_player < rating_cut_off:
#                     replay_has_unskilled_player = True
#         if not replay_has_unskilled_player:
#             list_replay_data_pro_duels += [replay_data]

# with open(path_replay_data+r"\\replay_data_pro_duels_"+date_start+"_"+date_end+".json", 'w') as fout:
#     json.dump(list_replay_data_pro_duels, fout)

#%% Download replay files
download_full_replays = False
if download_full_replays:
    for replay_data in tqdm.tqdm(list_replay_data_pro_duels):
        replay_filename = replay_data["fileName"]
        # Combine the name and the downloads directory to get the local filename
        url = url_replays_store+replay_filename
        url = url.replace(" ", "%20")
        filename = path_local_replays+"\\"+replay_filename
        
        # Download the file if it does not exist
        if not os.path.isfile(filename):
            urllib.request.urlretrieve(url, filename)