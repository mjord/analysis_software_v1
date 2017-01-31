from database_manager import Database
from ImportMethods import ImportMethods

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

        #TODO: Change gui.ui files to .py and import directly <MJ p:3>
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
        self.actionMeasurement.triggered.connect(self.new_measure)

        #TODO: VIEW DATABASE IN THE databaseView (QTreeView) Widget <MJ p:1>
        self.model = QtGui.QStandardItemModel()
        self.databaseView.setModel(self.model)

        # self.model = self.TreeViewModel()
        # self.databaseView.setModel(self.model)



        #TODO: DEFAULT DATA VIEW INCLUDING IPYTHON <MJ P:2>

        # self.ipyConsole = QIPythonWidget(customBanner="Welcome to the embedded ipython console\n")
        # self.gridLayout.addWidget(self.ipyConsole)

        self.show()

    def refresh_Tree(self):
        data = OrganizedMeasurements("test")
        self.data = data.getData(self.db)
        self.model.appendRow(self.data)

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

            self.refresh_Tree()

    def new_project(self):
        self.add_window = NewProject(self.db)
        # self.add_window = NewProject(self.db, rowid=2)
        self.add_window.exec_()

    def new_process(self):
        self.add_window = NewProcess(self.db)
        # self.add_window = NewProject(self.db, rowid=2)
        self.add_window.exec_()

    def new_wafer(self):
        self.add_window = NewWafer(self.db)
        # self.add_window = NewWafer(self.db, rowid=2)
        # self.add_window.show()
        self.add_window.exec_()

    def new_measure(self):
        self.add_window = NewMeasurement(self.db)
        #TODO Test measurement popup in edit mode <MJ p2>
        # self.add_window = NewWafer(self.db, rowid=2)
        self.add_window.exec_()


class OrganizedMeasurements():
    def __init__(self, txt, **kwargs):

        if "db" in kwargs:
            self.db = kwargs.get("db")

        if "parent" in kwargs:
            self.parent = kwargs.get("parent")

        self.txt = txt
        # self.tooltip = None
        # self.child = []
        # self.icon = []
        # self.index = None
        # self.widget = None

    def sample_recusive(self, db, sample, list):
        # q = "SELECT PROCESS_STEP.NAME FROM MEASUREMENT JOIN PROCESS_STEP " \
        #     "ON PROCESS_STEP.ROWID = MEASUREMENT.PROCESS AND SAMPLE = %i"%sample["rowid"]
        # measurements = db.query(q)
        q = """SELECT ROWID, * FROM SAMPLE
         WHERE
         PROJECT = %i AND PARENT_TYPE > 0 AND PARENT_ID = %i"""%(sample["PROJECT"], sample["rowid"])
        subsamples = db.query(q)

        if len(subsamples) > 0:
            for subsample in subsamples:
                self.sample_recusive(db, subsample, list)
        else:
            #TODO: I'm going to assume that the sample chains end in measurements. Fix this later <MJ p:3>
            # q = """
            # SELECT PROCESS_STEP.NAME, MEASUREMENT.ROWID, SAMPLE.REFERENCE FROM PROCESS_STEP JOIN MEASUREMENT JOIN SAMPLE
            # ON
            # (MEASUREMENT.PROCESS = PROCESS_STEP.ROWID AND MEASUREMENT.SAMPLE = %i)
            # OR
            # (SAMPLE.PARENT_TYPE = PROCESS_STEP.ROWID AND SAMPLE.ROWID = %i)"""%(sample["rowid"], sample["rowid"])
            # print(q)
            q = """
            SELECT PROCESS_STEP.NAME, MEASUREMENT.ROWID FROM PROCESS_STEP JOIN MEASUREMENT
            ON
            (MEASUREMENT.PROCESS = PROCESS_STEP.ROWID AND MEASUREMENT.SAMPLE = %i)
            """ %sample["rowid"]
            rows = db.query(q)
            measurements = []
            if len(rows) > 0:
                for row in rows:
                    q = "SELECT * FROM MEASUREMENT WHERE ROWID = %i"%row["rowid"]
                    M = db.query(q)
                    measurements.append([row["name"], M[0]["name"]])

            list.append([sample["reference"], measurements])
        return list









    def getData(self, db):
        Data = []

        q = "SELECT ROWID, * FROM PROJECT"
        projects = db.query(q)

        for project in projects:
            Data.append(project["name"])
            q = "SELECT ROWID, * FROM SAMPLE WHERE PROJECT = %i AND PARENT_TYPE = 0"%project["rowid"]
            topsamples = db.query(q)
            for sample in topsamples:
                Data = self.sample_recusive(db, sample, Data)

        return Data


        # q = "SELECT ROWID, * FROM SAMPLE"
        # samples = self.db.query(q)
        #
        # q = "SELECT ROWID, * FROM MEASUREMENTS"
        # measurements = self.db.query(q)
        #
        # q = "SELECT ROWID, * FROM PROCESS_STEP"
        # processes = self.db.query(q)

        #Now organize it Projects -> Sample ... Subsample -> Process_Step -> Measurement




