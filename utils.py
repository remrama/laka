
def get_current_timestamp():
    from time import strftime
    return strftime('%Y-%m-%dT%H:%M:%S')

def id2num(bids_id):
    """Convert a BIDS-style ID to the number."""
    assert isinstance(bids_id,str)
    assert '-' in bids_id
    assert bids_id[-3:].isnumeric()
    return int(bids_id.split('-')[1])

def get_next_id_number(fname):
    """
    Get the most recent subject, session, or arousal
    ID number from the appropriate BIDS-structured tsv file,
    and add 1 to that.
    """
    from csv import reader

    assert fname[-4:] == '.tsv'
    with open(fname,'r') as tsv_file:
        tsv_rows = list(reader(tsv_file,delimiter='\t'))
    recent_id = tsv_rows[-1][0]
    if '-' not in recent_id:
        next_num = 1
    else:
        next_num = 1 + int(recent_id.split('-')[-1])
    return next_num

def append_tsv_row(fname,row_data):
    from csv import writer

    assert fname[-4:] == '.tsv'
    with open(fname,'a') as tsv_file:
        writer = writer(tsv_file,delimiter='\t')
        writer.writerow(row_data)
