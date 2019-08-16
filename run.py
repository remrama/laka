"""
Initialize a new session and open the main laka interface.
"""
import os, sys, json

from PyQt5.QtWidgets import QApplication

from winSession import sessionWindow

# get the data directory and subject id
CONFIG_FNAME = './config.json'
with open(CONFIG_FNAME,'r') as infile:
    CONFIG = json.load(infile)
data_dir   = CONFIG['data_directory']
setup_keys = CONFIG['setup_keys']

if '~' in data_dir:
    data_dir = os.path.expanduser(data_dir)

# run the app
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = sessionWindow(data_dir,setup_keys)
    sys.exit(app.exec_())