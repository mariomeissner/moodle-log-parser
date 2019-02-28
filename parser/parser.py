import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from math import isnan
# Pandas settings
pd.options.display.max_rows = 200

class Parser():

    def __init__(self, csv_path):
        '''
        Creates a new parser with log data taken from the csv
        found in the `csv_path`. 
        '''

        self.log = pd.read_csv(csv_path, parse_dates=[0], infer_datetime_format=True)
        # Sort by students and then ascending time
        self.log.sort_values(["pseudonimo", "Hora"], inplace=True)
        index = pd.Index(self.log["pseudonimo"].unique(), name='pseudonimo')
        self.output = pd.DataFrame(index=index)
        # Create deltatime differences
        self.log["HoraDelta"] = self.log["Hora"] - self.log.shift(1)["Hora"]


    def _group_by_periods(self, row_id, period_start, period_duration):
        row = self.log.loc[row_id]
        if row["Hora"] < period_start: 
            return 0
        else: 
            return math.ceil((row["Hora"] - period_start) / period_duration)


    def add_actions_per_type(self, actions=None):
        '''
        Adds a new column for each action in the log
        counting the number of times each student has performed each action
        in total.
        '''
        
        # Number of each action performed by each user
        action_counts = self.log[["pseudonimo","Nombre evento"]].groupby(
            ["pseudonimo", "Nombre evento"]).size().unstack(fill_value=0)
        # Merge action counts with output
        self.output = self.output.merge(action_counts, on='pseudonimo')


    def add_total_sessions(self, name, delta=timedelta(minutes=20)):
        '''
        Adds total number of sessions each student has performed.
        '''

        self.log["NumSesion"] = self.log.groupby("pseudonimo")["HoraDelta"].apply(
            lambda t: (t >= delta).cumsum())
        self.output[name] = self.log.groupby("pseudonimo")["NumSesion"].max() + 1


    def add_actions_per_period(self, period_start, period_duration):

        self.period_groups = self.log.groupby(
            lambda row_id: self._group_by_periods(row_id, period_start, period_duration))

        self.periods = ((self.log["Hora"] - period_start) // period_duration) + 1
        self.periods[self.periods < 0] = 0
        self.log["Periodo"] = self.periods
        self.counts = self.log.groupby(["pseudonimo","Periodo"]).size().unstack()
        self.output = self.output.merge(self.counts, on="pseudonimo")


    def add_actions_per_forum(self):
        log_context = self.log[["pseudonimo","Contexto del evento"]]
        log_forums = log_context.loc[self.log["Componente"] == "Foro"]
        per_forum = log_forums.groupby(["pseudonimo","Contexto del evento"]).size().unstack()
        self.output = self.output.merge(per_forum, on='pseudonimo')


    def write_file(self, output_path):

        self.output.to_csv(output_path)


if __name__ == "__main__":

    parser = Parser("./data/primaria.csv")
    parser.add_actions_per_type()
    parser.add_total_sessions('session counts')
    parser.add_actions_per_period(datetime(2017,9,1), timedelta(days=30))
    parser.add_actions_per_forum()


