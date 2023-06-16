import os
import re
import time
import glob
import subprocess
import json
import pandas as pd
import numpy as np
import plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.express as px
import plotly.figure_factory as ff
import tqdm

def create_folder(path):
    if not os.path.exists(path):
        
        # Create a new directory because it does not exist 
        os.makedirs(path)


# date_start = "2022-07-01"
# date_end = "2022-07-31"
date_start = "2023-04-01"
date_end = "2023-05-27"


# path_output = r"E:\SyncedFiles\LAE_Python\BAR_Analysis\Output\4v4"
# path_output_vis = path_output+r"\Visualisations"

path_int = r"Z:\SyncedFiles\LAE_Python\BAR_Analysis\Intermediate\pro_duels"

path_BAR_data = r"E:\BAR\data"
path_replays = r"Z:\BAR_replays_analytical\pro_duels\\"+date_start+"_"+date_end #r"E:\BAR\data\demos" #r"Z:\BAR_replays_analytical"
path_replay_metadata = path_int+r"\replay_metadata"
path_BARexe = r"E:\BAR\Beyond-All-Reason.exe"

path_BARsdd = r"E:\BAR\games\BAR.sdd"
path_configheadless = r"E:\BAR\data\springsettings_headless.cfg"
path_stats = r"E:\BAR\data\stats"
create_folder(path_stats)
# cmd = '"'+path_springexe+'" --help'
# os.system(cmd)


#%% Load all required BAR versions from replay info

list_replay_detailed_data = json.load(open(path_replay_metadata+r"\replay_detailed_data_pro_duels_"+date_start+"_"+date_end+".json"))
list_game_versions = list(set([l["gameVersion"] for l in list_replay_detailed_data]))

#%% List engine versions
list_engines = []
for rep in list_replay_detailed_data:
    engine = rep["engineVersion"]
    if engine not in list_engines:
        list_engines += [engine]

#assert len(list_engines) == 1 # single engine to deal with
#list_replay_detailed_data = [r for r in list_replay_detailed_data if r["engineVersion"]=="105.1.1-1767-gaaf2cc3 BAR105"]
# list_replay_detailed_data = [r for r in list_replay_detailed_data if r["engineVersion"]=="105.1.1-1764-g15bd92d BAR105"]

# str_engine_path = list_engines[0].replace("BAR105","bar")
# path_springexe = r"E:\BAR\data\engine\\"+str_engine_path+"\spring.exe"
# path_springheadlessexe = r"E:\BAR\data\engine\\"+str_engine_path+"\spring-headless.exe"
# path_springexe_devBuild = r"E:\BAR\data\engine\105.1.1-1767-gaaf2cc3 bar\spring.exe"

#%% Maps stats
dict_maps_data = {}
for i,r in enumerate(list_replay_detailed_data):
    dict_maps_data[str(i)] = r["Map"] 

df_maps = pd.DataFrame.from_dict(data=dict_maps_data, orient='index')
df_maps = df_maps.dropna()
df_maps["scriptName"].value_counts()
df_maps["size"] = df_maps["width"].astype(int).astype(str)+"x"+df_maps["height"].astype(int).astype(str)
ds_sizes_counts = df_maps["size"].value_counts()
str_sizes_counts = str(ds_sizes_counts)

df_maps["area"] = df_maps["height"] * df_maps["width"]

df_maps["height"].describe()
df_maps["width"].describe()
df_maps["area"].describe()

#%%

path_pr_downloader = r"E:\BAR\bin\pr-downloader.exe"

for gv in tqdm.tqdm(list_game_versions):
    # args = path_pr_downloader+" --filesystem-writepath "+ path_BAR_data +" --download-game "+ gv
    # subprocess.call(args)
    cmd = path_pr_downloader+' --filesystem-writepath '+ path_BAR_data +' --download-game "' + gv +'"'
    os.system(cmd)

for map_file in tqdm.tqdm(df_maps["scriptName"].unique().tolist()):
    #print(map_file)
    cmd = path_pr_downloader+' --filesystem-writepath '+ path_BAR_data +' --download-map "' + map_file +'"'
    os.system(cmd)

for engine_file in tqdm.tqdm(list_engines):
    #print(map_file)
    cmd = path_pr_downloader+' --filesystem-writepath '+ path_BAR_data +' --download-engine "' + engine_file +'"'
    os.system(cmd)
    

#%%

## Use start boxes to see if maps have a bias for start postion winning
## See bias in factions on results

list_replays_to_analyse_8v8 = []

