import os
from json import dump, load
from collections import OrderedDict

from PyQt5 import QtWidgets, QtGui

from utils import id2num,                   \
                  get_next_id_number,       \
                  get_current_timestamp,    \
                  append_tsv_row

from winArousal import arousalWindow
from winScale import ScalePopup


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

        # get the available scales for menu
        with open('./config.json','r') as json_file:
            config = load(json_file)
            self.pheno_scales = config['longitudinal_scales']
            self.arousal_types = config['arousal_types']

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
        self.ses_inittime = current_timestamp
        # self.arousal_fname = arousal_fname

        
    def initUI(self):

        status_msg = f'{self.sub_id}_{self.ses_id}'#' at {self.ses_inittime}'
        self.statusBar().showMessage(status_msg)


        ##### create actions that can be applied to *either* menu or toolbar #####
        # exitAct = QtWidgets.QAction(,'&Exit',self)        
        exitAct = QtWidgets.QAction('&Exit',self) #QtGui.QIcon('./image.jpg')
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QtWidgets.qApp.quit)
        
        saveAct = QtWidgets.QAction('&Save File',self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.setStatusTip('Save File')
        # saveAct.triggered.connect(self.savefile)

        phenoscaleActs = [ QtWidgets.QAction(scale,self) for scale in self.pheno_scales ]
        for action, scale in zip(phenoscaleActs,self.pheno_scales):
            action.setStatusTip(f'Create new {scale} scale')
            action.triggered.connect(self.open_phenotype_scale)

        arousalActs = [ QtWidgets.QAction(arotype,self) for arotype in self.arousal_types ]
        for action, arotype in zip(arousalActs,self.arousal_types):
            action.setStatusTip(f'Create new arousal with type as {arotype}')
            action.triggered.connect(self.openArousalWindow)


        #####  setup menu bar  #####
        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(False) # needed for pyqt5 on Mac

        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(exitAct)

        # make submenu for available phenotype scales
        newMenu = menuBar.addMenu('&Add')

        phenoMenu = QtWidgets.QMenu('Phenotype',self)
        for scaleAction in phenoscaleActs:
            phenoMenu.addAction(scaleAction)
        newMenu.addMenu(phenoMenu)

        arousalMenu = QtWidgets.QMenu('Arousal',self)
        for scaleAction in arousalActs:
            arousalMenu.addAction(scaleAction)
        newMenu.addMenu(arousalMenu)

        # mainMenu = self.menuBar()
        # mainMenu.setNativeMenuBar(False)
        # fileMenu = mainMenu.addMenu('TEST')
        # fileAction = fileMenu.addAction('Change file')
        # fileAction.triggered.connect(lambda x: print(x))



        #####  setup tool bar  #####
        # toolbar = self.addToolBar('Exit')
        # toolbar.addAction(exitAct)

        # create central widget for holding grid layout
        self.init_CentralWidget()

        # main window stuff
        xywh = (300, 300, 200, 100) # xloc, yloc, width, height
        self.setGeometry(*xywh)
        self.setWindowTitle('laka')    
        self.show()


    def open_phenotype_scale(self):
        scale = self.sender().text()
        self.scalewin = ScalePopup(scale,self.sub_id)
        self.scalewin.show()


    def init_CentralWidget(self):
        """The central widget holds the *non-toolbar*
        contents of the main window."""

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
                if ',' in response and label.text() in ['sleep_aids','LDIMs']:
                    response = [ r.strip() for r in response.split(',') ]
                setup_payload[label.text()] = response
        with open(self.setup_fname,'w') as json_file:
            dump(setup_payload,json_file,sort_keys=True,indent=4,ensure_ascii=False)
        print(f'Saved to {self.setup_fname}.')

    def openArousalWindow(self):
        # get the arousal type
        aro_type = self.sender().text()
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
