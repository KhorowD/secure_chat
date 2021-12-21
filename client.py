import sys,time
from PyQt5 import QtCore, QtGui, QtWidgets
import socket
from threading import Thread 
from socketserver import ThreadingMixIn 
import client_ui as ui

tcpClientA=None
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
        # self.flag=0
        # self.chatTextField=QLineEdit(self)
        # self.chatTextField.resize(480,100)
        # self.chatTextField.move(10,350)
        # self.btnSend=QPushButton("Send",self)
        # self.btnSend.resize(480,30)
        # self.btnSendFont=self.btnSend.font()
        # self.btnSendFont.setPointSize(15)
        # self.btnSend.setFont(self.btnSendFont)
        # self.btnSend.move(10,460)
        # self.btnSend.setStyleSheet("background-color: #F7CE16")
        # self.btnSend.clicked.connect(self.send)

        # self.chatBody=QVBoxLayout(self)
        # # self.chatBody.addWidget(self.chatTextField)
        # # self.chatBody.addWidget(self.btnSend)
        # # self.chatWidget.setLayout(self.chatBody)
        # splitter=QSplitter(QtCore.Qt.Vertical)

        # self.chat = QTextEdit()
        # self.chat.setReadOnly(True)

        # splitter.addWidget(self.chat)
        # splitter.addWidget(self.chatTextField)
        # splitter.setSizes([400,100])

        # splitter2=QSplitter(QtCore.Qt.Vertical)
        # splitter2.addWidget(splitter)
        # splitter2.addWidget(self.btnSend)
        # splitter2.setSizes([200,10])

        # self.chatBody.addWidget(splitter2)


        # self.setWindowTitle("Chat Application")
        # self.resize(500, 500)

    def send(self):
        text=self.chatTextField.text()
        font=self.chat.font()
        font.setPointSize(13)
        self.chat.setFont(font)
        textFormatted='{:>80}'.format(text)
        self.chat.append(textFormatted)
        tcpClientA.send(text.encode())
        self.chatTextField.setText("")

class ClientThread(Thread):
    def __init__(self,window): 
        Thread.__init__(self) 
        self.window=window
 
    def run(self): 
       host = '127.0.0.1'
       print(host)
       port = 8080
       BUFFER_SIZE = 2000 
       global tcpClientA
       tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
       tcpClientA.connect((host, port))
       
       while True:
           data = tcpClientA.recv(BUFFER_SIZE)
           window.chat.append(data.decode("utf-8"))
       tcpClientA.close() 


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    clientThread=ClientThread(window)
    clientThread.start()
    window.show()
    sys.exit(app.exec_())