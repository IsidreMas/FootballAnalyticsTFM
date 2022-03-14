# Script intended to gather dataframe filtering functions.

import pandas as pd

def time_window(tracking_dataframe, start, end, frame = False):

    if not frame:
        try:
            return tracking_dataframe[(tracking_dataframe['Time [s]'] <= end) & (tracking_dataframe['Time [s]'] >= start)]
        except:
            return tracking_dataframe[(tracking_dataframe['End Time [s]'] <= end) & (tracking_dataframe['Start Time [s]'] >= start)]
    else:
        try:
            return tracking_dataframe[(tracking_dataframe['Frame'] <= end) & (tracking_dataframe['Frame'] >= start)]
        except:
            return tracking_dataframe[(tracking_dataframe['End Frame'] <= end) & (tracking_dataframe['Start Frame'] >= start)]

def filter_dead_time(match_object):
    print('Filtering dead time...\n')
    indices = match_object.events[match_object.events["Type"] == "SET PIECE"].index[1:]
    lower = match_object.events.iloc[indices-1]['End Time [s]']
    lower.index = indices
    upper = match_object.events.iloc[indices]['Start Time [s]']
    ranges = pd.concat([lower,upper], axis=1)
    for period in ranges.iterrows():
        match_object.tracking_home = match_object.tracking_home[~match_object.tracking_home['Time [s]'].between(period[1][0], period[1][1])]
        match_object.tracking_away = match_object.tracking_away[~match_object.tracking_away['Time [s]'].between(period[1][0], period[1][1])]