class NewMeasurement(QtWidgets.QDialog):
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
        self.ui = "new_measurement_dialog.ui"  # Enter file here.

        # Set up the user interface from Designer.
        uic.loadUi(self.ui, self)

        ### Set up functionality
        #Open file browser on startup
        self.open_file()

        #Connect Browse Button
        self.browseButton.clicked.connect(self.open_file)
        #Connect Cancel Button
        self.cancelButton.clicked.connect(self.close)

        # set the time
        now = QtCore.QDateTime.currentDateTime()
        self.dateTimeEdit.setDateTime(now)

        ## Populate comboboxes
        #importMethodsBox
        importMethods = ImportMethods()
        self.methodsList = importMethods.MethodsList
        for name in self.methodsList["name"]:
            self.importMethodsBox.addItem(name)
        # self.importMethodsBox.insertSeparator(2)

        #Sample Box
        q = "SELECT ROWID, REFERENCE FROM SAMPLE"
        rows = self.db.query(q)
        self.sampleList = {"name": [], "rowid": []}
        self.sampleList["name"].append(None)
        self.sampleList["rowid"].append(None)
        self.sampleBox.addItem("")
        self.sampleList["name"].append(None)
        self.sampleList["rowid"].append(None)
        self.sampleBox.addItem("Add New Sample")
        self.sampleList["name"].append(None)
        self.sampleList["rowid"].append(None)
        self.sampleBox.insertSeparator(2)

        for row in rows:
            self.sampleList["name"].append(row["REFERENCE"])
            self.sampleList["rowid"].append(row["rowid"])
            self.sampleBox.addItem(row["REFERENCE"])
        self.sampleBox.currentIndexChanged.connect(self.check_sample_index)



        #Process Box
        q = "SELECT ROWID, NAME FROM PROCESS_STEP"
        rows = self.db.query(q)
        self.processList = {"name": [], "rowid": []}
        self.processList["name"].append(None)
        self.processList["rowid"].append(None)
        self.processBox.addItem("")
        self.processList["name"].append(None)
        self.processList["rowid"].append(None)
        self.processBox.addItem("Add New Process")
        self.processList["name"].append(None)
        self.processList["rowid"].append(None)
        self.processBox.insertSeparator(2)

        for row in rows:
            self.processList["name"].append(row["NAME"])
            self.processList["rowid"].append(row["rowid"])
            self.processBox.addItem(row["NAME"])
        self.processBox.currentIndexChanged.connect(self.check_process_index)


        #Add Measurement Functionality
        if self.rowid is None:
            self.addButton.clicked.connect(self.add_measure)

        #Todo Make edit mode work in NewMeasurement class <MJ p2>
        # else:#Open in Edit Mode
        #     q = "SELECT * FROM PROCESS_STEP WHERE ROWID = %i"%self.rowid
        #     rows = self.db.query(q)
        #     row = rows[0]
        #
        #     self.nameText.setText(row["NAME"])
        #     self.overviewText.setText(row["OVERVIEW"])
        #
        #     self.makeButton.setText("Edit Project")
        #     self.makeButton.clicked.connect(self.edit_process)

    def check_sample_index(self):
        if self.sampleBox.currentIndex() == 1:
            self.add_window = NewWafer(self.db)
            # self.add_window.setWindowModality(QtCore.Qt.WindowModal)
            self.add_window.exec_()
            self.reinit_boxes()

    def check_process_index(self):
        if self.processBox.currentIndex() == 1:
            self.add_window = NewProcess(self.db)
            # self.add_window.setWindowModality(QtCore.Qt.WindowModal)
            # self.add_window.setWindowFlags(self.add_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            self.add_window.exec_()
            self.reinit_boxes()

    def reinit_boxes(self):

        # Sample Box
        self.sampleBox.clear()
        q = "SELECT ROWID, REFERENCE FROM SAMPLE"
        rows = self.db.query(q)
        samples = {"name": [], "rowid": []}
        samples["name"].append(None)
        samples["rowid"].append(None)
        self.sampleBox.addItem("")
        samples["name"].append(None)
        samples["rowid"].append(None)
        self.sampleBox.addItem("Add New Sample")
        samples["name"].append(None)
        samples["rowid"].append(None)
        self.sampleBox.insertSeparator(2)

        for row in rows:
            samples["name"].append(row["REFERENCE"])
            samples["rowid"].append(row["rowid"])
            self.sampleBox.addItem(row["REFERENCE"])

        diff = [False if i in self.sampleList["rowid"] else True for i in samples["rowid"]]
        try:
            indx = diff.index(True)
            self.sampleList = samples
        except ValueError:
            indx = 0

        self.sampleBox.setCurrentIndex(indx)

        # Process Box
        self.processBox.clear()
        q = "SELECT ROWID, NAME FROM PROCESS_STEP"
        rows = self.db.query(q)
        processes = {"name": [], "rowid": []}
        processes["name"].append(None)
        processes["rowid"].append(None)
        self.processBox.addItem("")
        processes["name"].append(None)
        processes["rowid"].append(None)
        self.processBox.addItem("Add New Process")
        processes["name"].append(None)
        processes["rowid"].append(None)
        self.processBox.insertSeparator(2)

        for row in rows:
            self.processList["name"].append(row["NAME"])
            self.processList["rowid"].append(row["rowid"])
            self.processBox.addItem(row["NAME"])

        diff = [False if i in self.processList["rowid"] else True for i in processes["rowid"]]
        try:
            indx = diff.index(True)
            self.processList = processes
        except ValueError:
            indx = 0

        self.processBox.setCurrentIndex(indx)


    def open_file(self):
        names = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Measurement', '','All Files (*.*)')
        self.fname = names[0]
        self.fileEdit.setText(self.fname)

    def add_measure(self):
        name = self.nameText.text()
        if name == "":
            self.nameText.setStyleSheet("color: rgb(255, 0, 0);")
            self.nameText.setText("Must supply a Name")
            self.nameText.setFocus()
            return

        #Make sure a valid index is selected
        if self.sampleBox.currentIndex() == 0:
            self.sampleBox.setItemText(self.sampleBox.currentIndex(), "Select Sample")
            self.sampleBox.setFocus()
            # self.sampleBox.palette.setColor("color: rgb(255, 0, 0);")
            #TODO: Set Combobox color to red to indicate that they need to fix it
            return
        if self.processBox.currentIndex() == 0:
            self.processBox.setItemText(self.processBox.currentIndex(), "Select Process")
            self.processBox.setFocus()
            return

        self.check_sample_index()
        self.check_process_index()

        #Get Sample and Process
        sample_id = self.sampleList["rowid"][self.sampleBox.currentIndex()]
        process_id = self.processList["rowid"][self.processBox.currentIndex()]

        #Get Date/Time
        qdatetime = self.dateTimeEdit.dateTime()
        datetimeString = qdatetime.toString('yyyy-MM-dd hh:mm:ss')

        #Get File Name
        file = self.fileEdit.text()

        #Get Notes
        notes = self.notesText.toPlainText()

        name = re.sub("'", "", name)#Hack
        notes = re.sub("'", "", notes)#Hack

        #Import Method
        method_id = self.methodsList["id"][self.importMethodsBox.currentIndex()]


        q = """
        INSERT INTO MEASUREMENT
        (SAMPLE, PROCESS, FILE, NOTES, NAME, IMPORT_METHOD, DATE)
        VALUES
        (%i, %i, '%s', '%s', '%s', %i, '%s')"""%(sample_id, process_id, file, notes, name, method_id, datetimeString)
        self.db.query(q)
        self.close()

    def edit_measure(self):
        # name = self.nameText.text()
        # if name == "":
        #     self.nameText.setStyleSheet("color: rgb(255, 0, 0);")
        #     self.nameText.setText("Must supply a Name")
        #     return
        #
        # overview = self.overviewText.toPlainText()
        #
        # name = re.sub("'", "", name)
        # overview = re.sub("'", "", overview)
        #
        #
        # q = "UPDATE PROCESS_STEP SET NAME = '%s', OVERVIEW = '%s' WHERE ROWID = %i" % (name, overview, self.rowid)
        # self.db.query(q)
        self.close()







