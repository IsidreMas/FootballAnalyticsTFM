# Script intended to gather dataframe filtering functions.

import pandas as pd

def time_window(tracking_dataframe, start, end, frame = False):

    if frame:
        try:
            return tracking_dataframe[(tracking_dataframe['Frame'] <= end) & (tracking_dataframe['Frame'] >= start)]
        except:
            return tracking_dataframe[(tracking_dataframe['End Frame'] <= end) & (tracking_dataframe['Start Frame'] >= start)]
    else:
        try:
            return tracking_dataframe[(tracking_dataframe['Time [s]'] <= end) & (tracking_dataframe['Time [s]'] >= start)]
        except:
            return tracking_dataframe[(tracking_dataframe['End Time [s]'] <= end) & (tracking_dataframe['Start Time [s]'] >= start)]
        

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

def possesion_filter(match_object, 
                     possesion_df=None, 
                     defense_df=None,
                     events_df=None, 
                     possesion_team = 'Home'):
    if not possesion_df:
        if possesion_team == 'Home':
            possesion_df = match_object.tracking_home
        else:
            possesion_df = match_object.tracking_away
    if not defense_df:
        if possesion_team == 'Home':
            defense_df = match_object.tracking_away
        else:
            defense_df = match_object.tracking_home
    if not events_df:
        events_df = match_object.events
    
    possesion = False
    number_of_possesions = 0
    possesions = {}

    for index, row in events_df.iterrows():
        if row['Team'] == possesion_team:
            if not possesion:
                number_of_possesions += 1
                possesions[number_of_possesions] = [row['Start Time [s]']]
                possesion = True
        else:
            if possesion:
                possesions[number_of_possesions].append(row['Start Time [s]'])
                possesion = False
    
    filtered_possesion = pd.DataFrame()
    for value in possesions.values():
        try:
            filtered_possesion = filtered_possesion.append(possesion_df[possesion_df['Time [s]'].between(value[0],value[1], inclusive = 'both')])
            defense_df = defense_df[~defense_df['Time [s]'].between(value[0],value[1], inclusive = 'both')]
        except IndexError:
            pass
    return filtered_possesion, defense_df

def ball_position_filter(match_object, 
                     home_df=None, 
                     away_df=None,
                     left_bound = None,
                     right_bound = None,
                     top_bound = None,
                     bottom_bound = None):
    if not any(home_df):
        home_df = match_object.tracking_home
    if not any(away_df):
        away_df = match_object.tracking_away
    
    if left_bound:
        home_df = home_df[home_df['ball_x']>=left_bound]
        away_df = away_df[away_df['ball_x']>=left_bound]
    if right_bound:
        home_df = home_df[home_df['ball_x']<=right_bound]
        away_df = away_df[away_df['ball_x']<=right_bound]
    if top_bound:
        home_df = home_df[home_df['ball_y']<=top_bound]
        away_df = away_df[away_df['ball_y']<=top_bound]
    if bottom_bound:
        home_df = home_df[home_df['ball_y']>=bottom_bound]
        away_df = away_df[away_df['ball_y']>=bottom_bound]
    
    return home_df, away_df

