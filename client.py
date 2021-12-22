import sys,time
from PyQt5 import QtCore, QtGui, QtWidgets
import socket
from threading import Thread 
from socketserver import ThreadingMixIn 
import client_ui as ui
from registration_dialog import Ui_RegisterForm

tcpClientA=None
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)

        # dialog slot bindings

        self.ui.actionLogin.triggered.connect(self.onActionLoginClicked)

    def onActionLoginClicked(self):
        reg_form = RegistrationForm(self)
        reg_form.exec()


    # TO DO
    # def send(self):
    #     text=self.chatTextField.text()
    #     font=self.chat.font()
    #     font.setPointSize(13)
    #     self.chat.setFont(font)
    #     textFormatted='{:>80}'.format(text)
    #     self.chat.append(textFormatted)
    #     tcpClientA.send(text.encode())
    #     self.chatTextField.setText("")

class RegistrationForm(QtWidgets.QDialog):
    """
    Класс для реализации формы регистрации или логина
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui_reg_form = Ui_RegisterForm()
        self.ui_reg_form.setupUi(self)

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

class CurentUser():
    """
    Класс пользователя содержит информацию для верификации и регистрации новых пользователей
    """
    def __init__(self, user_name, user_pass_hash):
        self.user_name = user_name
        self.user_pass_hash = user_pass_hash


    # Регистрация новоого пользователя
    def new_user_reg(self):
        pass

    # Верификация пользователя
    def verify_user_acc(self):
        pass





if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    clientThread=ClientThread(window)
    clientThread.start()
    window.show()
    sys.exit(app.exec_())