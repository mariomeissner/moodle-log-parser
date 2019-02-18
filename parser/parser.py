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
        self.log.sort_values("Hora", inplace=True)
        self.indices = self.log["pseudonimo"].unique()
        self.output = pd.DataFrame(index=self.indices)

        # Create deltatime differences
        self.log["HoraDelta"] = self.log["Hora"] - self.log["Hora"].shift(1)
        # Session generation: https://stackoverflow.com/questions/17547391/session-generation-from-log-file-analysis-with-pandas
    def set_course_periods(self):
        '''
        Set the time periods that exist in the course, 
        which will define how student action distribution is computed. 
        For example, a course with three midterms, these could be the split
        point for three periods in the course. 
        Default is months.
        '''
        pass

    def add_total_action_counts(self):
        '''
        Adds a new column for each action in the log
        counting the number of times each student has performed each action
        in total.
        '''
        pass

    def add_total_session_counts(self):

        pass



if __name__ == "__main__":

    parser = Parser("./data/primaria.csv")
    exit()


