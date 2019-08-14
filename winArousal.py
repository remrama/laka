import os
from json import dump, load
# from collections import OrderedDict

from PyQt5 import QtGui, QtWidgets, QtCore

from utils import id2num,                   \
                  get_next_id_number,       \
                  get_current_timestamp,    \
                  append_tsv_row
from winScale import ScalePopup


class arousalWindow(QtWidgets.QMainWindow):
    """
    Main GUI interface for dream reporting.

    Assumes a BIDS-structured file system.
    Takes the top-level data directory and
    the subject id (eg, sub-001) as arguments,
    but they come from the configuration json file.

    Each entry is a new session, and it auto-detects
    the session by looking at the subject session file
    and creating the "next" entry.
    """
    def __init__(self,data_dir,sub_id,ses_id,arousal_type,parent=None):
        super(self.__class__, self).__init__(parent)

        # for appending
        self.arousal_fname = f'{data_dir}/{sub_id}/{ses_id}/{sub_id}_{ses_id}_arousals.tsv'

        # generates arousal id
        self.aro_type = arousal_type
        self.init_new_arousal()

        # for creating/saving
        self.dream_fname = f'{data_dir}/{sub_id}/{ses_id}/dreams/{sub_id}_{ses_id}_task-sleep_{self.aro_id}_dream.json'

        self.init_CentralWidget()

        self.sub_id = sub_id

        with open('./config.json') as json_file:
            config = load(json_file)
        self.available_scales = config['arousal_scales']



    def init_new_arousal(self):
        """Get the next arousal number for the current session
        and append the arousals.tsv file with a timestamps and arousal type.
        
        TODO: restrict options for arousal type

        """
        current_arousal_num = get_next_id_number(self.arousal_fname)
        current_arousal_id = f'aro-{current_arousal_num:03d}'
        current_timestamp = get_current_timestamp()
        row_data = [current_arousal_id,current_timestamp,self.aro_type]
        append_tsv_row(self.arousal_fname,row_data)
        # cleanup
        self.aro_id = current_arousal_id


    def init_CentralWidget(self):

        #####  setup toolbar  #####
        # no toolbar for now (see winSession for how to make one)

        # create central widget for holding grid layout
        self.init_CW()

        # main window stuff
        self.setGeometry(300,300,300,300)
        self.setWindowTitle(f'New arousal type {self.aro_type}')    
        self.show()


    # def set_io(self,i):
    #     prelim_probe = self.prelimWidgs[]
    #     print("Items in the list are :")
    #     for count in range(self.prelimWidgs[0].count()):
    #         print(self.prelimWidgs[0].itemText(count))
    #     # print("Current index",i,"selection changed ",self.prelimWidgs[0].currentText())

    def init_CW(self):
        ## make everything grouped boxes
        ## even when unnecessary, just seems easier for code organization

        # preliminary questions
        #### note that rn participant id doesnt change as a function of this
        # self.cb = QComboBox()
        # self.cb.addItem("C")
        # self.cb.addItem("C++")
        # self.cb.addItems(["Java", "C#", "Python"])
        # self.cb.currentIndexChanged.connect(self.selectionchange)

        # self.comboBoxes = OrderedDict([
        #     ('subject_num: ', QtWidgets.QComboBox()), 
        #     ('session_num: ', QtWidgets.QComboBox()),
        #     ('arousal_num: ', QtWidgets.QComboBox()),
        # ])
        # # prelimQuests = ['sub_id:','sess_id:','wakeup_id:']
        # prelimAnsws = [ id2num(bidsid) for bidsid in [self.sub_id,self.ses_id,self.aro_id] ]
        # # self.prelimWidgs = [ QtWidgets.QComboBox() for q in prelimQuests ]
        # for qst, cb in self.comboBoxes.items():
        #     if qst == 'subject_num: ':
        #         opt_range = range(1000)
        #     elif qst == 'session_num: ':
        #         opt_range = range(10000)
        #     elif qst == 'wakeup_num: ':
        #         opt_range = range(100)
        #     for j in opt_range:
        #         cb.addItem(str(j))
        #     # cb.currentIndexChanged.connect(self.set_io)

        # # self.prelimWidgs = [ QtWidgets.QLineEdit(a) for a in prelimAnsws ]
        # prelimLabels = [ QtWidgets.QLabel(q) for q in self.comboBoxes.keys() ]
        # prelimBox = QtWidgets.QGroupBox()
        # prelimLayout = QtWidgets.QHBoxLayout()
        # prelimBox.setLayout(prelimLayout)
        # for l, w in zip(prelimLabels,self.comboBoxes.values()):
        #     prelimLayout.addWidget(l)
        #     prelimLayout.addWidget(w)
        
        # dream report
        self.reportText = QtWidgets.QTextEdit()
        reportLabel = QtWidgets.QLabel('Dream report (separate dreams with ---)')
        reportBox = QtWidgets.QGroupBox()
        reportLayout = QtWidgets.QVBoxLayout()
        reportBox.setLayout(reportLayout)
        reportLayout.addWidget(reportLabel)
        reportLayout.addWidget(self.reportText)

        # binary lucid probe
        lucidity_options = ['no','semi','yes']
        self.lucidityRadBttns = [ QtWidgets.QRadioButton(x) for x in lucidity_options ]
        lucidBinBox = QtWidgets.QGroupBox()
        # lucidBox.setCheckable(True)
        lucidBinLabel = QtWidgets.QLabel('Were you lucid?')
        lucidBinLayout = QtWidgets.QHBoxLayout()
        lucidBinBox.setLayout(lucidBinLayout)
        lucidBinLayout.addWidget(lucidBinLabel)
        for buttn in self.lucidityRadBttns:
            lucidBinLayout.addWidget(buttn)
        # lucidBinLayout.addWidget(QtWidgets.QRadioButton('semi'))
        # lucidBinLayout.addWidget(QtWidgets.QRadioButton('yes'))

        # # lucid continous probe
        # self.lucidSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        # self.lucidSlider.setRange(0,29)
        # self.lucidSlider.setValue(0) # default :/
        # self.lucidSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        # self.lucidSlider.setTickInterval(1)
        # self.lucidSlider.setSingleStep(1)
        # lucidContLabel = QtWidgets.QLabel('How lucid were you?')
        # lucidContBox = QtWidgets.QGroupBox()
        # lucidContLayout = QtWidgets.QHBoxLayout()
        # lucidContBox.setLayout(lucidContLayout)
        # lucidContLayout.addWidget(lucidContLabel)
        # lucidContLayout.addWidget(self.lucidSlider)

        # memory sources open response
        self.memsrcText = QtWidgets.QTextEdit()
        memsrcLabel = QtWidgets.QLabel('Try to estimate the memory sources of the dream.')
        memsrcBox = QtWidgets.QGroupBox()
        memsrcLayout = QtWidgets.QVBoxLayout()
        memsrcBox.setLayout(memsrcLayout)
        memsrcLayout.addWidget(memsrcLabel)
        memsrcLayout.addWidget(self.memsrcText)

        # buttons for scales
        scaleButtons = [ QtWidgets.QPushButton(s) for s in self.available_scales ]
        for bttn in scaleButtons:
            bttn.clicked.connect(self.openScaleWindow)
        optbttnsBox = QtWidgets.QGroupBox()
        optbttnsLayout = QtWidgets.QHBoxLayout()
        optbttnsBox.setLayout(optbttnsLayout)
        for bttn in scaleButtons:
            optbttnsLayout.addWidget(bttn)


        # manage the location/size of widgets
        grid = QtWidgets.QGridLayout()
        # grid.addWidget(prelimBox,0,0)
        grid.addWidget(reportBox,0,0)
        grid.addWidget(lucidBinBox,1,0)
        grid.addWidget(memsrcBox,2,0)
        grid.addWidget(optbttnsBox,3,0)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(grid)
        self.setCentralWidget(centralWidget)


        self.popups = { sname: ScalePopup(sname,self.sub_id) for sname in self.available_scales }
        # dict to later determine whether a scale was used/clicked
        self.popups_completed = { sname: False for sname in self.available_scales }

    # def save_scale(self,scalename):
    #     from pandas import DataFrame
    #     scalewidg = self.popups[scalename]
    #     responses = { qnum: slid.value() for qnum, slid in scalewidg.sliders.items() }
        
    #     outdf = DataFrame(responses.items(),columns=['question_num','response']
    #         ).sort_values('question_num')
    #     outdf.to_csv(self.out_fname,index=False,sep='\t')

    #     for scalename, scalewidg in self.popups.items():


    def closeEvent(self,event):
        """Overrides default window shutdown
        behavior by asking for confirmation.
        """
        exit_msg = 'Are you sure you want to save and exit?'
        reply = QtWidgets.QMessageBox.question(self,'Message',exit_msg,
            QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.save_dream_json()
            event.accept()
        else:
            event.ignore()



    def openScaleWindow(self):
        scalename = self.sender().text()
        self.popups_completed[scalename] = True
        self.popups[scalename].show()


    def save_dream_json(self):

        # initialize the payload empty because only adding stuff that was completeed
        payload = {}

        # get text dream report
        dream_report = self.reportText.toPlainText()
        if len(dream_report) > 0:
            payload['report'] = dream_report

        # get text memory sources report
        memsrc_report = self.memsrcText.toPlainText()
        if len(memsrc_report) > 0:
            payload['memory_sources'] = memsrc_report

        # get lucidity response
        downBttns = [ b for b in self.lucidityRadBttns if b.isChecked() ]
        if len(downBttns) > 0:
            payload['lucid'] = downBttns[0].text()

        # add scale responses
        for scalename, scalewidg in self.popups.items():
            if self.popups_completed[scalename]:
                if 'scales' not in payload.keys():
                    payload['scales'] = {}
                payload['scales'][scalename] = [ slid.value() for slid in scalewidg.sliders.values() ]
            # responses = { qnum: slid.value() for qnum, slid in scalewidg.sliders.items() }

        # save
        # If it's the first arousal, then need to make dreams directory.
        if self.aro_id == 'aro-001':
            os.mkdir(os.path.dirname(self.dream_fname))
        with open(self.dream_fname,'w') as outfile:
            dump(payload,outfile,sort_keys=True,indent=4,ensure_ascii=False)
        print(f'Saved {self.dream_fname}.')

        # from pandas import DataFrame
        # responses = { qnum: slid.value() for qnum, slid in self.sliders.items() }
        # outdf = DataFrame(responses.items(),columns=['question_num','response']
        #     ).sort_values('question_num')
        # outdf.to_csv(self.out_fname,index=False,sep='\t')



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
