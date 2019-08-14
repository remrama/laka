"""
nomie export json has 4 key:value pairs
    nomie    : dict containing nomie version and file creation timestamp
    boards   : list of different user boards (I don't use these so mine's empty)
    events   : list of all events saved with trackers
    trackers : dict of the different trackers available

So really I'm just using 'events'.

Each event has 9 key:value pairs
    _id      : as far as I can tell this is randomly generated
    note     : the text input and saved. using a tracker automatically 
               gives a hashtagged phrase with value in parentheses
    end      : unix millisecond timestamp (same as start?)
    start    : unix millisecond timestamp (same as end?)
    score    : always seems to be None??
    lat      : latitude
    lng      : longitude
    location : these seem to just be ordered numbers???
    modified : boolean indicating whether the event was edited
"""
from json import load
from glob import glob
from pandas import DataFrame, to_datetime


# get filename of latest nomie export
with open('./config.json') as json_file:
    config = load(json_file)
    data_dir = config['data_directory']
    sub_id = config['subject_id']
in_fname = sorted(glob(f'{data_dir}/source/{sub_id}/nomie/*.json'))[-1]
out_fname = f'{data_dir}/{sub_id}/{sub_id}_long-nomie.tsv'


# load in nomie data and grab events list
with open(in_fname,'r') as json_file:
    data = load(json_file)
events = data['events']
# convert to usable pandas dataframe
df = DataFrame(events)

# convert unix timestamp to something more readable
# and something that pandas knows is time
df['timestamp'] = to_datetime(df['start'],unit='ms')
# order by the time of event
df.sort_values('timestamp',inplace=True)

# parse out the note, which contains event info and value
def note2eventname(note):
    if '(' in note:
        note = note[:note.index('(')]
    event_name = note.lstrip('#')
    return event_name

def note2value(note):
    return float(1 if '(' not in note else note[note.index('(')+1:note.index(')')])

df['event_name'] = df['note'].apply(note2eventname)
df['event_value'] = df['note'].apply(note2value)


# export relevant columns
keep_cols = ['timestamp','event_name','event_value']
time_fmt = '%Y-%m-%dT%H:%M:%S'
df.to_csv(out_fname,columns=keep_cols,sep='\t',index=False,date_format=time_fmt)