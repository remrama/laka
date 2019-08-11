
import sys
from PyQt5 import QtGui, QtWidgets, QtCore


class ScalePopup(QtWidgets.QScrollArea):
    def __init__(self,scalename):
        super(self.__class__, self).__init__()
        # QtWidgets.QWidget.__init__(self)

        self.scale_fname = f'./scales/{scalename}.json'
        self.out_fname = f'./{scalename}.tsv'


        self.load_scale_json()

        widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout()
        widget.setLayout(grid)

        # top row shows the scale options
        for i, respstr in enumerate(self.response_strings):
            Label = QtWidgets.QLabel(respstr)
            Label.setWordWrap(True)
            grid.addWidget(Label,0,i+1,1,1,QtCore.Qt.AlignBottom)
            # Label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)


        self.sliders = {} # save to access responses
        for qnum, qstr in self.questions.items():
            Slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            Slider.setRange(self.response_min,self.response_max)
            Slider.setValue(self.response_min)
            Slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
            Slider.setTickInterval(1)
            Slider.setSingleStep(1)
            Label = QtWidgets.QLabel(qstr)

            grid.addWidget(Label,qnum,0,1,1,QtCore.Qt.AlignRight)
            grid.addWidget(Slider,qnum,1,1,len(self.response_values))

            self.sliders.update({qnum:Slider})



        self.setWidget(widget)
        self.setWidgetResizable(True)

        # main window stuff
        self.setGeometry(500,0,900,500)
        self.setWindowTitle(scalename)    


    def load_scale_json(self):
        import json
        with open(self.scale_fname,'r') as infile:
            data = json.load(infile)
        self.questions = { int(qnum): qstr for qnum, qstr in data['questions'].items() }
        self.response_values = data['response_values']
        self.response_strings = data['response_strings']
        self.response_min = min(self.response_values)
        self.response_max = max(self.response_values)

    # def save_scale(self):
    #     from pandas import DataFrame
    #     responses = { qnum: slid.value() for qnum, slid in self.sliders.items() }
    #     outdf = DataFrame(responses.items(),columns=['question_num','response']
    #         ).sort_values('question_num')
    #     outdf.to_csv(self.out_fname,index=False,sep='\t')


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
    window = ScalePopup(scalename='LuCiD')
    window.show()
    sys.exit(app.exec_())