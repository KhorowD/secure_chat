import sys
import threading
# from tkinter import *
# from tkinter import simpledialog
from google.protobuf import message
from bitarray import util


import grpc

import generated.chat_pb2 as chat
import generated.chat_pb2_grpc as rpc

from PyQt5 import QtCore, QtGui, QtWidgets
import client_ui as ui
from registration_dialog import Ui_RegisterForm

from gamma import gen_key
from pyecm import factors
from sha_one import sha_one_process
import gost

address = 'localhost'
port = 8080

# Функция для отображений сообщений об ошибке
def message_box(text, title, icon, buttons):
    message_wgt = QtWidgets.QMessageBox()
    message_wgt.setText(text)
    message_wgt.setWindowTitle(title)
    message_wgt.setIcon(icon)
    message_wgt.setStandardButtons(buttons)
    if buttons == QtWidgets.QMessageBox.Ok:
        message_wgt.exec_()
    else:
        retrn_value = message_wgt.exec_()
        return retrn_value

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
        self.nonce128 = ""
        self.nonce256 = ""
        self.p = 0
        self.q = 0
        self.server_pub_key_fingerprint = ""

        

class ServerData():
    """
    Структура содержащая информацию о сервере 
    """
    def __init__(self) -> None:
        self.keys = {} #Кортеж ключей который загружаем из файла
        self.current_key_id = 0
        self.server_nonce = ""
        self.rsa_pub_key = ""
        self.rsa_priv_key = ""
        self.rsa_n_value = ""
        self.dh_pub_key = ""
        self.dh_priv_key = ""


    def load_keys_from_file(self, file_path) -> bool:
        """
        Функция установки ключей сервера

        Согласно описанию протокола MTProto у клиента уже есть открытые ключи сервера
        В нашем случае для наглядности они сохранены в файле server_keys.txt
        """
        try:
            with open(file_path, "r") as f:
                text_keys = f.read()
        except FileNotFoundError:
            message_box("Файл не существует!", "Error!",
                        QtWidgets.QMessageBox.Critical,
                        QtWidgets.QMessageBox.Ok)
            return False

        if text_keys != "":
            splited_text_keys = text_keys.split("\n")

            # print(splited_text_keys)
            first_keys = splited_text_keys[1:6]
            second_keys = splited_text_keys[7:12]
            third_keys = splited_text_keys[13:]
            # print(first_keys,second_keys,third_keys)

            self.keys[1] = {"N": first_keys[2][6:], "pub_key": first_keys[3][6:]}
            self.keys[2] = {"N": second_keys[2][6:], "pub_key": second_keys[3][6:]}
            self.keys[3] = {"N": third_keys[2][6:], "pub_key": third_keys[3][6:]}

            # print(self.keys)
            return True
        else:
            return False

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.client_data = ClientData()
        self.server_data = ServerData()

        isKeysLoaded = self.server_data.load_keys_from_file("./server_keys.txt")
        
        if isKeysLoaded:
            self.log_event("Ключи сервера успешно установлены")
        else:
            self.log_event("Произошла ошибка при установке ключей сервера")
            

        # Инициализация кнопок

        self.ui.actionLogin.triggered.connect(self.onActionLoginClicked)
        self.ui.btn_send_msg.clicked.connect(self.send_message)
        self.ui.btn_gen_128_bits.clicked.connect(self.gen_128_bits)
        self.ui.btn_gen_256_bits.clicked.connect(self.gen_256_bits)
        self.ui.actionRegister.triggered.connect(self.request_pq)
    
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
        """
        Запуск формы для логина клиента
        """
        reg_form = RegistrationForm(self)
        reg_form.exec()
        creds = reg_form.get_current_user_credits()
        self.client_data.isRegistered = True
        self.client_data.username = creds[0]
        self.client_data.password = creds[1]
        # reg_form.

    def log_event(self, text):
        """
        Логирование событий в поле log_box
        """
        self.ui.log_box.append(text)

    def factorize(self, n):
        """
        функция для факторизации небольших чисел на основе модуля pyecm
        """
        return list(factors(n, False, True, 10, 1))

    def gen_128_bits(self):
        """
        Функция генерирования рандомного вектора 128 битов 
        """
        curr = self.ui.line_edit_128bits.text()

        if curr != "":
            self.ui.line_edit_128bits.setText("")

        new_IV = gen_key(128)

        self.ui.line_edit_128bits.setText(new_IV)

    def gen_256_bits(self):
        """
        Функция генерирования рандомного вектора 256 битов 
        """
        curr = self.ui.line_edit_256bits.text()

        if curr != "":
            self.ui.line_edit_256bits.setText("")

        new_IV = gen_key(256)

        self.ui.line_edit_256bits.setText(new_IV)


    def __listen_for_messages(self):
        """
        Метод запускаемый в отдельном потоке от ui для того чтобы принимать сообщения и выводить их в поле чата
        """
        for note in self.conn.ChatStream(chat.Empty()):  # this line will wait for new messages from the server!
            print("R[{}] {}".format(note.name, note.message))  # debugging statement
            # self.chat_list.insert(END, "[{}] {}\n".format(note.name, note.message))  # add the message to the UI
            self.ui.chat_field_msg.append("[{}] {}\n".format(note.name, note.message))

    def send_message(self, event):
        """
        Метод отправки сообщения
        """
        # message = self.entry_message.get()  # retrieve message from the UI

        if self.client_data.isRegistered == False:
            message_box("Регистрация не пройдена!", "Error!",
                    QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None

        message = self.ui.text_input_msg.toPlainText()

        if message != '':
            n = chat.Note()  # create protobug message (called Note)
            n.name = self.client_data.username  # set the username
            n.message = message  # set the actual message of the note
            print("S[{}] {}".format(n.name, n.message))  # debugging statement
            try:
                self.conn.SendNote(n)  # send the Note to the server
            except Exception:
                message_box("Проблема при отправке сообщения!", "Error!",
                    QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
                return None

    def request_pq(self):
        """
        Функция, которая вызывается для регистрации нового клиента и запрашивает параметры от сервера
        """
        client_nonce = self.ui.line_edit_128bits.text()

        if client_nonce == "":
            message_box("IV 128 bit не задан", "Error!",
                QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None

        request = chat.req_pq()
        request.nonce = client_nonce

        try:
            response = self.conn.RequestPQ(request)
        except Exception as e:
            print(e)
            message_box("Запрос регистрации клиента неудачен", "Error!",
                QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None

        print(response)

        # Проверяем идентификатор nonce
        if client_nonce != response.nonce:
            self.log_event("Предположительно неверный nonce в ответ от сервера")
            message_box("Не удалось верифицировать сервер, неверный идентификатор nonce. Повторите попытку регистрации.", "Error!",
                QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None

        # Проверяем по полученному хэшу наличие открытого ключа

        self.client_data.server_pub_key_fingerprint = response.pub_key_fingerprint

        for i in range(1, 4):
            current_key = self.server_data.keys[i] 
            rsa_fingerprint = sha_one_process(current_key["N"]+current_key["pub_key"])
            rsa_fingerprint = util.hex2ba(rsa_fingerprint)
            rsa_fingerprint = rsa_fingerprint.to01()[96:]
            if self.client_data.server_pub_key_fingerprint == rsa_fingerprint:
                self.log_event("Хэш ключа верифицирован.")
                self.server_data.current_key_id = i
                break
        else:
            self.log_event("Не найдено представление открытого ключа сервера в текущих ключах")
            message_box("Не удалось верифицировать сервер, нет соответствующего открытого ключа. Повторите попытку регистрации.", "Error!",
                QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None           


        # Сохраняем серверный nonce 
        self.server_data.server_nonce = response.server_nonce

        # Пытаемся факторизовать полученное число (Proof of work)
        proof_result = self.factorize(int(response.pq, 10))

        if len(proof_result) == 1:
            self.log_event("Не удалось факторизовать число. Повторите попытку регистрации.")
            message_box("Не удалось факторизовать число. Повторите попытку регистрации.", "Error!",
                QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None

        else:
            self.client_data.p = proof_result[0]
            self.client_data.q = proof_result[1]
            self.log_event(f"Факторизованные числа p = {self.client_data.p} & q = {self.client_data.q}")

        # Формируем вызов второго запроса

        self.request_dh()

    def request_dh(self):



        pass

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
