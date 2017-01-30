from database_manager import Database
import sqlite3 as sql
import sys
import os
import re

os.environ['QT_API'] = 'pyqt5'

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
# ipython won't work if this is not correctly installed. And the error message will be misleading
from PyQt5 import QtSvg
# from PyQt5.QtCore import QTimer, QSize


# Import the console machinery from ipython
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = "mainWindow_gui.ui"  # Enter file here.

        # Set up the user interface from Designer.
        uic.loadUi(self.ui, self)

        # #Set up database
        # self.db = None
        #
        # # Connect up the buttons.
        self.actionOpen_Database.triggered.connect(self.open_db)
        self.actionProject.triggered.connect(self.new_project)
        self.actionProcess.triggered.connect(self.new_process)
        self.actionSample.triggered.connect(self.new_wafer)



        #
        # # self.searchText.textChanged.connect(self.update_search)
        # self.searchText.editingFinished.connect(self.update_list)
        #
        #
        # self.timer = None

        # self.ipyConsole = QIPythonWidget(customBanner="Welcome to the embedded ipython console\n")
        # self.gridLayout.addWidget(self.ipyConsole)

        self.show()

    def open_db(self):
        names = QtWidgets.QFileDialog.getOpenFileName(self, 'Open database', '','Open database (*.sqlite)')

        if names:
            fname = names[0]
            if len(fname) <= 7:
                fname = fname + ".sqlite"
            elif fname[-7:] != ".sqlite":
                fname = fname + ".sqlite"

            sql.connect(fname)

            self.db = Database(db_name=fname)

    def new_project(self):
        self.add_window = NewProject(self.db)
        # self.add_window = NewProject(self.db, rowid=2)
        self.add_window.show()

    def new_process(self):
        self.add_window = NewProcess(self.db)
        # self.add_window = NewProject(self.db, rowid=2)
        self.add_window.show()

    def new_wafer(self):
        self.add_window = NewWafer(self.db)
        # self.add_window = NewProject(self.db, rowid=2)
        self.add_window.show()


class NewProject(QtWidgets.QWidget):
    def __init__(self, db, **kwargs):
        from datetime import date, datetime


        self.db = db
        if "rowid" in kwargs:
            rowid = kwargs.get("rowid")
            if isinstance(rowid, int):
                self.rowid = rowid
            else:
                self.rowid = None
        else:
            self.rowid = None

        super().__init__()
        self.ui = "make_project_gui.ui"  # Enter file here.

        # Set up the user interface from Designer.
        uic.loadUi(self.ui, self)



        if self.rowid is None:
            self.makeButton.clicked.connect(self.make_project)
            today = date.today()
            try:
                tenyears =  today.replace(year=today.year + 10)
            except ValueError:
                tenyears = today + (date(today.year + 10, 1, 1) - date(today.year, 1, 1))

            qtDate1 = QtCore.QDate.fromString(str(today), 'yyyy-MM-dd')
            qtDate2 = QtCore.QDate.fromString(str(tenyears), 'yyyy-MM-dd')
            self.startDate.setDate(qtDate1)
            self.endDate.setDate(qtDate2)
        else:
            q = "SELECT * FROM PROJECT WHERE ROWID = %i"%self.rowid
            rows = self.db.query(q)
            row = rows[0]
            qtDate1 = QtCore.QDate.fromString(row["DATE_START"][:-9], 'yyyy-MM-dd')
            qtDate2 = QtCore.QDate.fromString(row["DATE_END"][:-9], 'yyyy-MM-dd')
            self.startDate.setDate(qtDate1)
            self.endDate.setDate(qtDate2)

            self.nameText.setText(row["NAME"])
            self.overviewText.setText(row["OVERVIEW"])

            self.makeButton.setText("Edit Project")
            self.makeButton.clicked.connect(self.edit_project)

    def make_project(self):
        name = self.nameText.text()
        if name == "":
            self.nameText.setStyleSheet("color: rgb(255, 0, 0);")
            self.nameText.setText("Must supply a Name")
            return

        overview = self.overviewText.toPlainText()

        name = re.sub("'", "", name)
        overview = re.sub("'", "", overview)


        qstart = self.startDate.date()
        start = qstart.toString('yyyy-MM-dd') + ' 12:00:00'
        qend = self.endDate.date()
        end = qend.toString('yyyy-MM-dd') + ' 12:00:00'

        q = "INSERT INTO PROJECT (NAME, OVERVIEW, DATE_START, DATE_END) VALUES ('%s', '%s', '%s', '%s')"%(name, overview, start, end)
        self.db.query(q)
        self.close()

    def edit_project(self):
        name = self.nameText.text()
        if name == "":
            self.nameText.setStyleSheet("color: rgb(255, 0, 0);")
            self.nameText.setText("Must supply a Name")
            return

        overview = self.overviewText.toPlainText()

        name = re.sub("'", "", name)
        overview = re.sub("'", "", overview)

        qstart = self.startDate.date()
        start = qstart.toString('yyyy-MM-dd') + ' 12:00:00'
        qend = self.endDate.date()
        end = qend.toString('yyyy-MM-dd') + ' 12:00:00'

        q = "UPDATE PROJECT SET NAME = '%s', OVERVIEW = '%s', DATE_START = '%s', DATE_END = '%s' WHERE ROWID = %i" % (
        name, overview, start, end, self.rowid)
        self.db.query(q)
        self.close()

