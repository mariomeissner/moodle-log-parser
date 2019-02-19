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
        self.indices = self.log["pseudonimo"].unique()
        self.output = pd.DataFrame(index=self.indices)
        self.names = ["ID"]

        # Create deltatime differences
        self.log["HoraDelta"] = self.log["Hora"] - self.log.shift(1)["Hora"]


    def add_total_action_counts(self, names=None):
        '''
        Adds a new column for each action in the log
        counting the number of times each student has performed each action
        in total.
        @params:
        names: Dict of mappings to 
        '''
        pass


    def add_total_session_counts(self, name, delta=timedelta(minutes=20)):
        '''
        Adds total number of sessions each student has performed.
        '''

        self.names.append(name)
        self.log["NumSesion"] = self.log.groupby("pseudonimo")["HoraDelta"].apply(
            lambda t: (t >= delta).cumsum())
        self.output["NumSessions"] = self.log.groupby("pseudonimo")["NumSesion"].max() + 1


    def write_file(self, output_path):

        self.output.to_csv(output_path)





if __name__ == "__main__":

    parser = Parser("./data/primaria.csv")
    exit()


