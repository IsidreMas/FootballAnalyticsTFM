#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:52:19 2020

Module for measuring player velocities, smoothed using a Savitzky-Golay filter, with Metrica tracking data.

Data can be found at: https://github.com/metrica-sports/sample-data

@author: Laurie Shaw (@EightyFivePoint)

"""
import numpy as np
import scipy.signal as signal
from Tracking_Constants import *

def calc_player_velocities(team, players = None, smoothing=True, filter_='Savitzky-Golay', window=7, polyorder=1, maxspeed = 12):
    """ calc_player_velocities( tracking_data )
    
    Calculate player velocities in x & y direciton, and total player speed at each timestamp of the tracking data
    
    Parameters
    -----------
        team: the tracking DataFrame for home or away team
        smoothing: boolean variable that determines whether velocity measures are smoothed. Default is True.
        filter: type of filter to use when smoothing the velocities. Default is Savitzky-Golay, which fits a polynomial of order 'polyorder' to the data within each window
        window: smoothing window size in # of frames
        polyorder: order of the polynomial for the Savitzky-Golay filter. Default is 1 - a linear fit to the velcoity, so gradient is the acceleration
        maxspeed: the maximum speed that a player can realisitically achieve (in meters/second). Speed measures that exceed maxspeed are tagged as outliers and set to NaN. 
        
    Returns
    -----------
       team : the tracking DataFrame with columns for speed in the x & y direction and total speed added

    """
    # remove any cinematic data already in the dataframe
    team = remove_player_cinematics(team)
    
    # Get the player ids
    if not any(players):
        players = np.unique( [ c.split('_')[0]+'_'+c.split('_')[1] for c in team.columns if c[:4] in ['Home','Away'] ] )

    # Calculate the timestep from one frame to the next. Should always be 0.04 within the same half
    dt = team['Time [s]'].diff()
    players = np.append(players, "ball")
    
    # index of first frame in second half
    second_half_idx = team.Period.values.searchsorted(1.5, side='right')+1

    # Center of mass velocities
    vx = team["team_meanx"].diff() / dt
    vy = team["team_meany"].diff() / dt
    stdvx = team["team_sdx"].diff() / dt
    stdvy = team["team_sdy"].diff() / dt

    if maxspeed > 0:
        # remove unsmoothed data points that exceed the maximum speed (these are most likely position errors)
        raw_speed = np.sqrt(vx ** 2 + vy ** 2)
        vx[raw_speed > maxspeed] = np.nan
        vy[raw_speed > maxspeed] = np.nan

    if smoothing:
        if filter_ == 'Savitzky-Golay':
            vx = signal.savgol_filter(vx, window_length=window, polyorder=polyorder)
            vy = signal.savgol_filter(vy, window_length=window, polyorder=polyorder)
            stdvx = signal.savgol_filter(vx, window_length=window, polyorder=polyorder)
            stdvy = signal.savgol_filter(vy, window_length=window, polyorder=polyorder)
        elif filter_ == 'moving average':
            ma_window = np.ones(window) / window
            # calculate first half velocity
            vx = np.convolve(vx, ma_window, mode='same')
            vy = np.convolve(vy, ma_window, mode='same')
            stdvx = np.convolve(vx, ma_window, mode='same')
            stdvy = np.convolve(vy, ma_window, mode='same')

    team['team_meanvx'] = vx
    team['team_meanvy'] = vy
    team['team_stdvx'] = stdvx
    team['team_stdvy'] = stdvy



    
    # estimate velocities for players in team
    for player in players: # cycle through players individually
        # difference player positions in timestep dt to get unsmoothed estimate of velocity
        vx = team[player+"_x"].diff() / dt
        vy = team[player+"_y"].diff() / dt

        if maxspeed>0:
            # remove unsmoothed data points that exceed the maximum speed (these are most likely position errors)
            raw_speed = np.sqrt( vx**2 + vy**2 )
            vx[ raw_speed>maxspeed ] = np.nan
            vy[ raw_speed>maxspeed ] = np.nan
            
        if smoothing:
            if filter_=='Savitzky-Golay':
                # calculate first half velocity
                vx = signal.savgol_filter(vx,window_length=window,polyorder=polyorder)
                vy = signal.savgol_filter(vy,window_length=window,polyorder=polyorder)        
                # calculate second half velocity
                #vx.loc[second_half_idx:] = signal.savgol_filter(vx.loc[second_half_idx:],window_length=window,polyorder=polyorder)
                #vy.loc[second_half_idx:] = signal.savgol_filter(vy.loc[second_half_idx:],window_length=window,polyorder=polyorder)
            elif filter_=='moving average':
                ma_window = np.ones( window ) / window 
                # calculate first half velocity
                vx = np.convolve( vx , ma_window, mode='same' ) 
                vy = np.convolve( vy , ma_window, mode='same' )      
                # calculate second half velocity
                #vx.loc[second_half_idx:] = np.convolve( vx.loc[second_half_idx:] , ma_window, mode='same' ) 
                #vy.loc[second_half_idx:] = np.convolve( vy.loc[second_half_idx:] , ma_window, mode='same' ) 
                
        
        # put player speed in x,y direction, and total speed back in the data frame
        team[player + "_vx"] = vx
        team[player + "_vy"] = vy
        team[player + "_cmvx"] = vx - team["team_meanvx"]
        team[player + "_cmvy"] = vy - team["team_meanvy"]
        team[player + "_normvx"] = ((vx - team["team_meanvx"])*team["team_sdx"] - (team[player + "_x"]-team["team_meanx"])*team['team_stdvx'])/team["team_varx"]
        team[player + "_normvy"] = ((vy - team["team_meanvy"])*team["team_sdy"] - (team[player + "_y"]-team["team_meany"])*team['team_stdvy'])/team["team_vary"]
        team[player + "_speed"] = np.sqrt( vx**2 + vy**2 )
        team[player + "_speedcm"] = np.sqrt(team[player + "_cmvx"] ** 2 + team[player + "_cmvy"] ** 2)
        team[player + "_speednorm"] = np.sqrt(team[player + "_normvx"] ** 2 + team[player + "_normvy"] ** 2)

    return team

def remove_player_cinematics(team):
    # remove player velocoties and acceleeration measures that are already in the 'team' dataframe
    columns = [c for c in team.columns if c.split('_')[-1] in ['vx','vy','ax','ay','speed','acceleration','distance']] # Get the player ids
    team = team.drop(columns=columns)
    return team
def remove_player_normals(team):
    # remove player normals and acceleeration measures that are already in the 'team' dataframe
    columns = [c for c in team.columns if c.split('_')[-1] in ['normx','normy']] # Get the player ids
    team = team.drop(columns=columns)
    return team

def calc_player_norm_positions(team1, team2 = None, goalkeeper1 = None,
                               goalkeeper2 = None,
                               global_normalization = False,
                               normalize_goalkeeper = False):
    # remove any normalization data ifalready in the dataframe
    team1 = remove_player_normals(team1)
    # Get the player ids (REVISE THIS, MIGHT NOT WORK WITH OTHER DATA SOURCES/PLAYER IDS)
    team1_players_ids = np.unique( [ c.split('_')[0]+'_'+c.split('_')[1] for c in team1.columns if c[:4] in ['Home','Away'] ] )
    team2_players_ids = np.unique([c.split('_')[0] + '_' + c.split('_')[1] for c in team2.columns if
                                   c.split('_')[0] in team2.columns[4].split('_')[0]])
    #Initialitation of necessary variables to normalize positions 
    team1['team_cmx']=0
    team1['team_cmy']=0
    team1['team_cmx2']=0
    team1['team_cmy2']=0
    team1['num_team']=0

    # estimate normal positions for players in team1
    for player in team1_players_ids: # cycle through players individually
        if not normalize_goalkeeper:
            if int(player.split("_")[1]) != int(goalkeeper1):
                team1['team_cmx']=team1['team_cmx'].add(team1[player+'_x'], fill_value = 0)
                team1['team_cmy']=team1['team_cmy'].add(team1[player+'_y'], fill_value = 0)
                team1['team_cmx2']=team1['team_cmx2'].add(team1[player+'_x']**2, fill_value = 0)
                team1['team_cmy2']=team1['team_cmy2'].add(team1[player+'_y']**2, fill_value = 0)
                team1['num_team']=team1['num_team'].add(team1[player + '_x']/team1[player + '_x'], fill_value = 0)
        else:
            team1['team_cmx'] = team1['team_cmx'].add(team1[player + '_x'], fill_value=0)
            team1['team_cmy'] = team1['team_cmy'].add(team1[player + '_y'], fill_value=0)
            team1['team_cmx2'] = team1['team_cmx2'].add(team1[player + '_x'] ** 2, fill_value=0)
            team1['team_cmy2'] = team1['team_cmy2'].add(team1[player + '_y'] ** 2, fill_value=0)
            team1['num_team'] = team1['num_team'].add(team1[player + '_x'] / team1[player + '_x'], fill_value=0)
    if global_normalization:
        for player in team2_players_ids:  # cycle through players individually
            if not normalize_goalkeeper:
                if int(player.split("_")[1]) != int(goalkeeper2):
                    team1['team_cmx'] = team1['team_cmx'].add(team2[player + '_x'], fill_value=0)
                    team1['team_cmy'] = team1['team_cmy'].add(team2[player + '_y'], fill_value=0)
                    team1['team_cmx2'] = team1['team_cmx2'].add(team2[player + '_x'] ** 2, fill_value=0)
                    team1['team_cmy2'] = team1['team_cmy2'].add(team2[player + '_y'] ** 2, fill_value=0)
                    team1['num_team'] = team1['num_team'].add(team2[player + '_x'] / team2[player + '_x'], fill_value=0)
            else:
                team1['team_cmx'] = team1['team_cmx'].add(team2[player + '_x'], fill_value=0)
                team1['team_cmy'] = team1['team_cmy'].add(team2[player + '_y'], fill_value=0)
                team1['team_cmx2'] = team1['team_cmx2'].add(team2[player + '_x'] ** 2, fill_value=0)
                team1['team_cmy2'] = team1['team_cmy2'].add(team2[player + '_y'] ** 2, fill_value=0)
                team1['num_team'] = team1['num_team'].add(team2[player + '_x'] / team2[player + '_x'], fill_value=0)

    team1['team_meanx']=team1['team_cmx']/team1['num_team']
    team1['team_meany']=team1['team_cmy']/team1['num_team']
    team1['team_varx']=team1['team_cmx2']/team1['num_team']-team1['team_meanx']**2
    team1['team_vary']=team1['team_cmy2']/team1['num_team']-team1['team_meany']**2
    team1['team_sdx']=team1['team_varx']**0.5
    team1['team_sdy']=team1['team_vary']**0.5

    for player in team1_players_ids:
        # put player normal position in x,y direction, and total speed back in the data frame
        team1[player + "_normx"] = (team1[player + "_x"]-team1['team_meanx'])/team1['team_sdx']
        team1[player + "_normy"] = (team1[player + "_y"]-team1['team_meany'])/team1['team_sdy']

    for player in team2_players_ids:
        team1[player + "_normx"] = (team2[player + "_x"]-team1['team_meanx'])/team1['team_sdx']
        team1[player + "_normy"] = (team2[player + "_y"]-team1['team_meany'])/team1['team_sdy']

    team1["ball_normx"] = (team1["ball_x"]-team1["team_meanx"])/team1["team_sdx"]
    team1["ball_normy"] = (team1["ball_y"]-team1["team_meany"])/team1["team_sdy"]



    return team1