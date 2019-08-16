
import sys
from json import load
from PyQt5 import QtGui, QtWidgets, QtCore

from utils import get_current_timestamp, load_scale

class ScalePopup(QtWidgets.QScrollArea):
    def __init__(self,scalename):
        super(self.__class__, self).__init__()
        # QtWidgets.QWidget.__init__(self)

        self.scalename = scalename
        with open('./config.json') as json_file:
            config = load(json_file)
        data_dir = config['data_directory']
        self.longitudinal_scales = config['longitudinal_scales']

        # this filename is ONLY for longitudinal scales
        timestamp = get_current_timestamp().replace('-','').replace(':','')
        self.results_fname = f'{data_dir}/longitudinal/{scalename}_{timestamp}.json'
        
        from os import makedirs
        from os.path import exists, dirname
        if not exists(dirname(self.results_fname)):
            makedirs(dirname(self.results_fname))

        widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout()
        widget.setLayout(grid)

        self.load_probes()
        self.payload = {} # to hold results (though they get overwritten everytime so could just init each time :/)

        self.QProbes = {} # for later accessing the data
        for i, (probe_var, probe_info) in enumerate(self.probes.items()):
            # add the label, which is the probe text question
            Label = QtWidgets.QLabel(probe_info['Description'])
            grid.addWidget(Label,i,0,1,1,QtCore.Qt.AlignBottom)

            # add the response option, which ** varies dependent on response type **
            if 'min' in probe_info['Levels'].keys():
                # value counter
                self.QProbes[probe_var] = QtWidgets.QSpinBox()
                self.QProbes[probe_var].setRange(probe_info['Levels']['min'],probe_info['Levels']['max'])
                self.QProbes[probe_var].setSingleStep(probe_info['Levels']['step'])
            else:
                # dropdown menu
                self.QProbes[probe_var] = QtWidgets.QComboBox()
                # for level_val, level_name in probe_info['Levels'].items():
                self.QProbes[probe_var].addItems(probe_info['Levels'].values())
                self.QProbes[probe_var].currentIndexChanged.connect(self.update_payload)
            grid.addWidget(self.QProbes[probe_var],i,1)

        self.setWidget(widget)
        self.setWidgetResizable(True)

        # main window stuff
        # self.setMinimumWidth(widget.sizeHint().width())
        width, height = widget.sizeHint().width(), 500
        xloc, yloc = 500, 300
        self.setGeometry(xloc,yloc,width,height)
        self.setWindowTitle(scalename)


    def update_payload(self,i):
        for k, v in self.QProbes.items():
            # getting response also depends on response type
            if isinstance(v,QtWidgets.QComboBox):
                # response = list(self.probes[k]['Levels'].keys())[v.currentIndex()]
                levels = self.probes[k]['Levels']
                response = [ lval for lval, lstr in levels.items() if lstr==v.currentText() ]
                assert len(response) == 1
                response = int(response[0])
            elif isinstance(v,QtWidgets.QSpinBox):
                response = v.value()
            self.payload[k] = response

        # self.payload['acq_time'] = get_current_timestamp()
        
        # only save if longitudinal scale.
        # otherwise it's an arousal scale and will be saved
        # within the arousal window.
        if self.scalename in self.longitudinal_scales:
            self.save()


    def save(self):
        """Save every time anything changes.
        """
        # payload = { k: v.currentText() for k, v in self.QProbes.items() }
        # payload = { k: v.currentIndex() for k, v in self.QProbes.items() }
        # payload = { k: list(self.probes[k]['Levels'].keys())[v.currentIndex()] for k, v in self.QProbes.items() }
        from json import dump
        with open(self.results_fname,'w') as json_file:
            dump(self.payload,json_file,indent=4,ensure_ascii=False)#,sort_keys=True)
        

    def load_probes(self):
        self.scale_payload = load_scale()
        self.probes = { k: v for k, v in data.items() if k != 'MeasurementToolMetadata'}


    # def closeEvent(self,event):
    #     '''Overrides default window shutdown
    #     behavior by asking for confirmation.
    #     '''
    #     exit_msg = 'Are you sure you want to save and exit?'
    #     reply = QtWidgets.QMessageBox.question(self,'Message',exit_msg,
    #         QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)
    #     if reply == QtWidgets.QMessageBox.Yes:
    #         self.save_scale()
    #         event.accept()
    #     else:
    #         event.ignore()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ScalePopup(scalename='MADRE')
    window.show()
    sys.exit(app.exec_())