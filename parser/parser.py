import pandas as pd
from datetime import datetime, timedelta

# Pandas settings
pd.options.display.max_rows = 200


class Parser:
    def __init__(
        self,
        csv_path,
        date_col=0,
        name_col=5,
        event_col=3,
        component_col=2,
        context_col=1,
        index_dtype=str,
    ):
        """
        Creates a new parser with log data taken from the csv
        found in the `csv_path`. 
        """

        # Load csv with pandas
        self.log = pd.read_csv(
            csv_path,
            parse_dates=[date_col],
            infer_datetime_format=True,
            # encoding="ascii",
        )

        # Get colnames
        self.date, self.name, self.event, self.component, self.context = self.log.columns.values[
            [date_col, name_col, event_col, component_col, context_col]
        ]

        # Get index dtype
        self.index_dtype = index_dtype

        # Sort by students and then ascending time
        self.log.sort_values([self.name, self.date], inplace=True)
        index = pd.Index(self.log[self.name].unique(), name=self.name)
        self.output = pd.DataFrame(index=index)
        # Create deltatime differences
        self.log["delta"] = self.log[self.date] - self.log.shift(1)[self.date]

    def add_event_counts(
        self,
        prefix,
        period,
        event_filter=None,
        component_filter=None,
        clip_val=20,
    ):
        """
        Adds a new column for each event in the log
        counting the number of times each student has performed each event
        in total.
        """

        log = self.log

        # Filters
        if event_filter:
            mask = log[self.event].apply(
                lambda c: any(keyword in c for keyword in event_filter)
            )
            log = log[mask]

        if component_filter:
            mask = log[self.component].apply(
                lambda c: any(keyword in c for keyword in component_filter)
            )
            log = log[mask]

        # Apply period
        mask = log[self.date].apply(lambda c: c >= period[0] and c <= period[1])
        log = log[mask]

        # Number of each event performed by each user
        event_counts = (
            log[[self.name, self.event]]
            .groupby([self.name, self.event])
            .size()
            .unstack(fill_value=0)
        )

        # Rename columns
        event_counts = event_counts.add_prefix(prefix)

        # Clip long column names
        if clip_val:
            for i, name in enumerate(event_counts.columns.values):
                event_counts.columns.values[i] = name[:clip_val]

        # Merge event counts with output
        self.output = self.output.merge(event_counts, on=self.name)

    def add_component_counts(
        self, prefix, period, event_filter=None, component_filter=None
    ):
        """
        A useful docstring goes here.
        """

        log = self.log

        # Filters
        if event_filter:
            mask = log[self.event].apply(
                lambda c: any(keyword in c for keyword in event_filter)
            )
            log = log[mask]

        if component_filter:
            mask = log[self.component].apply(
                lambda c: any(keyword in c for keyword in component_filter)
            )
            log = log[mask]

        # Apply period
        mask = log[self.date].apply(lambda c: c >= period[0] and c <= period[1])
        log = log[mask]

        # Number of each event performed by each user
        component_counts = (
            log[[self.name, self.component]]
            .groupby([self.name, self.component])
            .size()
            .unstack(fill_value=0)
        )

        # Rename columns
        component_counts = component_counts.add_prefix(prefix)

        # Merge component counts with output
        self.output = self.output.merge(component_counts, on=self.name)

    def add_session_counts(self, colname, period, delta=timedelta(minutes=20)):
        """
        Adds total number of sessions each student has performed.
        """

        # Apply period
        mask = self.log[self.date].apply(
            lambda c: c >= period[0] and c <= period[1]
        )
        log = self.log[mask]

        # Compute session number (max + 1 will be number of sessions)
        self.log["session_number"] = log.groupby(self.name)["delta"].apply(
            lambda t: (t >= delta).cumsum()
        )

        # Save
        self.output[colname] = (
            self.log.groupby(self.name)["session_number"].max() + 1
        )

    def add_events_per_forum(
        self, prefix, period, component_name="Foro", clip_val=20
    ):

        # Get events per forum
        log_context = self.log[[self.name, self.context]]
        log_forums = log_context.loc[self.log[self.component] == component_name]
        per_forum = (
            log_forums.groupby([self.name, self.context])
            .size()
            .unstack(fill_value=0)
        )

        # Rename
        per_forum = per_forum.add_prefix(prefix)

        # Clip long column names
        if clip_val:
            for i, name in enumerate(per_forum.columns.values):
                per_forum.columns.values[i] = name[:clip_val]

        # Save
        self.output = self.output.merge(per_forum, on=self.name)

    def add_scores(self, csv_path, name_col=0, score_filter=None, na_scores=[]):

        scores = pd.read_csv(csv_path, na_values=na_scores)
        name_col = scores.columns.values[name_col]

        # If indexes were ints with missing values, fix float conversion
        if self.index_dtype == int:
            scores.dropna(inplace=True)
            scores[name_col] = scores[name_col].astype(int)

        # Use score filter
        if score_filter:
            scores = scores[[name_col] + score_filter]

        # Save
        self.output = self.output.merge(
            scores, left_on=self.name, right_on=name_col
        )

    def write_file(self, output_path):

        self.output.to_csv(
            output_path, quoting=None, index=False  # encoding="ascii",
        )


if __name__ == "__main__":

    period1 = (datetime(2016, 9, 1), datetime(2016, 12, 1))
    period2 = (datetime(2016, 12, 1), datetime(2017, 4, 1))
    parser = Parser(
        "./data/primaria2.csv",
        date_col=1,
        name_col=0,
        event_col=2,
        component_col=5,
        context_col=4,
        index_dtype=int,
    )

    # action_filter = [
    #     "Tema visto",
    #     "Informe usuario del curso visto",
    #     "Curso: G432 - Formación en valores y competencias personales para el docente  - Curso 2016-2017",
    #     "Cuestionario",
    #     "Tarea",
    # ]

    parser.add_event_counts("period1_", period1)
    parser.add_event_counts("period2_", period2)
    # parser.add_component_counts("total_", period)
    parser.add_session_counts("period1_sessions", period1)
    parser.add_session_counts("period2_sessions", period2)
    parser.add_events_per_forum("period1_", period1)
    parser.add_events_per_forum("period2_", period2)
    parser.add_scores("data/notas2.csv", na_scores="NP", score_filter=["FINAL"])
    parser.write_file("data/output.csv")