for rd in list_replay_detailed_data:
    replay_has_no_AIs = True
    replay_teams_have_8 = True
    list_AllyTeams = rd["AllyTeams"]
    dict_AllyTeams_num_players = {}
    
    if len(list_AllyTeams) == 2:
        for AT in list_AllyTeams:
            if len(AT["AIs"]) > 0:
                replay_has_no_AIs = False
            
            num_players = len(AT["Players"])
            dict_AllyTeams_num_players[str(AT)] = num_players
            if num_players != 8:
                replay_teams_have_8 = False
                
        if replay_has_no_AIs & replay_teams_have_8:
            list_replays_to_analyse_8v8 += [rd["fileName"]]

list_replays_to_analyse_1v1 = []

for rd in list_replay_detailed_data:
    replay_has_no_AIs = True
    replay_teams_have_1 = True
    list_AllyTeams = rd["AllyTeams"]
    dict_AllyTeams_num_players = {}
    
    if len(list_AllyTeams) == 2:
        for AT in list_AllyTeams:
            if len(AT["AIs"]) > 0:
                replay_has_no_AIs = False
            
            num_players = len(AT["Players"])
            dict_AllyTeams_num_players[str(AT)] = num_players
            if num_players != 1:
                replay_teams_have_1 = False
                
        if replay_has_no_AIs & replay_teams_have_1:
            list_replays_to_analyse_1v1 += [rd["fileName"]]

list_replays_to_analyse_2v2 = []

for rd in list_replay_detailed_data:
    replay_has_no_AIs = True
    replay_teams_have_2 = True
    list_AllyTeams = rd["AllyTeams"]
    dict_AllyTeams_num_players = {}
    
    if len(list_AllyTeams) == 2:
        for AT in list_AllyTeams:
            if len(AT["AIs"]) > 0:
                replay_has_no_AIs = False
            
            num_players = len(AT["Players"])
            dict_AllyTeams_num_players[str(AT)] = num_players
            if num_players != 2:
                replay_teams_have_2 = False
                
        if replay_has_no_AIs & replay_teams_have_2:
            list_replays_to_analyse_2v2 += [rd["fileName"]]

list_replays_to_analyse_3v3 = []

for rd in list_replay_detailed_data:
    replay_has_no_AIs = True
    replay_teams_have_3 = True
    list_AllyTeams = rd["AllyTeams"]
    dict_AllyTeams_num_players = {}
    
    if len(list_AllyTeams) == 2:
        for AT in list_AllyTeams:
            if len(AT["AIs"]) > 0:
                replay_has_no_AIs = False
            
            num_players = len(AT["Players"])
            dict_AllyTeams_num_players[str(AT)] = num_players
            if num_players != 3:
                replay_teams_have_3 = False
                
        if replay_has_no_AIs & replay_teams_have_3:
            list_replays_to_analyse_3v3 += [rd["fileName"]]

list_replays_to_analyse_4v4 = []

for rd in list_replay_detailed_data:
    replay_has_no_AIs = True
    replay_teams_have_4 = True
    list_AllyTeams = rd["AllyTeams"]
    dict_AllyTeams_num_players = {}
    
    if len(list_AllyTeams) == 2:
        for AT in list_AllyTeams:
            if len(AT["AIs"]) > 0:
                replay_has_no_AIs = False
            
            num_players = len(AT["Players"])
            dict_AllyTeams_num_players[str(AT)] = num_players
            if num_players != 4:
                replay_teams_have_4 = False
                
        if replay_has_no_AIs & replay_teams_have_4:
            list_replays_to_analyse_4v4 += [rd["fileName"]]


list_replays_to_analyse_all_others = []

for rd in list_replay_detailed_data:
    replay_has_no_AIs = True
    replay_teams_have_3 = True
    list_AllyTeams = rd["AllyTeams"]
    dict_AllyTeams_num_players = {}
    

    for AT in list_AllyTeams:
        if len(AT["AIs"]) > 0:
            replay_has_no_AIs = False
        
            
    if replay_has_no_AIs:
        if rd["fileName"] not in list_replays_to_analyse_1v1:
            if rd["fileName"] not in list_replays_to_analyse_2v2:
                if rd["fileName"] not in list_replays_to_analyse_3v3:
                    if rd["fileName"] not in list_replays_to_analyse_4v4:
                        if rd["fileName"] not in list_replays_to_analyse_8v8:
                            list_replays_to_analyse_all_others += [rd["fileName"]]

list_latest_replay = []

