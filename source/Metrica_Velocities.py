#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:52:19 2020

Module for measuring player velocities, smoothed using a Savitzky-Golay filter, with Metrica tracking data.

Data can be found at: https://github.com/metrica-sports/sample-data

@author: Laurie Shaw (@EightyFivePoint)

"""
from locale import normalize
import numpy as np
import scipy.signal as signal

def calc_player_velocities(team, smoothing=True, filter_='Savitzky-Golay', window=7, polyorder=1, maxspeed = 12):
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
    # remove any velocity data already in the dataframe
    team = remove_player_velocities(team)
    
    # Get the player ids
    player_ids = np.unique( [ c.split('_')[0]+'_'+c.split('_')[1] for c in team.columns if c[:4] in ['Home','Away'] ] )

    # Calculate the timestep from one frame to the next. Should always be 0.04 within the same half
    dt = team['Time [s]'].diff()
    
    # index of first frame in second half
    second_half_idx = team.Period.values.searchsorted(1.5, side='right')+1
    
    # estimate velocities for players in team
    for player in player_ids: # cycle through players individually
        # difference player positions in timestep dt to get unsmoothed estimate of velicity
        vx = (team[player+"_x"].diff()-team[player+"_x"].diff(periods=-1)) / (2*dt)
        vy = (team[player+"_y"].diff()-team[player+"_y"].diff(periods=-1)) / (2*dt)

        if maxspeed>0:
            # remove unsmoothed data points that exceed the maximum speed (these are most likely position errors)
            raw_speed = np.sqrt( vx**2 + vy**2 )
            vx[ raw_speed>maxspeed ] = np.nan
            vy[ raw_speed>maxspeed ] = np.nan
            
        if smoothing:
            if filter_=='Savitzky-Golay':
                # calculate first half velocity
                vx.loc[:second_half_idx] = signal.savgol_filter(vx.loc[:second_half_idx],window_length=window,polyorder=polyorder)
                vy.loc[:second_half_idx] = signal.savgol_filter(vy.loc[:second_half_idx],window_length=window,polyorder=polyorder)        
                # calculate second half velocity
                vx.loc[second_half_idx:] = signal.savgol_filter(vx.loc[second_half_idx:],window_length=window,polyorder=polyorder)
                vy.loc[second_half_idx:] = signal.savgol_filter(vy.loc[second_half_idx:],window_length=window,polyorder=polyorder)
            elif filter_=='moving average':
                ma_window = np.ones( window ) / window 
                # calculate first half velocity
                vx.loc[:second_half_idx] = np.convolve( vx.loc[:second_half_idx] , ma_window, mode='same' ) 
                vy.loc[:second_half_idx] = np.convolve( vy.loc[:second_half_idx] , ma_window, mode='same' )      
                # calculate second half velocity
                vx.loc[second_half_idx:] = np.convolve( vx.loc[second_half_idx:] , ma_window, mode='same' ) 
                vy.loc[second_half_idx:] = np.convolve( vy.loc[second_half_idx:] , ma_window, mode='same' ) 
                
        
        # put player speed in x,y direction, and total speed back in the data frame
        team[player + "_vx"] = vx
        team[player + "_vy"] = vy
        team[player + "_speed"] = np.sqrt( vx**2 + vy**2 )
        team[player + "_distance"] = np.sqrt( team[player+"_x"].diff()**2 + team[player+"_y"].diff()**2 ).cumsum()

    return team

def remove_player_velocities(team):
    # remove player velocoties and acceleeration measures that are already in the 'team' dataframe
    columns = [c for c in team.columns if c.split('_')[-1] in ['vx','vy','ax','ay','speed','acceleration','distance']] # Get the player ids
    team = team.drop(columns=columns)
    return team
def remove_player_normals(team):
    # remove player normals and acceleeration measures that are already in the 'team' dataframe
    columns = [c for c in team.columns if c.split('_')[-1] in ['normx','normy']] # Get the player ids
    team = team.drop(columns=columns)
    return team

def player_norm_positions(team):
    # remove any normalization data ifalready in the dataframe
    team = remove_player_normals(team)
    # Get the player ids
    player_ids = np.unique( [ c.split('_')[0]+'_'+c.split('_')[1] for c in team.columns if c[:4] in ['Home','Away'] ] )

    # index of first frame in second half
    second_half_idx = team.Period.values.searchsorted(1.5, side='right')+1

    #Initialitation of necessary variables to normalize positions 
    team['team_cmx']=0
    team['team_cmy']=0
    team['team_cmx2']=0
    team['team_cmy2']=0
    team['num_team']=0

    # estimate normal positions for players in team
    for player in player_ids: # cycle through players individually
        team['team_cmx']=team['team_cmx'].add(team[player+'_x'], fill_value = 0)
        team['team_cmy']=team['team_cmy'].add(team[player+'_y'], fill_value = 0)
        team['team_cmx2']=team['team_cmx2'].add(team[player+'_x']**2, fill_value = 0)
        team['team_cmy2']=team['team_cmy2'].add(team[player+'_y']**2, fill_value = 0)
        team['num_team']=team['num_team'].add(team[player + '_x']/team[player + '_x'], fill_value = 0)
    
    team['team_meanx']=team['team_cmx']/team['num_team']
    team['team_meany']=team['team_cmy']/team['num_team']
    team['team_varx']=team['team_cmx2']/team['num_team']-team['team_meanx']**2
    team['team_vary']=team['team_cmy2']/team['num_team']-team['team_meany']**2
    team['team_sdx']=team['team_varx']**0.5
    team['team_sdy']=team['team_vary']**0.5

    for player in player_ids:
        # put player normal position in x,y direction, and total speed back in the data frame
        #if (team[player+'_x']!="NaN") and (team[player+'_y']!="NaN"):
            team[player + "_normx"] = (team[player + "_x"]-team['team_meanx'])/team['team_sdx']
            team[player + "_normy"] = (team[player + "_y"]-team['team_meany'])/team['team_sdy']


    return team