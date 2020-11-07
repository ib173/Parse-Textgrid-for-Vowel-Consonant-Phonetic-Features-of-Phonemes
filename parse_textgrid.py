import glob
import parselmouth
import re
import os
import json
import csv
from collections import Counter
import pandas as pd
import numpy as np
import itertools
from parselmouth.praat import call


data_root_NE = r"C:\Users\iannb\OneDrive\Documents\BC Senior Year_\Speech Sig\Hackathons\hackathon1-team-9\Northeast_json3\*.json"
data_root_West = r"C:\Users\iannb\OneDrive\Documents\BC Senior Year_\Speech Sig\Hackathons\hackathon1-team-9\West_json3\*.json"

def collect_data():
    file_paths = [data_root_NE, data_root_West]
    df1_test_list, df2_test_list = [], []
    df1 = config_(file_paths[0])
    n1 = len(df1)
    df1_test_list += n1 * [0]
    df1['test'] = df1_test_list
    # print(df1)


    df2 = config_(file_paths[1])
    n2 = len(df2)
    df2_test_list += n2 * [1]
    df2['test'] = df2_test_list
    # print(df2)

    df3 = df1.append(df2, ignore_index=True)
    df3.fillna(0)

    print(df3)
    df3.to_csv("phoneme_data3.csv", index=False)

def config_(root):
    all_sounds = []
    file_names = []
    final_dict = dict()
    for filepath in glob.iglob(root):
        vowel_list = []
        con_list = []
        with open(filepath, 'r') as j:
            contents = json.loads(j.read())
            sounds = []
            if root == data_root_NE:
                a, b = filepath.find('Northeast'), filepath.find('_conversion')
                file_name = filepath[a+16:b]
            else:
                index = filepath.find("West")
                a, b = filepath.find('West'), filepath.find('_conversion')
                file_name = filepath[a+11:b]
            # print(file_name)
            intervals = contents["tiers"][0]["items"]
            for interval in intervals:
                duration = float(interval["xmax"]) - float(interval["xmin"])
                sound = interval["text"]
                sounds.append(sound)
                if sound[0].lower() in ['a', 'e', 'i', 'o', 'u']:
                    vowel_list.append(duration)
                else:
                    con_list.append(duration)
            vowel_ave = Average(vowel_list)
            con_ave = Average(con_list)
            # print(sounds)
            all_sounds.extend(sounds)
            # indexed_list = Counter(list(itertools.chain(*sounds)))
            indexed_list = Counter(list(sounds))
            # print(indexed_list)
            # print(vowel_ave, con_ave, filname)
            file_names.append(file_name)
            final_dict[file_name] = [indexed_list, vowel_ave, con_ave]

            # print("----------")
            # with open(file_path, 'a') as file:
            #     file.write(" <"+str(filname)+"> "+" <"+str(vowel_ave)+"> "+" <"+str(con_ave)+">\n")
    all_sounds_set = set(all_sounds)
    answer_list = []
    all_sounds_list = list(all_sounds_set)
    final_data_array = parse_dict(final_dict, file_names, all_sounds_list)
    df = pack_df(final_data_array, file_names, all_sounds_list)
    vowel_average_duration_list = []
    cons_average_duration_list = []
    for key in file_names:
        vowel_average_duration_list.append(final_dict[key][1])
        cons_average_duration_list.append(final_dict[key][2])

    df['vowel average'] = vowel_average_duration_list
    df['consonant average'] = cons_average_duration_list
    return df

def pack_df(final_data_array, file_names, all_sounds_list):
    column_names = ["name"] + all_sounds_list
    my_range = list(range(0, len(file_names)))
    df = pd.DataFrame(columns = column_names, index = my_range)

    for file_name, temp_arr, val in zip(file_names, final_data_array, my_range):
        df.iloc[val] = [file_name] + temp_arr
    return df


def parse_dict(file_dict, file_list, all_sounds_list):
    final_data_array = []
    for file_name in file_list:
        # print(file_name)
        temp_file_data = []
        temp_entry = file_dict[file_name]
        indexed_sound_list = temp_entry[0]
        vowel_avg = temp_entry[1]
        cons_avg = temp_entry[2]
        for sound in all_sounds_list:
            if sound in indexed_sound_list.keys():
                temp_file_data.append(indexed_sound_list[sound])
            else:
                temp_file_data.append(0)

        final_data_array.append(temp_file_data)

    return final_data_array



def Average(lst):
    return sum(lst) / len(lst)


collect_data()