#%% Launch all replays for data assimilation

dict_batch_stats = {}

list_test_replay = [r"Z:\BAR_replays_analytical\duels\2023-05-20_2023-05-27\20230520_014917_Comet Catcher Remake 1_105.1.1-1767-gaaf2cc3 BAR105.sdfz"]
#list_replays = list(glob.glob(path_replays+"\\*.sdfz"))

path_output_batch_procs = path_int+r"\batch_stats"
create_folder(path_output_batch_procs)
list_replay_paths = [path_replays+"\\"+r for r in list_replays_to_analyse_1v1[:10]]
for i,filename in tqdm.tqdm(enumerate(list_replay_paths)): #list_test_replay): #list_replay_paths:
    
    str_time_start_id = str(int(time.time()))
    list_generated_unit_stats_files = list(glob.glob(path_BAR_data+r"\\stats\\*_unit_stats.txt"))
    #print("\n"+str(i)+"/"+str(len(list_replay_paths))+": "+filename+"\n")
    
    with open(path_stats+"\\"+str_time_start_id+".json","w") as fout:
        json.dump(filename,fout)
    
    regex_str_engine = r"\d+\.\d+\.\d+-\d+-g[a-f0-9]+"
    regex_pattern_engine = re.compile(regex_str_engine)
    regex_match_engine = regex_pattern_engine.search(filename)
    str_engine = regex_match_engine.group()
    str_engine_path = str_engine+" bar"
    path_springexe = r"E:\BAR\data\engine\\"+str_engine_path+"\spring.exe"
    path_springheadlessexe = r"E:\BAR\data\engine\\"+str_engine_path+"\spring-headless.exe"
    path_springexe_devBuild = r"E:\BAR\data\engine\105.1.1-1767-gaaf2cc3 bar\spring.exe"
    
# 	cmd='copy .\\tehdemos\\'+filename+' '+filename
# 	print cmd
# 	os.system(cmd)
    # cmd='"'+path_springexe+'" "'+filename+'"'
    # print(cmd)
    # os.system(cmd)
    #filename = r"Z:\BAR_replays_analytical\20220701_063350_Eye Of Horus 1_105.1.1-966-g597222f BAR105.sdfz"
    
    # see Spring's springApp.cpp for flags
    # https://github.com/spring/spring/blob/a8cf33ad1d2ac775e6008cd04baa7e859d1f23ec/rts/System/SpringApp.cpp
    # args = '"'+path_springexe+'"'+' -write-dir "' + path_BAR_data + '" "' +filename+'"'
    # subprocess.call(args) #, stdout=FNULL, stderr=FNULL, shell=False)
    # time_start = time.time()
    # cmd = r'""'+path_springexe+'"'+' -write-dir "' + path_BAR_data + '" "' +filename+'""'
    # os.system(cmd)
    # time_end = time.time()
    # print("Normal spring took: ",time_end-time_start)
    
    
    dict_batch_stats[str(i)] = {}
    dict_batch_stats[str(i)]["filename"] = filename
    
    
    #cmd = r'""'+path_springheadlessexe+'"'+' -write-dir "' + path_BAR_data + '" "' +filename+'""'
    #cmd = r'""'+path_springexe+'" -write-dir "' + path_BAR_data + '" -config "' + path_configheadless + '" "' + filename+'""'
    run_required = True
    count_max_runs = 3
    int_cur_run = 0
    while run_required:
        
        args = r'"'+path_springheadlessexe+'" -write-dir "' + path_BAR_data + '" -config "' + path_configheadless + '" "' + filename+'"'
        #args = r'"'+path_springexe+'" -write-dir "' + path_BAR_data + '" -config "' + path_configheadless + '" "' + filename+'"'
       
        # subprocess.call(args) #, stdout=FNULL, stderr=FNULL, shell=False)
        # process_log = subprocess.check_output(args)
        time_start = time.time()
        run_data = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        time_end = time.time()
        print("Run #"+str(int_cur_run)+" Headless Recoil took : ",time_end-time_start)
        dict_batch_stats[str(i)]["str_time_start_id"] = str_time_start_id
        dict_batch_stats[str(i)]["time_taken_"+str(int_cur_run)] = time_end - time_start
        dict_batch_stats[str(i)]["stdout_"+str(int_cur_run)] = str(run_data.stdout)
        dict_batch_stats[str(i)]["stderr_"+str(int_cur_run)] = str(run_data.stderr)
        run_required = False
        int_cur_run += 1

        list_generated_unit_stats_files_recheck = list(glob.glob(path_BAR_data+r"\\stats\\*_unit_stats.txt"))
        list_new_unit_stats_file = [f for f in list_generated_unit_stats_files_recheck if not in list_generated_unit_stats_files]
        
        if len(list_new_unit_stats_file) == 0:
            run_required = True
        else:
            boolean_unit_stats_file_contains_ended = None
            with open(list_new_unit_stats_file[0], 'r') as f:
                # Read the file
                content = f.read()
        
                # Check if the word is in the file
                if "Game Ended" not in content:
                    # If the word is not in the file, add the file path to the list
                    boolean_unit_stats_file_contains_ended = True
                else:
                    boolean_unit_stats_file_contains_ended = False
        
        
        if boolean_unit_stats_file_contains_ended = False
            run_required = True
            
        if int_cur_run == count_max_runs: # Run no more than this many times
            run_required = False 

            
    #print(run_data.returncode, run_data.stdout, run_data.stderr)
    # cmd = r'""'+path_springheadlessexe+'" -write-dir "' + path_BAR_data + '" -config "' + path_configheadless + '" "' + filename+'""'
    # os.system(cmd)
    
    with open(path_output_batch_procs+r"\batch_processing_stats.json", 'w') as fout:
        json.dump(dict_batch_stats, fout)
        
