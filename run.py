"""
Initialize a new session and open the main laka interface.
"""
import os, sys, json, argparse

from PyQt5.QtWidgets import QApplication

from winSession import sessionWindow

parser = argparse.ArgumentParser()
parser.add_argument('--location',default='bedroom',type=str)
location = parser.parse_args().location

# get the data directory and subject id
CONFIG_FNAME = './config.json'
with open(CONFIG_FNAME,'r') as infile:
    CONFIG = json.load(infile)
data_dir   = CONFIG['data_directory']
subject_id = CONFIG['subject_id']
if '~' in data_dir:
    data_dir = os.path.expanduser(data_dir)

# run the app
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = sessionWindow(data_dir,subject_id,location)
    sys.exit(app.exec_())