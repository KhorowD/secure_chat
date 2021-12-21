import server_ui as ui
from 
import asyncio
from asyncqt import QEventLoop
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):

        super().__init__()
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
        
async def create_server(loop):
    return await 

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()