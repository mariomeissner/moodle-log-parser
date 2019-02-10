#%%
import csv
import pprint
import numpy as np
from datetime import datetime, timedelta

pp = pprint.PrettyPrinter(indent=4)


#%%
# Function to load a csv into a list
def load_csv(path, has_header=True):
    """
    If has_header, returns (rows, column_names)
    Else returns rows only.
    """
    with open("primaria.csv", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=";")
        if has_header:
            column_names = list(next(reader))
        rows = list(reader)
    if column_names:
        return rows, column_names
    else:
        return rows


#%%
# Load the csv into a list
rows, log_col_names = load_csv("primaria.csv", has_header=True)
rows = list(reversed(rows))

#%%
# Process action types
names = dict()
# Keeps all the features we will obtain in this script
features = ["ID"]

# Iterate over the rows, and create dictionary of students,
# counting number of actions performed by each.
for row in rows:
    # Get name of student and action performed
    name = row[5]
    component = row[2]
    event = row[3]
    # If new name found, create its entry.
    if name not in names:
        names[name] = {"ID": name}
    # If new component for this name found, create its entry.
    if component not in names[name]:
        names[name][component] = 0
    # If new event for this name found, create its entry.
    if event not in names[name]:
        names[name][event] = 0
    # Increment counter
    names[name][component] += 1
    names[name][event] += 1

    # Keep track of all action types found until now,
    # and add them as features.
    if component not in features:
        features.append(component)
    if event not in features:
        features.append(event)

print(f"Found {len(features)} features:")
pp.pprint(features)


#%%
# Compute average session length and number of sessions per student

# Format of the timesamp in the log
time_format = "%d/%m/%Y %H:%M"
# Dictionary holding a list of activity timestamps per student
timestamps_dict = {}

for row in rows:
    name = row[5]
    timestamp = row[0]
    if name not in timestamps_dict:
        timestamps_dict[name] = []
    time = datetime.strptime(timestamp, time_format)
    timestamps_dict[name].append(time)


#%%
# Max minutes between actions in a session
max_idle = timedelta(minutes=20)
# Iterate over timestamps to compute features
for name, timestamps in timestamps_dict.items():

    num_sessions = 0
    total_duration = timedelta(0)
    i = 1
    last = timestamps[0]
    session_start = last
    sessions = []
    session_months = []

    while i < len(timestamps):

        current = timestamps[i]
        diff = current - last
        if diff > max_idle:
            num_sessions += 1
            session_duration = last - session_start
            total_duration += session_duration
            sessions.append(session_duration.total_seconds())
            session_months.append(session_start.month)
            session_start = current

        last = current
        i += 1

    # Last session
    num_sessions += 1
    total_duration += last - session_start
    average_duration = total_duration / num_sessions
    sessions = np.array(sessions)

    # Add computed values as features
    # TODO: This can now also be done with numpy
    names[name]["Average Session Duration"] = total_duration.total_seconds()
    names[name]["Number of Sessions"] = num_sessions
    names[name]["Session Duration STD"] = np.std(sessions)

    for month in session_months:
        if month not in names[name]:
            names[name][str(month)] = 0
        names[name][str(month)] += 1

features.append("Average Session Duration")
features.append("Number of Sessions")
features.append("Session Duration STD")

for month in range(1, 13):
    features.append(str(month))

#%%
# Export as csv
with open("output.csv", "w", encoding="utf-8") as out:
    writer = csv.DictWriter(out, fieldnames=features, restval=0)

    writer.writeheader()
    for id in names.values():
        writer.writerow(id)