class NewProcess(QtWidgets.QWidget):
    def __init__(self, db, **kwargs):
        from datetime import date, datetime


        self.db = db
        if "rowid" in kwargs:
            rowid = kwargs.get("rowid")
            if isinstance(rowid, int):
                self.rowid = rowid
            else:
                self.rowid = None
        else:
            self.rowid = None

        super().__init__()
        self.ui = "new_process_gui.ui"  # Enter file here.

        # Set up the user interface from Designer.
        uic.loadUi(self.ui, self)



        if self.rowid is None:
            self.makeButton.clicked.connect(self.make_process)

        else:
            q = "SELECT * FROM PROCESS_STEP WHERE ROWID = %i"%self.rowid
            rows = self.db.query(q)
            row = rows[0]

            self.nameText.setText(row["NAME"])
            self.overviewText.setText(row["OVERVIEW"])

            self.makeButton.setText("Edit Project")
            self.makeButton.clicked.connect(self.edit_process)

    def make_process(self):
        name = self.nameText.text()
        if name == "":
            self.nameText.setStyleSheet("color: rgb(255, 0, 0);")
            self.nameText.setText("Must supply a Name")
            return

        overview = self.overviewText.toPlainText()

        name = re.sub("'", "", name)
        overview = re.sub("'", "", overview)


        q = "INSERT INTO PROCESS_STEP (NAME, OVERVIEW) VALUES ('%s', '%s')"%(name, overview)
        self.db.query(q)
        self.close()

    def edit_process(self):
        name = self.nameText.text()
        if name == "":
            self.nameText.setStyleSheet("color: rgb(255, 0, 0);")
            self.nameText.setText("Must supply a Name")
            return

        overview = self.overviewText.toPlainText()

        name = re.sub("'", "", name)
        overview = re.sub("'", "", overview)


        q = "UPDATE PROCESS_STEP SET NAME = '%s', OVERVIEW = '%s' WHERE ROWID = %i" % (name, overview, self.rowid)
        self.db.query(q)
        self.close()

class NewWafer(QtWidgets.QWidget):
    def __init__(self, db, **kwargs):
        from datetime import date, datetime


        self.db = db
        if "rowid" in kwargs:
            rowid = kwargs.get("rowid")
            if isinstance(rowid, int):
                self.rowid = rowid
            else:
                self.rowid = None
        else:
            self.rowid = None

        super().__init__()
        self.ui = "new_wafer_gui.ui"  # Enter file here.

        # Set up the user interface from Designer.
        uic.loadUi(self.ui, self)



        if self.rowid is None:
            self.makeButton.clicked.connect(self.make_wafer)

        else:
            q = "SELECT * FROM PROCESS_STEP WHERE ROWID = %i"%self.rowid
            rows = self.db.query(q)
            row = rows[0]

            self.nameText.setText(row["NAME"])
            self.notesText.setText(row["OVERVIEW"])

            self.makeButton.setText("Edit Project")
            self.makeButton.clicked.connect(self.edit_wafer)

    def make_wafer(self):
        self.close()

    def edit_wafer(self):
        self.close()



def get_app_qt5(*args, **kwargs):
    """Create a new qt5 app or return an existing one."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        if not args:
            args = ([''],)
        app = QtWidgets.QApplication(*args, **kwargs)
    return app

class QIPythonWidget(RichJupyterWidget):
    """ Convenience class for a live IPython console widget. We can replace the standard banner using the customBanner argument"""
    def __init__(self,customBanner=None,*args,**kwargs):
        super(QIPythonWidget, self).__init__(*args,**kwargs)
        if customBanner!=None: self.banner=customBanner
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            get_app_qt5().exit()
        self.exit_requested.connect(stop)

    def pushVariables(self,variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.kernel_manager.kernel.shell.push(variableDict)
    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()
    def printText(self,text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)
    def executeCommand(self,command):
        """ Execute a command in the frame of the console widget """
        self._execute(command,False)


# class ExampleWidget(QtWidgets.QMainWindow):
#     """ Main GUI Window including a button and IPython Console widget inside vertical layout """
#     def __init__(self, parent=None):
#         super(ExampleWidget, self).__init__(parent)
#         self.setWindowTitle('iPython in PyQt5 app example')
#         self.mainWidget = QtWidgets.QWidget(self)
#         self.setCentralWidget(self.mainWidget)
#         layout = QtWidgets.QVBoxLayout(self.mainWidget)
#         self.button = QtWidgets.QPushButton('Another widget')
#         ipyConsole = QIPythonWidget(customBanner="Welcome to the embedded ipython console\n")
#         layout.addWidget(self.button)
#         layout.addWidget(ipyConsole)
#         # This allows the variable foo and method print_process_id to be accessed from the ipython console
#         ipyConsole.pushVariables({"foo":43,"print_process_id":print_process_id})
#         ipyConsole.printText("The variable 'foo' and the method 'print_process_id()' are available. Use the 'whos' command for information.\n\nTo push variables run this before starting the UI:\n ipyConsole.pushVariables({\"foo\":43,\"print_process_id\":print_process_id})")
#         self.setGeometry(300, 300, 800, 600)

def print_process_id():
    print('Process ID is:', os.getpid())

def main():
    app  = get_app_qt5()
    widget = MainWindow()
    # widget.show()
    app.exec_()

if __name__ == '__main__':
    main()