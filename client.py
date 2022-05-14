import sys
import threading
from google.protobuf import message
from bitarray import util
from pprint import pprint
import yaml


import grpc
import generated.chat_pb2 as chat
import generated.chat_pb2_grpc as rpc

from PyQt5 import QtCore, QtGui, QtWidgets
import ui.client_ui as ui
from ui.registration_dialog import Ui_RegisterForm

from modules.gamma import gen_key
from modules.pyecm import factors
from modules.sha_one import sha_one_process
import modules.rsa as rsa
import modules.gost as gost
import modules.dh as diffie_hellman
from cryptography.hazmat.primitives.asymmetric import dh
from modules.client_context import ClientContext

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

class MsgToServer():
    """
    Структура для формирования сообщения на сервер
    """
    def __init__(self) -> None:
        self.auth_key_id = ""
        self.msg_type = ""
        self.msg_key = ""
        self.encrypted_data = ""

class MsgE2E():
    """
    Структура для формирования сообщения по сквозному шифрованию
    """
    def __init__(self) -> None:
        self.key_fingerprint = ""
        self.msg_key = ""
        self.encrypted_data = ""
    

# class ClientData():
#     """
#     Структура для хранения данных пользователя в одном месте
#     """
#     def __init__(self) -> None:
#         self.username = ""
#         self.password = ""
#         self.key_1 = ""
#         self.key_2 = ""
#         self.isRegistered = False #Если пользователь залогинился, тогда ставим True
#         self.isRegisteredRemote = False #Если пользователь прошел регистрацию устройства, ставим True
#         self.nonce_128 = ""
#         self.nonce_256 = ""
#         self.pq = ""
#         self.p = 0
#         self.q = 0
#         self.server_pub_key_fingerprint = ""
#         self.dh_p = ""
#         self.dh_g = ""
#         self.dh_pub_key = ""
#         self.dh_priv_key = ""
#         self.auth_key = ""
#         self.auth_key_hash = ""
#         self.chats = {}
#         self.tgt_user = ""

        

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
        self.last_msg_time = 0.0


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

        # self.client_data = ClientData()
        self.client_data = ClientContext()
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
        self.ui.btn_start_chat.clicked.connect(self.accept_tgt_username)
        self.ui.actionSave_session_file.triggered.connect(self.save_session_to_file)
        self.ui.actionUpload_Session.triggered.connect(self.read_session_from_file)
    

        # # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.ChatServerStub(channel)
        # create new listening thread for when new message streams come in
        threading.Thread(target=self.__listen_for_messages, daemon=True).start()
        
    def accept_tgt_username(self):

        tgt_username = self.ui.line_edit_chat_tgt.text()

        self.client_data.tgt_user = tgt_username

    def onActionLoginClicked(self):
        """
        Запуск формы для логина клиента
        """
        reg_form = RegistrationForm(self)
        reg_form.exec()
        credentials = reg_form.get_current_user_credits()
        self.client_data.isRegistered = True
        self.client_data.username = credentials[0]
        self.client_data.password = credentials[1]

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
            c_nonce_128
            s_nonce_128
            c_new_nonce_256
        """
        # ВЫчисляем новый nonce клиента (256 бит)
        client_new_nonce = self.ui.line_edit_256bits.text()

        if client_new_nonce == "":
            message_box("IV 256 bit не задан", "Error!",
                QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None

        self.client_data.nonce_256 = client_new_nonce

        data = self.client_data.pq + "\n" + self.client_data.p.digits() + "\n" + self.client_data.q.digits()
        data += "\n" + self.client_data.nonce_128
        data += "\n" + self.server_data.server_nonce
        data += "\n" + self.client_data.nonce_256

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

    def gen_client_dh_keys(self):
        """
        Функция отвечает за формирование ключей DH клиента
        """
        # Расчитываем параметры DH 
        pn = dh.DHParameterNumbers(int(self.client_data.dh_p[2:],16), int(self.client_data.dh_g[2:],16))
        parameters_dh = pn.parameters()

         # Расчитываем ключи для сервера
        client_dh_priv_key, client_dh_pub_key = diffie_hellman.gen_key_pair(parameters_dh.parameter_numbers().p, parameters_dh.parameter_numbers().g)
        # print(server_dh_priv_key, server_dh_pub_key)

       
        #Сохраняяем ключи в контексте клиента
        self.client_data.dh_priv_key = client_dh_priv_key
        self.client_data.dh_pub_key = client_dh_pub_key

        self.log_event("Ключи DH клиента успешно созданы")

        # Устанавливаем ключи клиента в UI
        self.ui.line_edit_dh_priv_key.setText(str(client_dh_priv_key))
        self.ui.line_edit_dh_pub_key.setText(str(client_dh_pub_key))

    def chek_set_DH_answer(self, answ_hash):

        ans_1_hash = util.hex2ba(sha_one_process(self.client_data.nonce_256 + "00000001" + util.hex2ba(self.client_data.auth_key_hash).to01()[96:])).to01()

        ans_2_hash = util.hex2ba(sha_one_process(self.client_data.nonce_256 + "00000011" + util.hex2ba(self.client_data.auth_key_hash).to01()[96:])).to01()

        if ans_1_hash == answ_hash:
            return True

        elif ans_2_hash == answ_hash:
            return False

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

    def decrypt_msg(self, encrypted_data, key, iv):

        data_to_decrypt = gost.from_hex(encrypted_data)

        prepared_keys = [key[x:x + 32] for x in range(0, len(key), 32)]

        decrypted_data = gost.mode_OFB(data_to_decrypt, prepared_keys, iv[:64], None, reverse=True)

        decrypted_data = gost.to_str(decrypted_data).split("\n")
        
        return decrypted_data

    def encrypt_msg(self, data_to_encrypt, key, iv):
        
        prepared_keys = [key[x:x + 32] for x in range(0, len(key), 32)]

        print(data_to_encrypt)
        print(prepared_keys)

        print(iv[:64], len(iv[:64]))

        try:
            encrypted_data = gost.mode_OFB(data_to_encrypt, prepared_keys, iv[:64], None)
        except Exception as e:
            print(e)
            return chat.Empty()

        return gost.to_hex(encrypted_data)


    def kdf_2(self, auth_key_bits: str, msg_key_bits: str):
        """
        Функция формирования ключа
        """
        part_1 = util.hex2ba(msg_key_bits+auth_key_bits[:256]).to01()
        part_2 = util.hex2ba(auth_key_bits[256:384] + msg_key_bits + auth_key_bits[384:512]).to01()
        part_3 = util.hex2ba(auth_key_bits[512:768] + msg_key_bits).to01()
        part_4 = util.hex2ba(msg_key_bits+auth_key_bits[768:1024]).to01()

        key = part_1[:64] + part_2[64:] + part_3[32:128]
        iv = part_1[64:] + part_2[:64] + part_3[128:] + part_4[:64]

        return key, iv

    def __listen_for_messages(self):
        """
        Метод запускаемый в отдельном потоке от ui для того чтобы принимать сообщения и выводить их в поле чата
        """
        for note in self.conn.ChatStream(chat.Empty()):  # this line will wait for new messages from the server!
            print("R[{}] {}".format(note.src_usr_name, note.msg))  # debugging statement
            # self.chat_list.insert(END, "[{}] {}\n".format(note.name, note.message))  # add the message to the UI
            self.ui.chat_field_msg.append("[{}] {}\n".format(note.src_usr_name, note.msg))

    def send_message(self, event):
        """
        Метод отправки сообщения
        """
        # message = self.entry_message.get()  # retrieve message from the UI

        if self.client_data.isRegistered == False:
            message_box("Регистрация не пройдена!", "Error!",
                    QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None

        if self.client_data.isRegisteredRemote == False:
            message_box("Регистрация клиента удаленно не пройдена!", "Error!",
                    QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None

        message = self.ui.text_input_msg.toPlainText()


        if message != '':
            note = chat.enc_note() # Создаем объект класса сообщение

            note.auth_key_id = self.client_data.auth_key_hash[:64]

            data = self.client_data.username
            data += "\n" + self.client_data.tgt_user
            data += "\n" + message

            msg_key = util.hex2ba(sha_one_process(data)).to01()

            tmp_key, tmp_iv = self.kdf_2(self.client_data.auth_key, msg_key)

            note.msg_key = msg_key
            # Формируем зашифрованное сообщение
            note.encrypted_data = self.encrypt_msg(data, tmp_key, tmp_iv)


        
            # n = chat.Note()  # create protobug message (called Note)
            # n.name = self.client_data.username  # set the username
            # n.message = message  # set the actual message of the note
            # print("S[{}] {}".format(n.name, n.message))  # debugging statement
            try:
                self.conn.SendNote(note)  # send the Note to the server
            except Exception as e:
                message_box("Проблема при отправке сообщения!", "Error!",
                    QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
                print(e)
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

        self.client_data.nonce_128 = client_nonce
        

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

        request.nonce = self.client_data.nonce_128
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

        if response.nonce == self.client_data.nonce_128 and response.server_nonce == self.server_data.server_nonce:
            print("Ответ на запрос DH получен")
            self.log_event("Ответ на запрос DH получен")
        else:
            print("Ответ на запрос DH не верифицирован")
            self.log_event("Ответ на запрос DH не верифицирован. Неверные nonce от сервера")

        # Формируем ключи для расшифровки запроса
        tmp_gost_key, tmp_gost_iv = self.kdf(self.server_data.server_nonce, self.client_data.nonce_256)        

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

        self.client_data.dh_g = decrypted_data[3]
        self.client_data.dh_p = decrypted_data[4]

        self.server_data.dh_pub_key = decrypted_data[5]

        self.server_data.last_msg_time = float(decrypted_data[6])

        self.set_client_dh()

    def set_client_dh(self):

        # Здесь, генерируем ключи клиента
        self.gen_client_dh_keys()

        # Вычисляем auth_key

        print(type(self.server_data.dh_pub_key), self.server_data.dh_pub_key)
        print(type(self.client_data.dh_priv_key), self.client_data.dh_priv_key)
        print(type(self.client_data.dh_p), self.client_data.dh_p)

        auth_key = bin(pow(int(self.server_data.dh_pub_key), self.client_data.dh_priv_key, int(self.client_data.dh_p[2:], 16)))[2:]
        auth_key_hash = sha_one_process(auth_key)


        # Сохраняем aut_key  в контексте клиента
        self.client_data.auth_key = auth_key
        self.client_data.auth_key_hash = auth_key_hash

        # Формируем запрос
        request = chat.set_DH_params()

        request.nonce = self.client_data.nonce_128
        request.server_nonce = self.server_data.server_nonce

        # Формируем данные для шифрования
        data_request = self.client_data.nonce_128
        data_request += "\n" + self.server_data.server_nonce
        data_request += "\n" + "0" #retry_id
        data_request += "\n" + str(self.client_data.dh_pub_key)

        print(f"data_request = {data_request}")

        data_with_hash = sha_one_process(data_request) + "\n" + data_request

        tmp_gost_key, tmp_gost_iv = self.kdf(self.server_data.server_nonce, self.client_data.nonce_256)

        data_to_encrypt = data_with_hash + "\n" + tmp_gost_key + "\n" + tmp_gost_iv

        prepared_keys = [tmp_gost_key[x:x + 32] for x in range(0, len(tmp_gost_key), 32)]

        # print(data_to_encrypt)
        # print(prepared_keys)

        # print(tmp_gost_iv[:64], len(tmp_gost_iv[:64]))

        try:
            encrypted_data = gost.mode_OFB(data_to_encrypt, prepared_keys, tmp_gost_iv[:64], None)
        except Exception as e:
            print(e)
            self.log_event("Процесс установки ключей DH клиента нарушен. \nПовторите попытку")
        
        request.encrypted_data = gost.to_hex(encrypted_data)

        try:
            response = self.conn.SetClientDH(request)
        except Exception as e:
            print(e)
            message_box("Запрос установки ключей DH клиента неудачен", "Error!",
                QtWidgets.QMessageBox.Critical, QtWidgets.QMessageBox.Ok)
            return None


        print(response)

        # Проверка сессии

        if response.nonce == self.client_data.nonce_128 and response.server_nonce == self.server_data.server_nonce:
            print("Ответ на запрос по установке ключа DH получен")
            self.log_event("Ответ на запрос по установке ключа DH получен")
        else:
            print("Ответ на запрос по установке ключа DH не верифицирован")
            self.log_event("Ответ на запрос по установке ключа DH не верифицирован. Неверные nonce от сервера")

        isSessionComplete = self.chek_set_DH_answer(response.new_nonce_hash_type)

        if isSessionComplete:
            self.log_event("Сессия с сервером установлена!")
            message_box("Регистрация пройдена, сессия установлена!", "Error!",
                        QtWidgets.QMessageBox.Information,
                        QtWidgets.QMessageBox.Ok)
            # Устанавливаем флаг что прошли регистрацию
            self.client_data.isRegisteredRemote = True


            #Save user configuration 
            # with open("user_config.txt", "w") as conf:
            #     pprint(self.client_data.__dict__, conf)

            return False
        else:
            self.log_event("Сервер ответил ошибкой на запрос установки сессии. Повторите регистрацию пользователя.")
            message_box("Сервер ответил ошибкой на запрос установки сессии. Повторите регистрацию пользователя.", "Error!",
                        QtWidgets.QMessageBox.Critical,
                        QtWidgets.QMessageBox.Ok)
            # Устанавливаем флаг что прошли регистрацию
            self.client_data.isRegisteredRemote = False
            return False

    def fill_user_ui_crypto_fields(self):
        """
        Заполняем ui поля данными клиента
        """
        self.ui.line_edit_128bits.setText(self.client_data.nonce_128)
        self.ui.line_edit_256bits.setText(self.client_data.nonce_256)
        self.ui.line_edit_dh_g.setText(self.client_data.dh_g)
        self.ui.line_edit_dh_p.setText(self.client_data.dh_p)
        self.ui.line_edit_dh_priv_key.setText(self.client_data.dh_priv_key)
        self.ui.line_edit_dh_pub_key.setText(self.client_data.dh_pub_key)

    def setup_session(self, session: dict):
        """
        Установка данных клиента из файла
        """
        self.client_data.auth_key = str(session["crypto"]["auth_key"])
        self.client_data.auth_key_hash = str(session["crypto"]["auth_key_hash"])
        self.client_data.nonce_128 = str(session["crypto"]["nonce_128"])
        self.client_data.nonce_256 = str(session["crypto"]["nonce_256"])
        
        self.client_data.dh_p = hex(session["crypto"]["dh"]["p"])
        self.client_data.dh_g = hex(session["crypto"]["dh"]["g"])
        self.client_data.dh_priv_key= str(session["crypto"]["dh"]["priv_key"])
        self.client_data.dh_pub_key = str(session["crypto"]["dh"]["pub_key"])

        self.client_data.username = session["user"]["name"]
        self.client_data.password = session["user"]["pass_md5_hash"]
        self.client_data.isRegistered = session["user"]["local_registration"]
        self.client_data.isRegisteredRemote = session["user"]["remote_registration"]

        self.client_data.p = session["pow"]["p"]
        self.client_data.q = session["pow"]["q"]
        self.client_data.pq = session["pow"]["pq"]

        self.client_data.server_pub_key_fingerprint = session["server_data"]["pub_key_fingerprint"]

        message_box("Сессия установлена успешно!", "OK!",
                        QtWidgets.QMessageBox.Information,
                        QtWidgets.QMessageBox.Ok)

        pprint(self.client_data.__dict__)

        self.fill_user_ui_crypto_fields()

    def save_session_to_file(self):
        with open("./sessions/user_config.txt", "w") as conf:
                pprint(self.client_data.__dict__, conf)

        with open(self.client_data.username+"_session.yml", "w") as conf:
            try:
                yaml.dump(self.client_data.__dict__, conf)
            except Exception as e:
                print(e)
                message_box("Сессия клиента не сохранена!", "Error!",
                        QtWidgets.QMessageBox.Critical,
                        QtWidgets.QMessageBox.Ok)
                return None


    def read_session_from_file(self):

        file_name = QtWidgets.QFileDialog.getOpenFileName(
                self, "Read text", "./", "YAML (*.yml)")
        if not file_name[0]:
            return None
        try:
            # with open(file_name[0], "r") as file:
            #     # config = yaml.load(file, Loader=SafeLoader).get("ping_script", {})
            #     session = yaml.safe_load(file)
            #     print(session)
            # Читаем конфиг
            session = ClientContext().read_config(file_name[0])

        except FileNotFoundError:
            message_box("Файл не существует!", "Error!",
                        QtWidgets.QMessageBox.Critical,
                        QtWidgets.QMessageBox.Ok)
            return None

        try:
            self.setup_session(session)
        except Exception as e:
            print(e)

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
