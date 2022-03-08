#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  19 13:22:00 2022
@author: Isidre Mas Magre (GitHub: @IsidreMas)

#############################################################################################################
#Extended from the module Metrica_IO.py created by Laurie Shaw (@EightyFivePoint).				            #
#The original repository can be found at: https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking	#
#############################################################################################################

Module for reading and preprocessing tracking data from multiple sources into a standarized football 
tracking data format. Each function preprocess the tracking data to the same format independently 
from the source chosen, the purpose of this is that other modules can easily analyse and process the tracking data.

ON WORK: (An standard format still needs to be defined, for now the format in use is the metrica-sports format)

Dev guide: Each source is assumed to have the same format, in case a source has different formats exceptions in the 
case definitions must be made. The source is passed to the source-sensitive functions as an argument.

Example: function_name(data_source = 'metrica-sports')

***************************************** SOURCES CURRENTLY AVAILABLE ***************************************

'metrica-sports' - Data can be found at: https://github.com/metrica-sports/sample-data

"""

import pandas as pd
import csv
import numpy as np

def read_match_data(data_source,match_id):

    """
    Reads the tracking data from given data source and match identifiers and returns dataframes
    for the home team, away team and events.
  
    Parameters:

    data_source (string): Identifier of the data source, must be chosen from the available:
                            - 'metrica-sports'

    match_id: Identifier of the match from the data source.
  
    Returns:
    tracking_home, tracking_away, events: Dataframes with the tracking data read from source.
    """

    tracking_home = tracking_data(data_source,match_id,'Home')
    tracking_away = tracking_data(data_source,match_id,'Away')
    events = read_event_data(data_source,match_id)
    return tracking_home,tracking_away,events

def get_datadir(source):
    if source == 'metrica-sports':
        DATADIR = '../data/MetricaSportsSampleData/data'
    return DATADIR

def read_event_data(data_source,game_id):
    """
    Reads the events data from given data source and match identifiers and returns a dataframe
    for events.
  
    Parameters:

    data_source (string): Identifier of the data source, must be chosen from the available:
                            - 'metrica-sports'

    match_id: Identifier of the match from the data source.
  
    Returns:
    events: Dataframe with the events data read from source.
    """
    DATADIR = get_datadir(data_source)
    if data_source == 'metrica-sports':
        eventfile = f"/Sample_Game_{game_id}/Sample_Game_{game_id}_RawEventsData.csv"
        events = pd.read_csv('{}/{}'.format(DATADIR, eventfile)) # read data
    return events

def tracking_data(data_source,game_id,teamname):
    """
    Reads the tracking data from given data source and match identifiers and returns a dataframe
    for events.
  
    Parameters:

    data_source (string): Identifier of the data source, must be chosen from the available:
                            - 'metrica-sports'

    match_id (int): Identifier of the match from the data source.

    teamname (string): Name of the team to be read. 
  
    Returns:
    tracking: Dataframe with the tracking data read from source.
    """
    DATADIR = get_datadir(data_source)

    if data_source == 'metrica-sports':
        teamfile = f"/Sample_Game_{game_id}/Sample_Game_{game_id}_RawTrackingData_{teamname}_Team.csv"
        # First:  deal with file headers so that we can get the player names correct
        csvfile =  open('{}/{}'.format(DATADIR, teamfile), 'r') # create a csv file reader
        reader = csv.reader(csvfile) 
        teamnamefull = next(reader)[3].lower()
        print(f"Reading team: {teamnamefull}")
        # construct column names
        jerseys = [x for x in next(reader) if x != ''] # extract player jersey numbers from second row
        columns = next(reader)
        for i, j in enumerate(jerseys): # create x & y position column headers for each player
            columns[i*2+3] = "{}_{}_x".format(teamname, j)
            columns[i*2+4] = "{}_{}_y".format(teamname, j)
        columns[-2] = "ball_x" # column headers for the x & y positions of the ball
        columns[-1] = "ball_y"
        # Second: read in tracking data and place into pandas Dataframe
        tracking = pd.read_csv('{}/{}'.format(DATADIR, teamfile), names=columns, index_col='Frame', skiprows=3)
    return tracking

def merge_tracking_data(home,away):
    """
    Reads the events data from given data source and match identifiers and returns a dataframe
    for events.
  
    Parameters:

    home: Dataframe of the home team.

    away: Dataframe of the away team.
  
    Returns:
    dataframe : Dataframe with the joined tracking data read from source.
    """
    return home.drop(columns=['ball_x', 'ball_y']).merge( away, left_index=True, right_index=True )
    
def to_metric_coordinates(data,data_source,field_dimen=(106.,68.)):
    """
    Reads the events data from given data source and match identifiers and returns a dataframe
    for events.
  
    Parameters:

    data: Dataframe containing raw tracking data read from tracking_data().

    data_source (string): Identifier of the data source, must be chosen from the available:
                            - 'metrica-sports'
    
    field_dimen: Tuple containing the field dimensions (length, width) in the desired units.
  
    Returns:
    dataframe: Dataframe with the tracking data transformed to metric units.
    """

    if data_source == 'metrica-sports':
        x_columns = [c for c in data.columns if c[-1].lower()=='x']
        y_columns = [c for c in data.columns if c[-1].lower()=='y']
        data[x_columns] = ( data[x_columns]-0.5 ) * field_dimen[0]
        data[y_columns] = -1 * ( data[y_columns]-0.5 ) * field_dimen[1]
        ''' 
        ------------ ***NOTE*** ------------
        Metrica actually define the origin at the *top*-left of the field, not the bottom-left, as discussed in the YouTube video. 
        I've changed the line above to reflect this. It was originally:
        data[y_columns] = ( data[y_columns]-0.5 ) * field_dimen[1]
        ------------ ********** ------------
        '''
    return data

def to_single_playing_direction(home,away,events):
    """
    Flip coordinates in second half so that each team always shoots in the same direction through the match.
  
    Parameters:

    home: Dataframe with home team tracking data.

    away: Dataframe with away team tracking data.

    events: Dataframe with events data.
  
    Returns:
    dataframe: Dataframe with flipped x coordinates.
    """
    for tracking in [home,away,events]:
        second_half_idx = tracking.Period.values.searchsorted(1.5, side='right')+1
        columns = [c for c in tracking.columns if c[-1].lower() in ['x','y']]
        tracking.loc[second_half_idx:,columns] *= -1
    return home,away,events


def find_players(team):
    return np.unique( [ c.split('_')[0]+'_'+c.split('_')[1] for c in team.columns if ('x' in c.split('_') and c.split('_')[0] != 'ball') ] )

# Functions below not reviewed from the original Laurie Shaw's version.
def find_playing_direction(team,teamname):
    '''
    Find the direction of play for the team (based on where the goalkeepers are at kickoff). +1 is left->right and -1 is right->left
    '''  
    GK_column_x = teamname+"_"+find_goalkeeper(team)+"_x"
    # +ve is left->right, -ve is right->left
    return -np.sign(team.iloc[0][GK_column_x])
    
def find_goalkeeper(team):
    '''
    Find the goalkeeper in team, identifying him/her as the player closest to goal at kick off
    ''' 
    x_columns = [c for c in team.columns if c[-2:].lower()=='_x' and c[:4] in ['Home','Away']]
    GK_col = team.iloc[0][x_columns].abs().idxmax(axis=1)
    return GK_col.split('_')[1]
