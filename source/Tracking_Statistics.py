import numpy as np
import pandas as pd
from Tracking_Constants import *
from Tracking_Filters import time_window


def bivariate_normal_distribution(tracking_data, players = None, ball = False, against = False):
    if ball:
        players = ['ball']
        dist_stats = pd.DataFrame()
    else:
        
        for player in players:
            if np.isnan(tracking_data[player + '_normx'].mean()): # Double mean calculation, maybe fix this
                players = players[players != player]
        dist_stats = pd.DataFrame({'player_number': [player.split('_')[1] for player in players]})
        dist_stats['player'] = players
    if not against:
        dist_stats['x_mean'] = [tracking_data[player+'_x'].mean() for player in players]
        dist_stats['y_mean'] = [tracking_data[player+'_y'].mean() for player in players]
        dist_stats['distance'] = [np.sqrt(tracking_data[player+'_x'].diff()**2+tracking_data[player+'_x'].diff()**2).sum() for player in players]
    dist_stats['normx_mean'] = [tracking_data[player+'_normx'].mean() for player in players]
    dist_stats['normy_mean'] = [tracking_data[player+'_normy'].mean() for player in players]

    if len(tracking_data) > 1:
        if not against:
            cov_matrices = [tracking_data[[player+'_x',player+'_y']].cov() for player in players]
            values, vectors = np.linalg.eig(cov_matrices)
            dist_stats['cov_x_std'] = np.sqrt(values[:,0])
            dist_stats['cov_y_std'] = np.sqrt(values[:,1])
            dist_stats['cov_angle'] = np.arctan(vectors[:,0,1]/vectors[:,0,0])
            dist_stats['x_std'] = [tracking_data[player+'_x'].std() for player in players]
            dist_stats['y_std'] = [tracking_data[player+'_y'].std() for player in players]
        cov_matrices = [tracking_data[[player+'_normx',player+'_normy']].cov() for player in players]
        values, vectors = np.linalg.eig(cov_matrices)
        dist_stats['cov_normx_std'] = np.sqrt(values[:,0])
        dist_stats['cov_normy_std'] = np.sqrt(values[:,1])
        dist_stats['cov_norm_angle'] = np.arctan(vectors[:,0,1]/vectors[:,0,0])
        dist_stats['normx_std'] = [tracking_data[player+'_normx'].std() for player in players]
        dist_stats['normy_std'] = [tracking_data[player+'_normy'].std() for player in players]
    else:
        if not against:
            dist_stats['cov_x_std'] = 0
            dist_stats['cov_y_std'] = 0
            dist_stats['cov_angle'] = 0
            dist_stats['x_std'] = 0
            dist_stats['y_std'] = 0
        dist_stats['cov_normx_std'] = 0
        dist_stats['cov_normy_std'] = 0
        dist_stats['cov_norm_angle'] = 0
        dist_stats['normx_std'] = 0
        dist_stats['normy_std'] = 0

    return dist_stats

def histogram(tracking_data, 
              players=None, 
              ball=False, 
              normalised=None, 
              field_dimen=None, 
              binsx=None, 
              binsy=None,
              return_dicts = True,
              **kwargs):
    if ball:
        if normalised:
            positions_x = tracking_data['ball_normx']
            positions_y = tracking_data['ball_normy']
        else:
            positions_x = tracking_data['ball_x']
            positions_y = tracking_data['ball_y']
    else:
        positions_x = pd.Series(dtype='float')
        positions_y = pd.Series(dtype='float')
        if normalised:
            for player in players:
                positions_x = pd.concat([positions_x, tracking_data[player + '_normx']])
                positions_y = pd.concat([positions_y, tracking_data[player + '_normy']])
        else:
            for player in players:
                positions_x = pd.concat([positions_x, tracking_data[player + '_x']])
                positions_y = pd.concat([positions_y, tracking_data[player + '_y']])
    if field_dimen:
        half_width = field_dimen[0]/2
        half_height = field_dimen[1]/2
    elif normalised:
        half_width = 3
        half_height = 3
        if not binsx:
            binsx = 100
        if not binsy:
            binsy = 100
    else:
        half_width = HALF_FIELD_WIDTH
        half_height = HALF_FIELD_HEIGHT
        if not binsx:
            binsx = int(FIELD_DIMENSIONS[0])
        if not binsy:
            binsy = int(FIELD_DIMENSIONS[1])

    xhist, xedges = np.histogram(positions_x, range = (-half_width,half_width), bins=binsx, **kwargs)
    yhist, yedges = np.histogram(positions_y, range = (-half_height,half_height), bins=binsy, **kwargs)
    if return_dicts:
        return {'top_x':xhist, 'bottom_x':xhist*0, 'left_x':xedges[:-1], 'right_x':xedges[1:]}, {'right_y':yhist, 'left_y':yhist*0, 'bottom_y':yedges[:-1], 'top_y':yedges[1:]}
    else:
        return xhist, yhist, xedges, yedges
        