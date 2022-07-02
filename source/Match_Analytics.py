#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  19 13:22:00 2022
@author: Isidre Mas Magre (GitHub: @IsidreMas)

This module defines a class to process tracking data for a single match. Eventually
we would like to process many Match instances to obtain the necessary data to train 
a ML model or do statistics with more than one game.

"""
import numpy as np

# Project modules
import Tracking_IO as io
import Tracking_Dynamics as dyn
import Tracking_Visualization as vis
from Tracking_Constants import *
from Tracking_Filters import filter_dead_time

class Match:
  def __init__(self, 
              data_source, 
              match_id=None, 
              name=None, 
              field_dimen=FIELD_DIMENSIONS, 
              home_color="red", 
              away_color="blue", 
              preprocess=True, 
              verbose = True,
              metadata_path=None,
              tracking_path=None,
              home_path = None,
              away_path = None,
              events_path=None,
              filter_dead_time=True,
              global_normalization = False,
              normalize_goalkeeper = False ):
    if match_id:
      self.match_id = match_id
    else:
      self.match_id = 0
    if name:
      self.name = name
    else:
      self.name = str(self.match_id)
    self.data_source = data_source
    self.field_dimen = field_dimen
    self.global_normalization = global_normalization
    self.normalize_goalkeeper = normalize_goalkeeper
    if verbose:
      print(f"Initializing match: {self.name}\n")
    self.read_match_data(data_source=self.data_source, 
                         match_id=self.match_id,
                         metadata_path = metadata_path,
                         tracking_path = tracking_path,
                         events_path = events_path,
                         home_path = home_path,
                         away_path = away_path)
    self.preprocessed = False
    if self.data_source == "tactics":
        self.preprocessed = True
        self.home_goalkeeper = io.find_goalkeeper(self.tracking_home)
        self.away_goalkeeper = io.find_goalkeeper(self.tracking_away)
        print(self.home_goalkeeper)
        print(self.away_goalkeeper)
    self.home_players = io.find_players(self.tracking_home)
    self.away_players = io.find_players(self.tracking_away)
    self.all_players = np.concatenate([self.home_players, self.away_players])
    self.home_color = home_color
    self.away_color = away_color
    self.filter_dead_time = filter_dead_time
    if preprocess:
      self.preprocess()

  def preprocess(self):
    """
    Wraps up all the methods and performs all the predefined preprocessing for the tracking data.
    """
    # Basic data preprocessing
    if not self.preprocessed:
      self.tracking_home = io.to_metric_coordinates(self.tracking_home,data_source = self.data_source, field_dimen = self.field_dimen)
      self.tracking_away = io.to_metric_coordinates(self.tracking_away, data_source = self.data_source, field_dimen = self.field_dimen)
      self.events = io.to_metric_coordinates(self.events, data_source = self.data_source, field_dimen = self.field_dimen)
      self.tracking_home, self.tracking_away, self.events = io.to_single_playing_direction(self.tracking_home, self.tracking_away, self.events)
      self.home_goalkeeper = io.find_goalkeeper(self.tracking_home)
      self.away_goalkeeper = io.find_goalkeeper(self.tracking_away)
      print(self.home_goalkeeper)
      print(self.away_goalkeeper)
      self.calculate_player_normals()
      self.calculate_player_velocities()
      self.preprocessed = True
      if self.filter_dead_time:
        self.ranges = filter_dead_time(self)
      print('Match preprocessed successfully.\n')
    return self
  
  def read_match_data(self, data_source, match_id, metadata_path, tracking_path, events_path, home_path, away_path):
    """
    Reads the tracking data from given data source and match identifiers and defines atributte dataframes
    for the home team, away team and events.
  
    Parameters:

    data_source (string): Identifier of the data source, must be chosen from the available:
                            - 'metrica-sports'

    match_id: Identifier of the match from the data source.
  
    Defines:
    self.tracking_home, self.tracking_away, self.events: Dataframes with the tracking data read from source.
    """
    self.tracking_home, self.tracking_away, self.events = io.read_match_data(data_source, 
                                                                             match_id, 
                                                                             metadata_path, 
                                                                             tracking_path, 
                                                                             events_path,
                                                                             home_path,
                                                                             away_path)
  
  
  def calculate_player_velocities(self):
    self.tracking_home = dyn.calc_player_velocities(self.tracking_home, players=self.home_players)
    self.tracking_away = dyn.calc_player_velocities(self.tracking_away, players=self.away_players)
  
  def calculate_player_normals(self):
    self.tracking_away = dyn.calc_player_norm_positions(team1 = self.tracking_away,
                                                        team2 = self.tracking_home,
                                                        goalkeeper1 = self.away_goalkeeper,
                                                        goalkeeper2 = self.home_goalkeeper,
                                                        global_normalization = self.global_normalization,
                                                        normalize_goalkeeper = self.normalize_goalkeeper)
    self.tracking_home = dyn.calc_player_norm_positions(team1 = self.tracking_home,
                                                        team2= self.tracking_away,
                                                        goalkeeper1 = self.home_goalkeeper,
                                                        goalkeeper2 = self.away_goalkeeper,
                                                        global_normalization = self.global_normalization,
                                                        normalize_goalkeeper = self.normalize_goalkeeper)