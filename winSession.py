import os
from json import dump
from collections import OrderedDict

from PyQt5 import QtWidgets, QtGui

from utils import id2num,                   \
                  get_next_id_number,       \
                  get_current_timestamp,    \
                  append_tsv_row

from winArousal import arousalWindow


class sessionWindow(QtWidgets.QMainWindow):
    """
    Main GUI interface for dream reporting.

    Assumes a BIDS-structured file system.
    Takes the top-level data directory and
    the subject id (eg, sub-001) as arguments,
    but they come from the configuration json file.

    Each entry is a new session, and it auto-detects
    the session by looking at the subject session file
    and creating the "next" entry.

    *_setup.json file
    =================
    This file is not initialized until the Update button is hit.
    Everything left blank will not go into the file.
    """
    def __init__(self,data_dir,subject_id,location,setup_keys):
                      # session_id='ses-0001',
                      # wakeup_id='wkup-01'):
        super().__init__()
        
        self.setup_keys = setup_keys
        
        self.data_dir = data_dir
        self.sub_id = subject_id
        self.session_fname = f'{self.data_dir}/{self.sub_id}/{self.sub_id}_sessions.tsv'

        # create new session id
        self.init_new_session(location)

        self.setup_fname = f'{self.data_dir}/{self.sub_id}/{self.ses_id}/{self.sub_id}_{self.ses_id}_setup.json'

        self.initUI()


    def init_new_session(self,location):
        """Append the session file with a new session and timestamp it.
        And add an *empty* arousal.tsv file.
        """
        # find next session id from BIDS session file
        current_session_num = get_next_id_number(self.session_fname)
        current_session_id = f'ses-{current_session_num:03d}'
        current_timestamp = get_current_timestamp()
        # append csv with new session
        row_data = [current_session_id,current_timestamp,location]
        append_tsv_row(self.session_fname,row_data)
        # create directory for new session
        curr_sess_dir = f'{self.data_dir}/{self.sub_id}/{current_session_id}'
        os.mkdir(curr_sess_dir)
        # initialize empty arousals.tsv file
        arousal_fname = f'{curr_sess_dir}/{self.sub_id}_{current_session_id}_arousals.tsv'
        row_data = ['arousal_id','acq_time','arousal_type']
        append_tsv_row(arousal_fname,row_data)
        # cleanup
        print(f'Created new session {current_session_id} at {current_timestamp}.')
        self.ses_id = current_session_id
        self.session_dir = curr_sess_dir
        # self.arousal_fname = arousal_fname

        
    def initUI(self):

        #####  setup toolbar  #####
        # exit button
        # exitAct = QtWidgets.QAction(QtGui.QIcon('./image.jpg'),'&Exit',self)        
        exitAct = QtWidgets.QAction('&Exit',self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QtWidgets.qApp.quit)
        # save button
        saveAct = QtWidgets.QAction('&Save File',self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.setStatusTip('Save File')
        # saveAct.triggered.connect(self.savefile)

        self.statusBar().showMessage('Ready')
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAct)
        toolbar.addAction(saveAct)
        # menubar = self.menuBar()
        # menubar.setNativeMenuBar(False) # needed for pyqt5
        # fileMenu = menubar.addMenu('&File')
        # fileMenu.addAction(exitAct)

        # create central widget for holding grid layout
        self.init_CentralWidget()

        # main window stuff
        xywh = (300, 300, 200, 100) # xloc, yloc, width, height
        self.setGeometry(*xywh)
        self.setWindowTitle('laka')    
        self.show()

    def init_CentralWidget(self):
        """The central widget holds the *non-toolbar*
        contents of the main window."""

        # make a button to initialize a new Arousal
        self.arousalLineEdit = QtWidgets.QLineEdit()
        arousalButton = QtWidgets.QPushButton('New Arousal')
        arousalButton.clicked.connect(self.openArousalWindow)

        # make a series of options for the *_setup.json file
        # each option needs a label and lineedit
        self.setupLabels = [ QtWidgets.QLabel(opt) for opt in self.setup_keys ]
        self.setupLEdits = [ QtWidgets.QLineEdit() for opt in self.setup_keys ]
        # and a button to update them
        updateSetupButton = QtWidgets.QPushButton('Update setup')
        updateSetupButton.clicked.connect(self.save_setup)

        # manage the location/size of widgets
        grid = QtWidgets.QGridLayout()
        i = 0
        for label, lineedit in zip(self.setupLabels,self.setupLEdits):
            grid.addWidget(label,i,0)
            grid.addWidget(lineedit,i,1)
            i += 1
        grid.addWidget(updateSetupButton,i,0,1,2)
        grid.addWidget(self.arousalLineEdit,i+1,0,1,2)
        grid.addWidget(arousalButton,i+2,0,1,2)

        # intialize the central widget
        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(grid)
        self.setCentralWidget(centralWidget)


    def save_setup(self):
        setup_payload = {}
        for label, lineedit in zip(self.setupLabels,self.setupLEdits):
            response = lineedit.text()
            if response:
                # sleep aids an be separate by commas
                if label.text() == 'sleep_aids' and ',' in response:
                    response = [ r.strip() for r in response.split(',') ]
                setup_payload[label.text()] = response
        with open(self.setup_fname,'w') as json_file:
            dump(setup_payload,json_file,sort_keys=True,indent=4,ensure_ascii=False)
        print(f'Saved to {self.setup_fname}.')

    def openArousalWindow(self):
        # get the arousal type
        aro_type = self.arousalLineEdit.text()
        # initialize the widget
        self.arousalWindow = arousalWindow(self.data_dir,self.sub_id,self.ses_id,aro_type)
        # show the widget
        self.arousalWindow.show()


    # def savefile(self):

    #     # get ids in case they changed from defaults
    #     subid = self.prelimWidgs[0].text()
    #     sesid = self.prelimWidgs[1].text()
    #     wkupid = self.prelimWidgs[2].text()

    #     outdir = f'{self.data_dir}/{subid}/{sesid}'
    #     if not os.path.isdir(outdir):
    #         os.mkdir(outdir)

    #     core_bname = f'{subid}_{sesid}_task-sleep_{wkupid}'
    #     report_fname = os.path.join(outdir,core_bname+'_drm-typed.txt')
    #     json_fname = os.path.join(outdir,core_bname+'_drm.txt')
    #     for fn in [report_fname,json_fname]:
    #         if os.path.isfile(fn):
    #             print(f"====== WARNING CANT SAVE BECAUSE FILE EXISTS: {fn}")
    #             return

    #     # save dream report
    #     print(f'saving to {report_fname}')
    #     drmreport = self.reportText.toPlainText()
    #     with open(report_fname,'w') as outfile:
    #         outfile.write(drmreport)

    #     # save json of scattered stuff
    #     downBttns = [ b for b in self.lucidityRadBttns if b.isChecked() ]
    #     lucidity_val = None if len(downBttns)==0 else downBttns[0].text()
    #     data = {
    #         'participant_id': self.participant_id,
    #         'session_id': self.session_id,
    #         'wakeup_id': self.wakeup_id,
    #         'lucidity': lucidity_val,
    #         'lucidity_continuous': self.lucidSlider.value(),
    #     }
    #     for k, v in data.items():
    #         print(f'{k} : {v}')
    #     import json
    #     with open(json_fname,'w') as outfile:
    #         json.dump(data,outfile,sort_keys=True,indent=4,ensure_ascii=False)
