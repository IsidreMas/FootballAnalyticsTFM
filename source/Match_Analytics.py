#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  19 13:22:00 2022
@author: Isidre Mas Magre (GitHub: @IsidreMas)

This module defines a class to process tracking data for a single match. Eventually
we would like to process many Match instances to obtain the necessary data to train 
a ML model or do statistics with more than one game.

"""

# Third party modules
import pandas as pd
import csv as csv
import numpy as np
# Project specific modules
import Tracking_IO as io

class Match:
  def __init__(self, data_source, match_id, name = 'Default_name', field_dimen = (106.,68.)):
    self.name = name
    self.data_source = data_source
    self.match_id = match_id
    self.read_match_data(data_source=self.data_source, match_id=self.match_id)
    self.tracking_home = io.to_metric_units(self.tracking_home,data_source = data_source,field_dimen = field_dimen)
    self.tracking_away = io.to_metric_units(self.tracking_away, data_source = data_source, field_dimen = field_dimen)
    self.events = io.to_metric_units(self.events, data_source = data_source, field_dimen = field_dimen)
    self.tracking_home, self.tracking_away, self.events = io.to_single_playing_direction(self.tracking_home, self.tracking_away, self.events)

  def process_all(self):
    """
    Wraps up all the methods and performs all the necessary processing for the tracking data.
    """
    print(f"The match {self.name} has been processed.")
  
  def read_match_data(self, data_source, match_id):
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
    self.tracking_home, self.tracking_away, self.events = io.read_match_data(data_source, match_id)