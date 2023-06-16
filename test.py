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
date_end = "2023-06-04" # datetime.datetime.today().strftime('%Y-%m-%d') #"2023-04-28"
# date_end seems to be upto and not including


str_game_type = "pro_duels"
#url_replays_store = r"https://storage.uk.cloud.ovh.net/v1/AUTH_10286efc0d334efd917d476d7183232e/BAR/demos/"
path_replay_files = r".\BAR_replays\\"+str_game_type+"\\"+date_start+"_"+date_end
path_output = r".\Output\\"+str_game_type
path_replay_metadata = path_output+"\\replay_metadata"

create_folder(path_replay_files)
create_folder(path_replay_metadata)

#response = requests.get(url_replays_store)
#xml_replays = response.content
url_BAR_replays_api = r"https://api.bar-rts.com/replays"

# get_replays_str = url_BAR_replays_api+"?limit=1000&page=2"

limit = "1000" #per page limit
duration_min = "5"
duration_max = "999"

## all matches
# get_replays_num_results = url_BAR_replays_api+'?page=1&limit='+limit+'&hasBots=false&endedNormally=true&date='+date_start+'&date='+date_end+'&durationRangeMins='+duration_min+'&durationRangeMins='+duration_max

## duels only
get_replays_preset = "&preset=duel"
get_replays_filters = get_replays_preset+'&hasBots=false&endedNormally=true&date='+date_start+'&date='+date_end+'&durationRangeMins='+duration_min+'&durationRangeMins='+duration_max
get_compute_total_results = "&computeTotalResults=true"
get_replays_num_results = url_BAR_replays_api+'?page=1&limit='+limit+get_replays_filters+get_compute_total_results
num_results = requests.get(get_replays_num_results).json()["totalResults"]

print(get_replays_num_results)
print(num_results)