class NewProject(QtWidgets.QDialog):
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
        self.ui = "make_project_dialog.ui"  # Enter file here.

        # Set up the user interface from Designer.
        uic.loadUi(self.ui, self)

        # Connect Cancel Button
        self.cancelButton.clicked.connect(self.close)


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

        name = re.sub("'", "", name)#Hack
        overview = re.sub("'", "", overview)#Hack


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

        name = re.sub("'", "", name)#Hack
        overview = re.sub("'", "", overview)#Hack

        qstart = self.startDate.date()
        start = qstart.toString('yyyy-MM-dd') + ' 12:00:00'
        qend = self.endDate.date()
        end = qend.toString('yyyy-MM-dd') + ' 12:00:00'

        q = "UPDATE PROJECT SET NAME = '%s', OVERVIEW = '%s', DATE_START = '%s', DATE_END = '%s' WHERE ROWID = %i" % (
        name, overview, start, end, self.rowid)
        self.db.query(q)
        self.close()

class NewProcess(QtWidgets.QDialog):
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
        self.ui = "new_process_dialog.ui"  # Enter file here.

        # Set up the user interface from Designer.
        uic.loadUi(self.ui, self)

        # Connect Cancel Button
        self.cancelButton.clicked.connect(self.close)

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

        name = re.sub("'", "", name)#Hack
        overview = re.sub("'", "", overview)#Hack


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

        name = re.sub("'", "", name)#Hack
        overview = re.sub("'", "", overview)#Hack


        q = "UPDATE PROCESS_STEP SET NAME = '%s', OVERVIEW = '%s' WHERE ROWID = %i" % (name, overview, self.rowid)
        self.db.query(q)
        self.close()

