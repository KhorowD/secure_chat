import sys
import threading
from tkinter import *
from tkinter import simpledialog
from google.protobuf import message

import grpc

import generated.chat_pb2 as chat
import generated.chat_pb2_grpc as rpc

from PyQt5 import QtCore, QtGui, QtWidgets
import client_ui as ui
from registration_dialog import Ui_RegisterForm

address = 'localhost'
port = 8080

class ClientData():
    """
    Структура для хранения данных пользователя в одном месте
    """
    def __init__(self) -> None:
        self.username = ""
        self.password = ""
        self.key_1 = ""
        self.key_2 = ""
        self.isRegistered = False #Если пользователь залогинился, тогда ставим True

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.client_data = ClientData()

        # dialog slot bindings

        self.ui.actionLogin.triggered.connect(self.onActionLoginClicked)
        self.ui.btn_send_msg.clicked.connect(self.send_message)
    
        # the frame to put ui components on
        # self.window = window
        # self.username = u
        # # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.ChatServerStub(channel)
        # create new listening thread for when new message streams come in
        threading.Thread(target=self.__listen_for_messages, daemon=True).start()
        # self.__setup_ui()
        # self.window.mainloop()

    def onActionLoginClicked(self):
        reg_form = RegistrationForm(self)
        reg_form.exec()
        creds = reg_form.get_current_user_credits()
        self.client_data.isRegistered = True
        self.client_data.username = creds[0]
        self.client_data.password = creds[1]
        # reg_form.

    def __listen_for_messages(self):
        """
        This method will be ran in a separate thread as the main/ui thread, because the for-in call is blocking
        when waiting for new messages
        """
        for note in self.conn.ChatStream(chat.Empty()):  # this line will wait for new messages from the server!
            print("R[{}] {}".format(note.name, note.message))  # debugging statement
            # self.chat_list.insert(END, "[{}] {}\n".format(note.name, note.message))  # add the message to the UI
            self.ui.chat_field_msg.append("[{}] {}\n".format(note.name, note.message))

    def send_message(self, event):
        """
        This method is called when user enters something into the textbox
        """
        # message = self.entry_message.get()  # retrieve message from the UI

        message = self.ui.text_input_msg.toPlainText()

        if message is not '':
            n = chat.Note()  # create protobug message (called Note)
            n.name = self.client_data.username  # set the username
            n.message = message  # set the actual message of the note
            print("S[{}] {}".format(n.name, n.message))  # debugging statement
            self.conn.SendNote(n)  # send the Note to the server

    # def __setup_ui(self):
    #     self.chat_list = Text()
    #     self.chat_list.pack(side=TOP)
    #     self.lbl_username = Label(self.window, text=self.username)
    #     self.lbl_username.pack(side=LEFT)
    #     self.entry_message = Entry(self.window, bd=5)
    #     self.entry_message.bind('<Return>', self.send_message)
    #     self.entry_message.focus()
    #     self.entry_message.pack(side=BOTTOM)

class RegistrationForm(QtWidgets.QDialog):
    """
    Класс для реализации формы регистрации или логина
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui_reg_form = Ui_RegisterForm()
        self.ui_reg_form.setupUi(self)
        self.accepted.connect(self.save_input_values)

        # Инициализируем поля для хранения данных
        self.username = ""
        self.password = ""

    def get_current_user_credits(self):
        """
        Фнкция возвращает данные которые пользовтель ввел
        в контексте диалогового окна логин
        """
        return (self.username, self.password)

    def save_input_values(self):
        self.username = self.ui_reg_form.line_edit_username.text()
        self.password = self.ui_reg_form.line_edit_password.text()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

    # root = Tk()  # I just used a very simple Tk window for the chat UI, this can be replaced by anything
    # frame = Frame(root, width=300, height=300)
    # frame.pack()
    # root.withdraw()
    # username = None
    # while username is None:
    #     # retrieve a username so we can distinguish all the different clients
    #     username = simpledialog.askstring("Username", "What's your username?", parent=root)
    # root.deiconify()  # don't remember why this was needed anymore...
    # c = Client(username, frame)  # this starts a client and thus a thread which keeps connection to server open


# import sys,time
# from PyQt5 import QtCore, QtGui, QtWidgets
# import socket
# from threading import Thread 
# from socketserver import ThreadingMixIn 
# import client_ui as ui
# from registration_dialog import Ui_RegisterForm

# tcpClientA=None
# class MainWindow(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.ui = ui.Ui_MainWindow()
#         self.ui.setupUi(self)

#         # dialog slot bindings

#         self.ui.actionLogin.triggered.connect(self.onActionLoginClicked)

#     def onActionLoginClicked(self):
#         reg_form = RegistrationForm(self)
#         reg_form.exec()


#     # TO DO
#     # def send(self):
#     #     text=self.chatTextField.text()
#     #     font=self.chat.font()
#     #     font.setPointSize(13)
#     #     self.chat.setFont(font)
#     #     textFormatted='{:>80}'.format(text)
#     #     self.chat.append(textFormatted)
#     #     tcpClientA.send(text.encode())
#     #     self.chatTextField.setText("")

# class RegistrationForm(QtWidgets.QDialog):
#     """
#     Класс для реализации формы регистрации или логина
#     """
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.ui_reg_form = Ui_RegisterForm()
#         self.ui_reg_form.setupUi(self)

# class ClientThread(Thread):
#     def __init__(self,window): 
#         Thread.__init__(self) 
#         self.window=window
 
#     def run(self): 
#         host = '127.0.0.1'
#         print(host)
#         port = 8080
#         BUFFER_SIZE = 2000 
#         global tcpClientA
#         tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#         tcpClientA.connect((host, port))
       
#         while True:
#             data = tcpClientA.recv(BUFFER_SIZE)
#             window.chat.append(data.decode("utf-8"))
#             tcpClientA.close() 

# class CurentUser():
#     """
#     Класс пользователя содержит информацию для верификации и регистрации новых пользователей
#     """
#     def __init__(self, user_name, user_pass_hash):
#         self.user_name = user_name
#         self.user_pass_hash = user_pass_hash


#     # Регистрация новоого пользователя
#     def new_user_reg(self):
#         pass

#     # Верификация пользователя
#     def verify_user_acc(self):
#         pass





# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     window = MainWindow()
#     clientThread=ClientThread(window)
#     clientThread.start()
#     window.show()
#     sys.exit(app.exec_())