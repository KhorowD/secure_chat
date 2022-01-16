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
import rsa
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
        self.pq = ""
        self.p = 0
        self.q = 0
        self.server_pub_key_fingerprint = ""
        self.dh_p = ""
        self.dh_g = ""
        self.dh_pub_key = ""
        self.dh_priv_key = ""

        

class ServerData():
    """
    Структура содержащая информацию о сервере 
    """
    def __init__(self) -> None:
        self.keys = {} #Кортеж ключей который загружаем из файла
        self.current_key_id = 0
        self.server_nonce = ""
        self.rsa_pub_key = ""
        self.rsa_n_value = ""
        self.dh_pub_key = ""


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

    def make_encrypted_data(self):
        """
        Функция предназначена для создания шифрованных данных,
        Отправляемых на втором шаге авторизации, для выработки ключей DH
        
        
        Здесь на выходе мы получаем строку зашифрованную строку

        data:
            pq
            p
            q
            c_nonce128
            s_nonce128
            c_new_nonce256
        """
        # ВЫчисляем новый nonce клиента (256 бит)
        client_new_nonce = self.ui.line_edit_256bits.text()

        if client_new_nonce == "":
            message_box("IV 256 bit не задан", "Error!",
                QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None

        self.client_data.nonce256 = client_new_nonce

        data = self.client_data.pq + "\n" + self.client_data.p.digits() + "\n" + self.client_data.q.digits()
        data += "\n" + self.client_data.nonce128
        data += "\n" + self.server_data.server_nonce
        data += "\n" + self.client_data.nonce256

        print(f"DH req data to encrypt = {data}")

        sha1_data = sha_one_process(data)
        
        print(f"DH req SHA1(data) to encrypt = {sha1_data}")

        data_with_hash = sha1_data +"\n"+ data

        print(f"DH req data_with_hash to encrypt = {data_with_hash}")
        print(f"DH req data_with_hash len = {len(data_with_hash)}")

        prepared_data_with_hash = rsa.to_bytes(data_with_hash)

        encrypted_data = rsa.encode(prepared_data_with_hash, "0x" + self.server_data.rsa_pub_key, "0x" + self.server_data.rsa_n_value)

        encrypted_data = "\n".join(encrypted_data)

        print(encrypted_data)

        return encrypted_data       

    def kdf(self, server_nonce, nonce_new):
        """
        Функция kdf - Для формирования временного ключа на основе nonce
        """

        sha_nonces_1 = sha_one_process(nonce_new + server_nonce)

        sha_nonces_2 = sha_one_process(server_nonce + nonce_new)

        sha_nonces_3 = sha_one_process(nonce_new + nonce_new)

        print(sha_nonces_1, sha_nonces_2, sha_nonces_3)

        tmp_gost_key = util.hex2ba(sha_nonces_1).to01() + util.hex2ba(sha_nonces_2[:24]).to01()
        
        tmp_gost_iv = util.hex2ba(sha_nonces_2[24:41]).to01() + util.hex2ba(sha_nonces_3).to01() + nonce_new[:32]

        return tmp_gost_key, tmp_gost_iv

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

        # Сохраняем nonce клиента

        self.client_data.nonce128 = client_nonce
        

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
                self.server_data.rsa_n_value = current_key["N"]
                self.server_data.rsa_pub_key = current_key["pub_key"]
                break
        else:
            self.log_event("Не найдено представление открытого ключа сервера в текущих ключах")
            message_box("Не удалось верифицировать сервер, нет соответствующего открытого ключа. Повторите попытку регистрации.", "Error!",
                QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None           


        # Сохраняем серверный nonce 
        self.server_data.server_nonce = response.server_nonce

        # Сохраняем полученный pq
        self.client_data.pq = response.pq

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

        # Формируем ответ запроса 

        request = chat.req_DH_params()

        request.nonce = self.client_data.nonce128
        request.server_nonce = self.server_data.server_nonce
        request.p = str(self.client_data.p)
        request.q = str(self.client_data.q)
        request.public_key_fingerprint = self.client_data.server_pub_key_fingerprint
        request.encrypted_data = self.make_encrypted_data()

        try:
            response = self.conn.RequestDH(request)
        except Exception as e:
            print(e)
            message_box("Запрос регистрации клиента неудачен", "Error!",
                QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None

        # Обрабатываем полученный ответ

        # print(response)

        if response.nonce == self.client_data.nonce128 and response.server_nonce == self.server_data.server_nonce:
            print("Ответ на запрос DH получен")
            self.log_event("Ответ на запрос DH получен")
        else:
            print("Ответ на запрос DH не верифицирован")
            self.log_event("Ответ на запрос DH не верифицирован. Неверные nonce от сервера")

        # Формируем ключи для расшифровки запроса
        tmp_gost_key, tmp_gost_iv = self.kdf(self.server_data.server_nonce, self.client_data.nonce256)        

        data_to_decrypt = gost.from_hex(response.encrypted_data)

        prepared_keys = [tmp_gost_key[x:x + 32] for x in range(0, len(tmp_gost_key), 32)]

        decrypted_data = gost.mode_OFB(data_to_decrypt, prepared_keys, tmp_gost_iv[:64], None, reverse=True)

        decrypted_data = gost.to_str(decrypted_data).split("\n")

        # Проверяем валидность полученных данных

        data_answer_hash = decrypted_data[0]

        checked_payload = "\n".join(decrypted_data[i] for i in range(1, 7))

        payload_hash = sha_one_process(checked_payload)

        print(payload_hash)

        if data_answer_hash == payload_hash:
            print("Данные в запросе DH верифицированы")
            self.log_event("Данные в запросе DH верифицированы")
        else:
            print("Данные на запрос DH не верифицированы")
            self.log_event("Данные на запрос DH не верифицированы. Неверный hash") 

        print(decrypted_data)

        # Устанавливаем полученные значения
        self.ui.line_edit_dh_g.setText(decrypted_data[3])
        self.ui.line_edit_dh_p.setText(decrypted_data[4])

        # self.client_data.dh

        # self.server_data.dh_pub_key = 

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