class NewWafer(QtWidgets.QDialog):
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
        self.ui = "new_wafer_dialog.ui"  # Enter file here.

        # Set up the user interface from Designer.
        uic.loadUi(self.ui, self)

        #Cancel Button
        self.cancelButton.clicked.connect(self.close)

        # set the time
        now = QtCore.QDateTime.currentDateTime()
        self.dateTimeEdit.setDateTime(now)

        #
        self.processLabel = None
        self.processCB = None

        # populate combobox
        q = "SELECT ROWID, NAME FROM PROJECT"
        rows = self.db.query(q)
        self.parentList = {"name": [], "rowid": [], "type": []}
        for row in rows:
            self.parentList["name"].append(row["name"])
            self.parentList["rowid"].append(row["rowid"])
            self.parentList["type"].append(0)

            self.parentBox.addItem(row["name"])

        # Separator in parentBox and parent List
        self.parentBox.insertSeparator(len(self.parentList["name"]))
        self.parentList["name"].append(None)
        self.parentList["type"].append(None)
        self.parentList["rowid"].append(None)

        q = "SELECT ROWID, REFERENCE FROM SAMPLE"
        rows = self.db.query(q)
        for row in rows:
            self.parentList["name"].append(row["reference"])
            self.parentList["rowid"].append(row["rowid"])

            self.parentBox.addItem(row["reference"])

        self.parentBox.currentIndexChanged.connect(self.check_parent)

        #Specific actions for whether or not we're editing the sample
        if self.rowid is None:
            self.makeButton.clicked.connect(self.make_wafer)

        else:
            q = "SELECT * FROM SAMPLE WHERE ROWID = %i"%self.rowid
            rows = self.db.query(q)
            row = rows[0]

            self.nameText.setText(row["REFERENCE"])
            self.notesText.setText(row["NOTES"])

            parent_type = row["PARENT_TYPE"]
            parent_id = row["PARENT_ID"]
            if parent_type == 0:#Parent is a Project
                q = "SELECT NAME FROM PROJECT WHERE ROWID = %i"%parent_id
                rows = self.db.query(q)
                itemName = rows[0]["NAME"]
            else:
                q = "SELECT REFERENCE FROM SAMPLE WHERE ROWID = %i"%parent_id
                rows = self.db.query(q)
                itemName = rows[0]["REFERENCE"]

            indx = self.parentList["name"].index(itemName)
            self.parentBox.setCurrentIndex(indx)

            self.makeButton.setText("Edit Sample")
            self.makeButton.clicked.connect(self.edit_wafer)

    # def indexchange(self):
    #     print(self.parentBox.currentIndex(), self.parentList["name"][self.parentBox.currentIndex()])
    def check_parent(self):
        if self.parentBox.currentIndex() >= len(self.parentList["type"]):
            self.processLabel = QtWidgets.QLabel()
            self.processLabel.setText("Set Process")

            self.processCB = QtWidgets.QComboBox()
            self.processCB.addItem("")
            self.processCB.addItem("Add Process")


            q = "SELECT ROWID, NAME FROM PROCESS_STEP"
            rows = self.db.query(q)
            self.process_ids = [None, None]
            for row in rows:
                self.processCB.addItem(row["name"])
                self.process_ids.append(row["rowid"])

            self.gridLayout_2.addWidget(self.processLabel, 0, 2)
            self.gridLayout_2.addWidget(self.processCB, 1, 2)
            self.processCB.currentIndexChanged.connect(self.add_process)
        else:
            self.processCB.clear()
            self.gridLayout_2.removeWidget(self.processCB)
            self.processCB.deleteLater()
            self.processCB = None
            self.processLabel.clear()
            self.gridLayout_2.removeWidget(self.processLabel)
            self.processLabel.deleteLater()
            self.processLabel = None

    def add_process(self):
        if self.processCB.currentIndex() == 1:
            self.add_window = NewProcess(self.db)
            # self.add_window = NewProject(self.db, rowid=2)
            self.add_window.exec_()

            self.check_parent()
        else:
            self.parenttype = self.process_ids[self.processCB.currentIndex()]

    def make_wafer(self):
        name = self.nameText.text()
        if name == "":
            self.nameText.setStyleSheet("color: rgb(255, 0, 0);")
            self.nameText.setText("Must supply a Name")
            return

        notes = self.notesText.toPlainText()

        name = re.sub("'", "", name)
        notes = re.sub("'", "", notes)

        # my_time.toPyDateTime()
        qdatetime = self.dateTimeEdit.dateTime()
        datetimeString = qdatetime.toString('yyyy-MM-dd hh:mm:ss')

        if self.parentBox.currentIndex() < len(self.parentList["type"]):
            parent_type = self.parentList["type"][self.parentBox.currentIndex()]
        else:
            parent_type = self.parenttype

        parent_id = self.parentList["rowid"][self.parentBox.currentIndex()]
        if parent_type == 0:#Sample Parent is a project
            project = parent_id
        elif parent_type > 0:#Sample Parent is another sample
            q = "SELECT PROJECT FROM SAMPLE WHERE ROWID = %i"%parent_id
            rows = self.db.query(q)
            project = int(rows[0]["project"])
        else:
            print("Sample can only be a child of a project or another sample")
            raise

        q = """
        INSERT INTO SAMPLE
        (REFERENCE, NOTES, CREATED, MODIFIED, PROJECT, PARENT_TYPE, PARENT_ID)
        VALUES
        ('%s', '%s', '%s', '%s', '%i', '%i', '%i')
        """%(name, notes, datetimeString, datetimeString, project, parent_type, parent_id)

        self.db.query(q)
        self.close()


    def edit_wafer(self):
        name = self.nameText.text()
        if name == "":
            self.nameText.setStyleSheet("color: rgb(255, 0, 0);")
            self.nameText.setText("Must supply a Name")
            return

        notes = self.notesText.toPlainText()

        name = re.sub("'", "", name)
        notes = re.sub("'", "", notes)

        # my_time.toPyDateTime()
        qdatetime = self.dateTimeEdit.dateTime()
        datetimeString = qdatetime.toString('yyyy-MM-dd hh:mm:ss')

        parent_type = self.parentList["type"][self.parentBox.currentIndex()]
        parent_id = self.parentList["rowid"][self.parentBox.currentIndex()]
        if parent_type == 0:  # Sample Parent is a project
            project = parent_id
        elif parent_type == 1:  # Sample Parent is another sample
            q = "SELECT PROJECT FROM SAMPLE WHERE ROWID = %i" % parent_id
            rows = self.db.query(q)
            project = int(rows[0]["project"])
        else:
            print("Sample can only be a child of a project or another sample")
            raise


        q = "UPDATE SAMPLE SET REFERENCE = '%s', NOTES = '%s', MODIFIED = '%s', PROJECT = %i, PARENT_TYPE = %i, " \
            "PARENT_ID = %i WHERE ROWID = %i"%(name, notes, datetimeString, project, parent_type, parent_id, self.rowid)

        self.db.query(q)
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

#XXX mark for cleanup
def print_process_id():
    print('Process ID is:', os.getpid())

def main():
    app  = get_app_qt5()
    widget = MainWindow()
    # widget.show()
    app.exec_()

if __name__ == '__main__':
    main()