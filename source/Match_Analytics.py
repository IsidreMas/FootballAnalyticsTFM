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
  def __init__(self, name, data_source, match_id):
    self.name = name
    self.data_source = data_source
    self.match_id = match_id
    self.read_home_data(data_source=self.data_source, match_id=self.match_id)
    self.read_away_data(data_source=self.data_source, match_id=self.match_id)
    self.read_events_data(data_source=self.data_source, match_id=self.match_id)

  def process_all(self):
    """
    Wraps up all the methods and performs all the necessary processing for the tracking data.
    """
    print(f"The match {self.name} has been processed.")
  
  def read_home_data(self, data_source, match_id):
    """
    Reads the home data of a match from the data source.
    """
    self.tracking_home = io.read_match_data()
  def read_away_data(self, data_source, match_id):
    """
    Reads the away data of a match from the data source.
    """
    self.tracking_away = 1
  def read_events_data(self, data_source, match_id):
    """
    Reads the events data of a match from the data source.
    """
    self.events = 1