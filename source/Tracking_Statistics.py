import numpy as np
import pandas as pd


def bivariate_normal_distribution(tracking_data, players = None, ball = False):
    if not ball:
        for player in players:
            if np.isnan(tracking_data[player + '_x'].mean()): # Double mean calculation, maybe fix this
                players = players[players != player]
        dist_stats = pd.DataFrame({'player': [player.split('_')[1] for player in players]})
    else:
        players = ['ball']
        dist_stats = pd.DataFrame()

    
    dist_stats['x_mean'] = [tracking_data[player+'_x'].mean() for player in players]
    dist_stats['y_mean'] = [tracking_data[player+'_y'].mean() for player in players]
    dist_stats['normx_mean'] = [tracking_data[player+'_normx'].mean() for player in players]
    dist_stats['normy_mean'] = [tracking_data[player+'_normy'].mean() for player in players]

    if len(tracking_data) > 1:
        cov_matrices = [tracking_data[[player+'_x',player+'_y']].cov() for player in players]
        values, vectors = np.linalg.eig(cov_matrices)
        dist_stats['cov_x_std'] = np.sqrt(values[:,0])
        dist_stats['cov_y_std'] = np.sqrt(values[:,1])
        dist_stats['cov_angle'] = np.arctan(vectors[:,0,1]/vectors[:,0,0])
        cov_matrices = [tracking_data[[player+'_normx',player+'_normy']].cov() for player in players]
        values, vectors = np.linalg.eig(cov_matrices)
        dist_stats['cov_normx_std'] = np.sqrt(values[:,0])
        dist_stats['cov_normy_std'] = np.sqrt(values[:,1])
        dist_stats['cov_norm_angle'] = np.arctan(vectors[:,0,1]/vectors[:,0,0])
        dist_stats['x_std'] = [tracking_data[player+'_x'].std() for player in players]
        dist_stats['y_std'] = [tracking_data[player+'_y'].std() for player in players]
        dist_stats['normx_std'] = [tracking_data[player+'_normx'].std() for player in players]
        dist_stats['normy_std'] = [tracking_data[player+'_normy'].std() for player in players]
    else:
        dist_stats['cov_x_std'] = 0
        dist_stats['cov_y_std'] = 0
        dist_stats['cov_angle'] = 0
        dist_stats['cov_normx_std'] = 0
        dist_stats['cov_normy_std'] = 0
        dist_stats['cov_norm_angle'] = 0
        dist_stats['x_std'] = 0
        dist_stats['y_std'] = 0
        dist_stats['normx_std'] = 0
        dist_stats['normy_std'] = 0

    return dist_stats