#%% 

# script_path = r"E:\BAR\games\BAR.sdd\test_inactive_ai_script.txt"

# cmd = r'""'+path_springexe+'" -game "' + path_BARsdd + '""' # + '" -config "' + script_path
# os.system(cmd)
# #%%


# list_replay_detailed_data = json.load(open(path_replay_metadata+r"\replay_detailed_data_"+date_start+"_"+date_end+".json"))
# df_replays_metadata = pd.DataFrame(list_replay_detailed_data)

# df_replays_metadata_test = df_replays_metadata.loc[df_replays_metadata["fileName"].isin(list_replays_to_analyse_8v8[:10])]

# list_batch_files_headless = list(glob.glob(path_output+r"\\Headless\\batch_processing_stats*.json"))

# dict_batch_stats_headless = {}
# for batch_file in list_batch_files_headless:
#     dict_batch_stats_headless.update(json.load(open(batch_file))) 
    
# dict_batch_stats_headless_process_time = {os.path.basename(v["filename"]):v["time_taken"] for k,v in dict_batch_stats_headless.items()} 

# list_batch_files_nonheadless = list(glob.glob(path_output+r"\\Nonheadless\\batch_processing_stats*.json"))

# dict_batch_stats_nonheadless = {}
# for batch_file in list_batch_files_nonheadless:
#     dict_batch_stats_nonheadless.update(json.load(open(batch_file))) 
    
# dict_batch_stats_nonheadless_process_time = {os.path.basename(v["filename"]):v["time_taken"] for k,v in dict_batch_stats_nonheadless.items()}     


# df_replays_metadata_test["headless_process_time"] = df_replays_metadata_test["fileName"].map(dict_batch_stats_headless_process_time)
# df_replays_metadata_test["nonheadless_process_time"] = df_replays_metadata_test["fileName"].map(dict_batch_stats_nonheadless_process_time)
# df_replays_metadata_test = df_replays_metadata_test.sort_values(by=["headless_process_time"]).reset_index(drop=True)
# df_replays_metadata_test["fullDuration_s"] = df_replays_metadata_test["fullDurationMs"] / (1000)

# df_replays_metadata_test["headless_game_time_per_process_time"] = df_replays_metadata_test["fullDuration_s"] / df_replays_metadata_test["headless_process_time"]
# df_replays_metadata_test["nonheadless_game_time_per_process_time"] = df_replays_metadata_test["fullDuration_s"] / df_replays_metadata_test["nonheadless_process_time"] 
# df_replays_metadata_test["headless_pc_faster"] = 100 * df_replays_metadata_test["headless_game_time_per_process_time"] / df_replays_metadata_test["nonheadless_game_time_per_process_time"] 

#%% Visualise headless test


# list_x_headless = df_replays_metadata_test["headless_process_time"].tolist()
# list_x_nonheadless = df_replays_metadata_test["nonheadless_process_time"].tolist()
# list_y = df_replays_metadata_test["fullDuration_s"].tolist()

# degree_poly = 2
# # headless polynomial fit
# z_headless = np.polyfit(list_x_headless, list_y, degree_poly)
# f_headless = np.poly1d(z_headless)
# x_headless_new = np.linspace(list_x_headless[0], list_x_headless[-1], 50)
# y_headless_new = f_headless(x_headless_new)

