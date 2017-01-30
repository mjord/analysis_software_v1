from database_manager import Database
import sys
import os

os.environ['QT_API'] = 'pyqt5'

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtGui
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
        # self.actionOpen_Database.triggered.connect(self.open_db)
        # self.actionAdd_Movie.triggered.connect(self.add_item)
        # self.actionNew_Database.triggered.connect(self.new_db)
        # self.iconSize.valueChanged.connect(self.rescale)
        #
        # # self.listWidget.itemDoubleClicked.connect(self.play)
        # # self.listWidget.itemClicked.connect(self.testMovieInfo)
        #
        # self.listWidget.itemDoubleClicked.connect(self.twoclick)
        # # self.listWidget.itemClicked.connect(self.clicked)
        # self.listWidget.itemClicked.connect(self.oneclick)
        #
        # # self.searchText.textChanged.connect(self.update_search)
        # self.searchText.editingFinished.connect(self.update_list)
        #
        #
        # self.timer = None

        ipyConsole = QIPythonWidget(customBanner="Welcome to the embedded ipython console\n")
        self.gridLayout.addWidget(ipyConsole)

        self.show()




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


class ExampleWidget(QtWidgets.QMainWindow):
    """ Main GUI Window including a button and IPython Console widget inside vertical layout """
    def __init__(self, parent=None):
        super(ExampleWidget, self).__init__(parent)
        self.setWindowTitle('iPython in PyQt5 app example')
        self.mainWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        layout = QtWidgets.QVBoxLayout(self.mainWidget)
        self.button = QtWidgets.QPushButton('Another widget')
        ipyConsole = QIPythonWidget(customBanner="Welcome to the embedded ipython console\n")
        layout.addWidget(self.button)
        layout.addWidget(ipyConsole)
        # This allows the variable foo and method print_process_id to be accessed from the ipython console
        ipyConsole.pushVariables({"foo":43,"print_process_id":print_process_id})
        ipyConsole.printText("The variable 'foo' and the method 'print_process_id()' are available. Use the 'whos' command for information.\n\nTo push variables run this before starting the UI:\n ipyConsole.pushVariables({\"foo\":43,\"print_process_id\":print_process_id})")
        self.setGeometry(300, 300, 800, 600)

def print_process_id():
    print('Process ID is:', os.getpid())

def main():
    app  = get_app_qt5()
    widget = MainWindow()
    # widget.show()
    app.exec_()

if __name__ == '__main__':
    main()