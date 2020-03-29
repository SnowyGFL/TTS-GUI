from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton, QMainWindow, QApplication, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from playsound import playsound
from pygame import mixer
from io import BytesIO
import os, tempfile, gtts, subprocess, gtts
from gtts import gTTS

LOGFILE = r""
DIR = r""
COMMAND = ".say"

# Don't touch below
LANGUAGES = [language for language in gtts.lang.tts_langs()]
NO_ASYNC = True


def TTS(message, language):
    tts = gTTS(text=message, lang=language)
    name = tempfile.mktemp(suffix='.mp3', dir=DIR)
    tts.save(name)
    try:
        playsound(name, NO_ASYNC)
    except Exception as e:
        print("UNABLE TO PLAY FILE")
        print(str(e))
    os.remove(name)


def splicer(mystr, sub):
    index = mystr.find(sub)
    if index != -1:
        return mystr[index:]
    else:
        pass


class MyThread(QObject):
    finished = pyqtSignal()
    writeLog = pyqtSignal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.continue_run = True

    def run(self):
        f = open(LOGFILE, 'r', encoding='utf8')
        f.seek(0, 2)
        self.writeLog.emit("Reading file...")

        while self.continue_run:
            loglines = f.readline()
            if COMMAND in loglines:
                # STRIP NEW LINES AT START AND END
                loglines = loglines.strip("\n")
                loglines = loglines.strip('\t')
                self.writeLog.emit(loglines)
                # print(loglines)
                string = splicer(loglines, COMMAND)
                string2 = string.split()
                # print(string2)

                Language = "en"
                if len(string2[0]) > 4:
                    Language = string2[0][4:]
                    # print(Language)

                if Language not in LANGUAGES:
                    self.writeLog.emit("Langauge not found")
                    # print("Language not available")
                    continue

                if string[len(string2[0]):].isspace():
                    self.writeLog.emit("No input found")
                    # print("No input found")
                    continue

                # print(string[len(string2[0]):])
                TTS(string[len(string2[0]):], Language)
            QThread.msleep(10)
        self.finished.emit()

    def stop(self):
        self.continue_run = False

    def start(self):
        self.continue_run = False


class Ui_MainWindow(QMainWindow):

    stop_signal = pyqtSignal()
    threadCreated = False

    def __init__(self):
        super().__init__()
        self.setupUi(MainWindow)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("mainWindow")
        MainWindow.resize(352, 350)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.logBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.logBrowser.setGeometry(QtCore.QRect(240, 10, 101, 211))
        self.logBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.logBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.logBrowser.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.logBrowser.setObjectName("logBrowser")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(120, 240, 111, 31))
        self.startButton.setObjectName("startButton")
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setGeometry(QtCore.QRect(240, 240, 101, 31))
        self.stopButton.setObjectName("stopButton")
        self.restartButton = QtWidgets.QPushButton(self.centralwidget)
        self.restartButton.setGeometry(QtCore.QRect(130, 300, 91, 31))
        self.restartButton.setObjectName("restartButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 355, 21))
        self.menubar.setObjectName("menubar")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(10, 10, 91, 21))
        self.comboBox.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.comboBox.setObjectName("comboBox")
        self.textInput = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.textInput.setGeometry(QtCore.QRect(10, 40, 221, 181))
        self.textInput.setObjectName("textInput")
        self.ABOUT = QtWidgets.QLabel(self.centralwidget)
        self.ABOUT.setGeometry(QtCore.QRect(140, 10, 91, 21))
        self.ABOUT.setAutoFillBackground(False)
        self.ABOUT.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ABOUT.setAlignment(QtCore.Qt.AlignCenter)
        self.ABOUT.setObjectName("ABOUT")
        self.playButton = QtWidgets.QPushButton(self.centralwidget)
        self.playButton.setGeometry(QtCore.QRect(10, 240, 101, 31))
        self.playButton.setObjectName("playButton")
        self.AsyncCheck = QtWidgets.QCheckBox(self.centralwidget)
        self.AsyncCheck.setGeometry(QtCore.QRect(10, 310, 91, 21))
        self.AsyncCheck.setObjectName("AsyncCheck")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        for lang in gtts.lang.tts_langs().keys():
            self.comboBox.addItem(lang)

        self.startButton.clicked.connect(self.start_thread)
        self.stopButton.clicked.connect(self.stop_thread)
        self.restartButton.clicked.connect(self.restart)
        self.playButton.clicked.connect(self.play_sound)
        self.AsyncCheck.stateChanged.connect(self.asyncCheck)

    def restart(self):
        if self.threadCreated:
            self.thread.quit
            self.worker.stop()
        subprocess.Popen(['python', 'CSGOTTS.py'])
        sys.exit(0)

    def play_sound(self):
        if not self.textInput.toPlainText():
            self.logBrowser.append("No text specified")
            return
        if self.textInput.toPlainText().isspace():
            self.logBrowser.append("Text are all spaces")
            return
        # TTS(self.textInput.toPlainText(), self.comboBox.currentText())
        # USE ANOTHER METHOD TO PLAY THE SOUND TO NOT FREEZE THE GUI FOR SOME REASON
        tts = gTTS(text=self.textInput.toPlainText(), lang=self.comboBox.currentText(), slow=False)
        mp3 = BytesIO()
        tts.write_to_fp(mp3)
        mp3.seek(0)

        # Play from Buffer
        mixer.init()
        mixer.music.load(mp3)
        mixer.music.play()

    def start_thread(self):
        if not self.threadCreated:
            self.thread = QThread()
            self.logBrowser.append("Thread started")
            self.threadCreated = True
        else:
            self.logBrowser.append("Thread already created")
            return
        self.worker = MyThread()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.thread.started.connect(self.worker.run)
        self.worker.writeLog.connect(self.appendtext)

    def appendtext(self, message):
        self.logBrowser.append(message)

    def stop_thread(self):
        if not self.threadCreated:
            self.logBrowser.append("Thread already stopped")
            return
        self.logBrowser.append("Thread stopped & deleted")
        self.worker.stop()
        self.thread.finished.connect(self.worker.stop)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.threadCreated=False

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CSGO TTS - v1.0"))
        self.startButton.setText(_translate("MainWindow", "START"))
        self.stopButton.setText(_translate("MainWindow", "STOP"))
        self.restartButton.setText(_translate("MainWindow", "RESTART"))
        self.ABOUT.setText(_translate("MainWindow", "Made by Snowy"))
        self.playButton.setText(_translate("MainWindow", "PLAY"))
        self.AsyncCheck.setText(_translate("MainWindow", "ASYNC?"))

    def asyncCheck(self, state):
        global NO_ASYNC
        if state == QtCore.Qt.Checked:
            NO_ASYNC = False
        else:
            NO_ASYNC = True

    def raise_error(self):
        assert False


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)
    QtWidgets.QApplication.quit()


if __name__ == "__main__":
    import sys
    sys.excepthook = excepthook
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