# # nonheadless polynomial fit
# z_nonheadless = np.polyfit(list_x_nonheadless, list_y, degree_poly)
# f_nonheadless = np.poly1d(z_nonheadless)
# x_nonheadless_new = np.linspace(list_x_nonheadless[0], list_x_nonheadless[-1], 50)
# y_nonheadless_new = f_nonheadless(x_nonheadless_new)



# data_title = "Headless vs nonheadless processing time"
# list_traces = []

# headless_trace = go.Scatter(
#     x = list_x_headless,
#     y = list_y,
#     name = "headless",
#     mode = 'markers',
#     hoverinfo = 'all',
#     opacity=0.8,
#     # line=dict(color=unit_colour,
#     #           width=5),
#     marker=dict(color="white",
#                 size=20,
#                 # line=dict(
#                 #     #color=cost_colours[cost],
#                 #     width=2
#                 #         )
#                 ),
#     text = df_replays_metadata_test["fileName"].tolist(),
#     #hovertemplate="%{x|%Y/%m/%d} value: %{y}"
#             )
# list_traces += [headless_trace]


# nonheadless_trace = go.Scatter(
#     x = list_x_nonheadless,
#     y = list_y,
#     name = "nonheadless",
#     mode = 'markers',
#     hoverinfo = 'all',
#     opacity=0.8,
#     # line=dict(color=unit_colour,
#     #           width=5),
#     marker=dict(color="green",
#                 size=20,
#                 # line=dict(
#                 #     #color=cost_colours[cost],
#                 #     width=2
#                 #         )
#                 ),
#     text = df_replays_metadata_test["fileName"].tolist(),
#     #hovertemplate="%{x|%Y/%m/%d} value: %{y}"
#             )
# list_traces += [nonheadless_trace]

# headless_fit_trace = go.Scatter(
#     x = x_headless_new,
#     y = y_headless_new,
#     name = "headless_fit",
#     mode = 'lines',
#     hoverinfo = 'all',
#     opacity=0.8,
#     line=dict(color="white",
#               width=2),
#             )
# list_traces += [headless_fit_trace]

# nonheadless_fit_trace = go.Scatter(
#     x = x_nonheadless_new,
#     y = y_nonheadless_new,
#     name = "nonheadless_fit",
#     mode = 'lines',
#     hoverinfo = 'all',
#     opacity=0.8,
#     line=dict(color="green",
#               width=2),
#             )
# list_traces += [nonheadless_fit_trace]

# ## pairing lines



# fig = go.Figure(data=list_traces,
#             layout = go.Layout(
#                title = data_title,
#                xaxis = dict(title = "Processing time (s)", type="linear"),
#                yaxis = dict(title = "Game time (s)", type="linear"),
#                plot_bgcolor = 'rgba(0,0,0,255)',
#                paper_bgcolor = 'rgba(0,0,0,255)',
#                titlefont = dict(
#                    family = "Consolas",
#                    size = 25,
#                    color = "White"),
#                font = dict(
#                    family = "Consolas",
#                    size = 10,
#                    color = "White"
#                    ),
#                showlegend = True,
#                hovermode = 'closest',
#                margin = dict(b=100,l=5,r=5,t=100),
#                annotations = [],
               
#                # xaxis=go.layout.XAxis(showgrid=False, zeroline=False, showticklabels=False), #, scaleanchor='y', scaleratio=1), # 
#                # yaxis=go.layout.YAxis(showgrid=False, zeroline=False, showticklabels=False), #, scaleanchor='x', scaleratio=1)
#             )
#             )

#                #range=[-7,7],   range needs to be relative to the initial edge length
        
# chart_annotations = [
#                    dict(
#                        text='<a href="https://www.beyondallreason.info/">Data from BAR RTS Replays</a>',
#                        showarrow=False,
#                        xref="paper", yref="paper",
#                        x=0.005, y=-0.05
#                        ),
#                    dict(
#                        text='<a href="https://discordapp.com/users/Borg%20King#9324">Borg King</a>',
#                        showarrow=False,
#                        xref="paper", yref="paper",
#                        x=1, y=-0.05
#                        )
#                        ]


# fig['layout']['annotations'] = chart_annotations

# path_output_file = r"\\" + data_title.replace("/","_") + ".html"
# py.offline.plot(fig, filename=path_output_vis+path_output_file, include_plotlyjs="cdn")
