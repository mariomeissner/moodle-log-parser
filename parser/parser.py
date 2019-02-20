import pprint
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from math import isnan


class Parser():

    def __init__(self, csv_path):
        '''
        Creates a new parser with log data taken from the csv
        found in the `csv_path`. 
        '''
        self.log = pd.read_csv(csv_path, parse_dates=[0], infer_datetime_format=True)
        self.log.sort_values(["pseudonimo", "Hora"], inplace=True)
        index = pd.Index(self.log["pseudonimo"].unique(), name='pseudonimo')
        self.output = pd.DataFrame(index=index)
        #self.names = ["ID"] TODO: I probably don't need this.

        # Create deltatime differences
        self.log["HoraDelta"] = self.log["Hora"] - self.log.shift(1)["Hora"]


    def add_total_action_counts(self, actions=None):
        '''
        Adds a new column for each action in the log
        counting the number of times each student has performed each action
        in total.
        '''
        
        # Number of each action performed by each user
        action_counts = self.log[["pseudonimo","Nombre evento"]].groupby(
            ["pseudonimo", "Nombre evento"]).size().unstack(fill_value=0)

        # Distinct actions present in the log# Distinct actions present in the log
        #self.actions = set(list(self.action_counts.index.get_level_values(1)))

        # Merge action counts with output
        self.output = self.output.merge(action_counts, on='pseudonimo')

    def add_total_session_counts(self, name, delta=timedelta(minutes=20)):
        '''
        Adds total number of sessions each student has performed.
        '''

        #self.names.append(name)
        self.log["NumSesion"] = self.log.groupby("pseudonimo")["HoraDelta"].apply(
            lambda t: (t >= delta).cumsum())
        self.output[name] = self.log.groupby("pseudonimo")["NumSesion"].max() + 1


    def write_file(self, output_path):

        self.output.to_csv(output_path)


if __name__ == "__main__":

    parser = Parser("./data/primaria.csv")
    parser.add_total_action_counts()
    parser.add_total_session_counts('session counts')


