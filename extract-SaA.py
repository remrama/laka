"""
To extract data from android sleep data file.

Every entry in the SaS datafile has 2 rows (data and column names).
There is a new row for column names for each entry because the
column names include event timestamps, and these are different for
each night. This means there is also a unique amount of columns
per entry, since there are different numbers of events.

Recent entries on *TOP* of csv file!!!

sleep-data.csv gets broken into 3 files
1. saa-info.json    : all the single-variable parameter stuff
2. saa-movement.tsv : timestamped movement values (2 columns)
3. saa-events.tsv   : timestamped events (2 columns)

prefs.xml gets copied exactly as it is.
This is generally constant but keep it with each entry
because it holds the app's global parameters at the time.
"""
import os, csv, json, time, shutil

from utils import get_next_id_number


CONFIG_FNAME = './config.json'
with open(CONFIG_FNAME,'r') as infile:
    CONFIG = json.load(infile)
laka_data_dir = CONFIG['data_directory']
sub_id = CONFIG['subject_id']
SaA_dir = os.path.expanduser(CONFIG['SaA_data_directory'])

SaA_fname = f'{SaA_dir}/sleep-export.csv'
SaA_pref_fname = f'{SaA_dir}/prefs.xml'

# make the filenames that will be used for exporting
session_fname = f'{laka_data_dir}/{sub_id}/{sub_id}_sessions.tsv'
last_ses_num = get_next_id_number(session_fname) - 1
last_ses_id = f'ses-{last_ses_num:03d}'
info_fname  = f'{laka_data_dir}/{sub_id}/{last_ses_id}/{sub_id}_{last_ses_id}_saa-info.json'
mov_fname   = f'{laka_data_dir}/{sub_id}/{last_ses_id}/{sub_id}_{last_ses_id}_saa-movement.tsv'
event_fname = f'{laka_data_dir}/{sub_id}/{last_ses_id}/{sub_id}_{last_ses_id}_saa-events.tsv'
pref_fname  = f'{laka_data_dir}/{sub_id}/{last_ses_id}/{sub_id}_{last_ses_id}_saa-prefs.xml'
assert os.path.getmtime(SaA_fname) < time.time()-(3600), \
    'The datafile was not updated/synced in the last hour.'


# first just copy the preferences file
# (This is a standalone thing that doesn't impact anything below.)
shutil.copyfile(SaA_pref_fname,pref_fname)



# sleep as android is shitty in that they use different timestamp formats
def unixms2iso(unixms_stamp):
    # SaA data timestamps are in milliseconds and need to be converted to seconds
    ts_secs = float(unixms_stamp) / 1000
    ts_struct = time.strptime(time.ctime(ts_secs))
    ts_iso = time.strftime('%Y-%m-%dT%H:%M:%S',ts_struct)
    # datetime.datetime.fromtimestamp(ts_secs).isoformat()
    return ts_iso
def fromtostamp2iso(fromto_stamp):
    # this is just a weird format that SaA uses :/
    ts_struct = time.strptime(fromto_stamp,'%d. %m. %Y %H:%M')
    ts_iso = time.strftime('%Y-%m-%dT%H:%M:%S',ts_struct)
    return ts_iso


# load most recent SaA entry
with open(SaA_fname,'r') as csvfile:
    SaA_file = csv.reader(csvfile,delimiter=',')#,quotechar='|')
    # loop over all rows just to extract the first and second
    for row_num, row in enumerate(SaA_file):
        if row_num == 0:
            cols = row
        elif row_num == 1:
            data = row

# get indices for info, movement, and events
event_start_idx = cols.index('Event')
mov_cols = [ c for c in cols if ':' in c ]
# make sure all the movement columns are actually times
assert all([ c.replace(':','').isnumeric() for c in mov_cols ])
mov_start_idx = cols.index(mov_cols[0])

info_slice  = slice(mov_start_idx)
mov_slice   = slice(mov_start_idx,event_start_idx)
event_slice = slice(event_start_idx,len(cols))

# create saa_info.json file
info_cols = cols[info_slice]
info_data = data[info_slice]
info_payload = { key.lower() : val for key, val in zip(info_cols,info_data) }
# do some formatting
for k, v in info_payload.items():
    if v.replace('.','').replace('-','').isnumeric():
        info_payload[k] = float(v)
    elif k == 'comment':
        info_payload[k] = [ com.lstrip('#') for com in v.split() ]
    elif k in ['from','to','sched']:
        info_payload[k] = fromtostamp2iso(v)
with open(info_fname,'w') as json_file:
    json.dump(info_payload,json_file,sort_keys=True,indent=4,ensure_ascii=False)

# create saa_movement.tsv file
mov_cols = cols[mov_slice]
mov_data = data[mov_slice]
with open(mov_fname,'w') as tsv_file:
    writer = csv.writer(tsv_file,delimiter='\t')
    # write header/columns of tsv file
    header = ['time','movement']
    writer.writerow(header)
    # write data
    for stamp, mov_val in zip(mov_cols,mov_data):
        mov_row = [stamp,float(mov_val)]
        writer.writerow(mov_row)

# create events file
# The event columns are useless, as they are all just "Event".
# The value in data has both event and timestamp, separated
# by a "-", *EXCEPT* for heart rate and DHA(?), which have additional
# "-" that separate the event and timestamp from a specific value.
# Sometimes there are 3 "-" because an additional one for sci notation.
event_data = data[event_slice]
with open(event_fname,'w') as tsv_file:
    writer = csv.writer(tsv_file,delimiter='\t')
    # write header/columns of tsv file
    header = ['time','event','value']
    writer.writerow(header)
    # write data
    for data_str in event_data:
        assert data_str.count('-') in [1,2,3]
        if data_str.count('-') == 1:
            event, stamp = data_str.split('-')
            mov_row = [unixms2iso(stamp),event,None]
        else:
            event, stamp, val = data_str.split('-',2)
            mov_row = [unixms2iso(stamp),event,float(val)]
        writer.writerow(mov_row)