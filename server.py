from concurrent import futures
import re
from urllib import response

import ui.server_ui as ui

import grpc
import time
import sys
import threading
from random import randint
from bitarray import util

import generated.chat_pb2 as chat
import generated.chat_pb2_grpc as rpc

from modules.gamma import gen_key as gen_IV
from modules.base_func import prime_gen_rm
from modules.sha_one import sha_one_process
import modules.gost as gost
import modules.rsa as rsa
import modules.dh as diffie_hellman
from cryptography.hazmat.primitives.asymmetric import dh
from modules.client_context import ClientContext

from PyQt5 import QtCore, QtGui, QtWidgets

MSG_SRV_TYPE = {0: "SET_USER_CREDS", 
                1: "E2E_DH_REQUEST",
                2: "CHECK_E2E_REQUEST",
                3: "PASS_E2E_REQUEST_TO_CLIENT",
                4: "ACCEPT_E2E_REQUEST_FROM_CLIENT",
                5: "PASS_E2E_PARAMS_FROM_CLIENT",
                6: "CHECK_ACCEPTED_REQUEST_FROM_CLIENT"}

MSG_CLIENT_TYPE = {1: "MSG", 2: "FILE"}

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

# class ClientContext():
#     """
#     Структура содержащая информацию о подключаемых клиентах
#     """
#     def __init__(self) -> None:
#         self.username = ""
#         self.nonce = ""
#         self.nonce_new = ""
#         self.pq = ""
#         self.p = ""
#         self.q = ""
#         self.server_nonce = ""
#         self.server_rsa_priv_key = ""
#         self.server_rsa_n_value = ""
#         self.dh_pub_key = ""
#         self.dh_priv_key = ""
#         self.dh_g = ""
#         self.dh_p = ""
#         self.dh_server_pub_key = ""
#         self.dh_server_priv_key = ""
#         self.auth_key_hash = ""
#         self.auth_key = ""
#         self.chats = {}
#         self.e2e_requests = []
#         self.e2e_accepted_requests = {}
#         self.e2e_passed_parameters = {}
#         self.e2e_g = ""
#         self.e2e_p = ""
#         self.e2e_dh_pub_key = ""
        
        


#     def __print__(self):
#         pprint.pprint(self.__dict__)
        

class ServerData():
    """
    Структура содержащая информацию о сервере 
    """
    def __init__(self) -> None:
        self.keys = {} #Кортеж ключей который загружаем из файла
        self.rsa_pub_key = ""
        self.rsa_priv_key = ""
        self.rsa_n_value = ""
        self.dh_pub_key = ""
        self.dh_priv_key = ""
        self.server_nonce = ""
        self.pq = ""
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

            self.keys[1] = {"N": first_keys[2][6:], "pub_key": first_keys[3][6:], "priv_key" : first_keys[4][6:] }
            self.keys[2] = {"N": second_keys[2][6:], "pub_key": second_keys[3][6:], "priv_key" : second_keys[4][6:] }
            self.keys[3] = {"N": third_keys[2][6:], "pub_key": third_keys[3][6:], "priv_key" : third_keys[4][6:] }

            # print(self.keys)
            return True
        else:
            return False

server_data = ServerData()

class LogEventSignal(QtCore.QObject):
    log_event_sig = QtCore.pyqtSignal(str)

class MainWindow(QtWidgets.QMainWindow):

    log_event = QtCore.pyqtSlot(str)


    def __init__(self):
        super().__init__()
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.server = None
        # server_data = ServerData()
        isKeysLoaded = server_data.load_keys_from_file("./server_keys.txt")
        
        if isKeysLoaded:
            self.log_event("Ключи сервера успешно установлены")
        else:
            self.log_event("Произошла ошибка при установке ключей сервера")


        self.btn_init() #Инициализируем кнопки

        # self.server = self.make_server()
        threading.Thread(target=self.make_server, daemon=True).start()

    
    # тут описываем действия окна сервера

    def btn_init(self):
        self.ui.btn_clear_log_box.clicked.connect(self.clear_log_box)
        self.ui.btn_reset_sessions.clicked.connect(self.reset_sessions)
        self.ui.btn_start_recevieng_msg.clicked.connect(self.start_recv)
        self.ui.btn_stop_recevieng_msg.clicked.connect(self.stop_recv)

    def clear_log_box(self):
        self.ui.log_box.clear()

    def reset_sessions(self):
        pass

    def start_recv(self):
        pass

    def stop_recv(self):
        pass
    
    def make_server(self):
        port = 8080  # a random port for the server to run on
        # the workers is like the amount of threads that can be opened at the same time, when there are 10 clients connected
        # then no more clients able to connect to the server.
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
        rpc.add_ChatServerServicer_to_server(ChatServer(), self.server)  # register the server to gRPC
        # gRPC basically manages all the threading and server responding logic, which is perfect!
        print('Starting server. Listening...')
        self.server.add_insecure_port('[::]:' + str(port))
        self.server.start()
        # Server starts in background (in another thread) so keep waiting
        # if we don't wait here the main thread will end, which will end all the child threads, and thus the threads
        # from the server won't continue to work and stop the server
        try:
            while True:
                time.sleep(64 * 64 * 100)
        except (KeyboardInterrupt, SystemExit):
            self.server.stop(0)

    def log_event(self, text):
        self.ui.log_box.append(text)

class ChatServer(rpc.ChatServerServicer):  # inheriting here from the protobuf rpc file which is generated

    def __init__(self):
        # List with all the chat history
        self.chats = []
        self.clients = []
        
    def make_error_message(self, text):
        """
        Функция формирующая сообщение об ошибке
        """
        pass

    def kdf(self, server_nonce, nonce_new):

        sha_nonces_1 = sha_one_process(nonce_new + server_nonce)

        sha_nonces_2 = sha_one_process(server_nonce + nonce_new)

        sha_nonces_3 = sha_one_process(nonce_new + nonce_new)

        print(sha_nonces_1, sha_nonces_2, sha_nonces_3)

        tmp_gost_key = util.hex2ba(sha_nonces_1).to01() + util.hex2ba(sha_nonces_2[:24]).to01()
        
        tmp_gost_iv = util.hex2ba(sha_nonces_2[24:41]).to01() + util.hex2ba(sha_nonces_3).to01() + nonce_new[:32]

        return tmp_gost_key, tmp_gost_iv

    def calc_aut_key(self, curr_client : ClientContext):
        """
        Функция вычисления поля auth_key
        """
        print(type(curr_client.dh_pub_key), curr_client.dh_pub_key)
        print(type(curr_client.dh_server_priv_key), curr_client.dh_server_priv_key)
        print(type(curr_client.dh_p), curr_client.dh_p)

        return pow(int(curr_client.dh_pub_key), curr_client.dh_server_priv_key, int(curr_client.dh_p[2:], 16))

    def make_DH_response(self, response: chat.res_DH_params, curr_client: ClientContext):
        """
        Функция формирования ответа на втором шаге авторизации

        Здесь отправляются данные для DH

        """
        # Устанавливаем данные для проверки сессии
        response.nonce = curr_client.nonce
        response.server_nonce = curr_client.server_nonce

        # Расчитываем параметры DH 
        parameters_dh = dh.generate_parameters(2, 2048)

         # Расчитываем ключи для сервера
        server_dh_priv_key, server_dh_pub_key = diffie_hellman.gen_key_pair(parameters_dh.parameter_numbers().p, parameters_dh.parameter_numbers().g)
        print(server_dh_priv_key, server_dh_pub_key)

       
        #Сохраняяем ключи в контексте клиента
        curr_client.dh_g = hex(parameters_dh.parameter_numbers().g)
        curr_client.dh_p = hex(parameters_dh.parameter_numbers().p)
        curr_client.dh_server_pub_key = server_dh_pub_key
        curr_client.dh_server_priv_key = server_dh_priv_key

        server_time = time.time()

        server_data.last_msg_time = server_time

        data_answer = (curr_client.nonce +"\n"+curr_client.server_nonce + "\n"
                        + curr_client.dh_g + "\n" + curr_client.dh_p + "\n" 
                        + str(curr_client.dh_server_pub_key) + "\n" + str(server_time))

        data_answer_with_hash = sha_one_process(data_answer) + "\n" + data_answer

        tmp_gost_key, tmp_gost_iv = self.kdf(curr_client.server_nonce, curr_client.nonce_new)

        print(f"key = {tmp_gost_key}\niv = {tmp_gost_iv}")
        print(f"key_len = {len(tmp_gost_key)}\niv_len = {len(tmp_gost_iv)}")

        data_to_encrypt = data_answer_with_hash + "\n" + tmp_gost_key + "\n" + tmp_gost_iv

        prepared_keys = [tmp_gost_key[x:x + 32] for x in range(0, len(tmp_gost_key), 32)]

        print(data_to_encrypt)
        print(prepared_keys)

        print(tmp_gost_iv[:64], len(tmp_gost_iv[:64]))

        try:
            encrypted_data = gost.mode_OFB(data_to_encrypt, prepared_keys, tmp_gost_iv[:64], None)
        except Exception as e:
            print(e)
            return chat.Empty()


        # Формируем ответ в котором отправляем параметры для DH
        response = chat.res_DH_params()
        response.nonce = curr_client.nonce
        response.server_nonce = curr_client.server_nonce
        response.encrypted_data = gost.to_hex(encrypted_data)

        return response

    def dh_gen_fail(self, client: ClientContext):
        """
        Формируется сообщение об неудачной установки ключей DH клиента
        """

        response = chat.dh_gen_ans()
        response.nonce = client.nonce
        response.server_nonce = client.server_nonce
        response.new_nonce_hash_type = util.hex2ba(sha_one_process(client.nonce_new + "00000011" + util.hex2ba(client.auth_key_hash).to01()[96:])).to01()

        return response

    def dh_gen_ok(self, client: ClientContext):
        """
        Формируется сообщение об удачной установки ключей DH клиента
        """

        response = chat.dh_gen_ans()
        response.nonce = client.nonce
        response.server_nonce = client.server_nonce
        response.new_nonce_hash_type = util.hex2ba(sha_one_process(client.nonce_new + "00000001" + util.hex2ba(client.auth_key_hash).to01()[96:])).to01()

        print("Auth_key между клиентом и сервером установлен!")

        return response

    # Поток предназначенный для отправки сообщений клиентам
    def ChatStream(self, request_iterator, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages
        :param request_iterator:
        :param context:
        :return:
        """
        lastindex = 0
        # For every client a infinite loop starts (in gRPC's own managed thread)
        while True:
            # Check if there are any new messages
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n

    def SendNote(self, new_note: chat.enc_note, context):
        """
        This method is called when a clients sends a Note to the server.
        :param request:
        :param context:
        :return:

        Метод вызываемый, когда пользователь хочет отправить сообщение 

        Получает зашифрованное на ключах сервера сообщение (chat.enc_note) от src_usr_name

        Полученное сообщение дешифруется и формируется структура note
        """
        # # this is only for the server console
        # print("[{}] {}".format(request.name, request.message))
        # # Add it to the chat history
        # self.chats.append(request)

        # Сначала расшифруем сообщение

        # Определяем по auth_key_hash[:64] = auth_key_id кому оно направлено и вятгиваем контекст этого клиента

        current_client : ClientContext = None

        for client in self.clients:
            if client.auth_key_hash[:64] == new_note.auth_key_id:
                current_client = client

        # После определения контекста вызываем kdf_2(c_auth_key, msg_key)
        tmp_key, tmp_iv = self.kdf_2(current_client.auth_key, new_note.msg_key)

        # расшифруем с ГОСТ

        decrypted_data = self.decrypt_msg(new_note.ecnrypted_data, tmp_key, tmp_iv)

        # формируем итоговое сообщение

        note = chat.note() 

        note.src_usr_name = decrypted_data[0]
        note.tgt_usr_name = decrypted_data[1]
        note.msg = decrypted_data[2]

        self.chats.append(note)

        return chat.Empty()  # something needs to be returned required by protobuf language, we just return empty msg

    def RequestPQ(self, request: chat.req_pq, context):
        """
        Вызовываемый клиентом метод, для прохождения pq авторизации
        """
        new_client = ClientContext()

        new_client.nonce = request.nonce

        print(new_client.nonce)
        print(type(new_client.nonce))

        # Формируем ответ сервера
        server_response = chat.res_pq()

        # Устанавливаем nonce клиента
        new_client.nonce = request.nonce
        server_response.nonce = request.nonce

        # Генерируем nonce сервера
        server_response.server_nonce = gen_IV(128)
        # Сохраняем nonce для проверки в последующем
        new_client.server_nonce = server_response.server_nonce


        # Формируем число n для клиента для Prof Of Work
        # Необходимо для защиты от DOS атак

        n = None

        while n == None:

            # Формируем параметры RSA -> p и q
            server_p = int(prime_gen_rm(30), 2)
            server_q = int(prime_gen_rm(30), 2)

            # Вычисляем N
            n =  server_p * server_q

            if n < (pow(2, 63) - 1):
                break
            else:
                n = None
                

        server_response.pq = str(n)

        new_client.pq = server_response.pq

        # Вычисляем отпечаток ключа

        chosen_key_id = randint(1,3)

        current_key = server_data.keys[chosen_key_id] 

        print(current_key)

        rsa_fingerprint = sha_one_process(current_key["N"]+current_key["pub_key"])

        rsa_fingerprint = util.hex2ba(rsa_fingerprint)

        print(len(rsa_fingerprint), rsa_fingerprint)

        rsa_fingerprint = rsa_fingerprint.to01()[96:]

        server_response.pub_key_fingerprint = rsa_fingerprint

        # Добавляем ключи в контекст клиента на сервере

        new_client.server_rsa_n_value = current_key["N"]

        new_client.server_rsa_priv_key = current_key["priv_key"]

        # Добавляем контекст клиента в список

        self.clients.append(new_client)

        # Отправляем ответ сервера
        return server_response

    def RequestDH(self, request: chat.req_DH_params, context):
        """
        Вызовываемый клиентом метод, для прохождения получения параметров DH
        """
        print("start req_DH process")

        print(f"request values:\n {request}")

        try:

            # Опредляем индекс клиента запросившего параметры DH
            current_client_index = None

            for client in self.clients:
                if client.nonce == request.nonce and client.server_nonce == request.server_nonce:
                    current_client_index = self.clients.index(client)
                    print(current_client_index)

        except Exception as e:
            print(e)
            return chat.Empty()

        recv_encrypted_data = request.encrypted_data #.split("\n")

        # print(recv_encrypted_data[0])

        try:
            decoded_data = rsa.decode(recv_encrypted_data, "0x" + self.clients[current_client_index].server_rsa_priv_key, "0x" + self.clients[current_client_index].server_rsa_n_value)
        except Exception as e:
            print(e)
            return chat.Empty()
 
        # print(f"decoded_data rsa = {decoded_data}")

        decoded_serialized_data = "".join(chr(x) for x in decoded_data)

        # decoded_data = decoded_data.split(" ")

        # print(f"DH req decoded data: \n{decoded_serialized_data}")

        decoded_request_values = decoded_serialized_data.split("\n")
        
        # Проверяем достоверность полученных данных с помощью хэша
        decoded_hash = decoded_request_values[0]

        checked_payload = decoded_serialized_data[41:]

        checked_hash = sha_one_process(checked_payload)

        if decoded_hash == checked_hash:
            print("Данные запроса DH верифицированы")
        else:
            print("Данные запроса DH не верифицированы")
            return chat.Empty()

        self.clients[current_client_index].p = decoded_request_values[2]
        self.clients[current_client_index].q = decoded_request_values[3]
        self.clients[current_client_index].nonce_new = decoded_request_values[6]

        self.clients[current_client_index].__print__()

        # Формирум ответ для клиента 
        response = chat.res_DH_params()

        response = self.make_DH_response(response, self.clients[current_client_index])

        return response

    def SetClientDH(self, request: chat.set_DH_params, context):
        """
        Вызовываемый клиентом метод, для установки параметров DH
        """
        print("start set_DH process")

        print(f"request values:\n {request}")

        try:

            # Опредляем индекс клиента запросившего параметры DH
            current_client_index = None

            for client in self.clients:
                if client.nonce == request.nonce and client.server_nonce == request.server_nonce:
                    current_client_index = self.clients.index(client)
                    print(current_client_index)

        except Exception as e:
            print(e)
            print("Клиент не найден")
            return chat.Empty()

        curr_client : ClientContext = self.clients[current_client_index]

        recv_encrypted_data = request.encrypted_data

        # Формируем ключи для расшифровки сообщения 
        tmp_gost_key, tmp_gost_iv = self.kdf(curr_client.server_nonce, curr_client.nonce_new)

        data_to_decrypt = gost.from_hex(recv_encrypted_data)

        prepared_keys = [tmp_gost_key[x:x + 32] for x in range(0, len(tmp_gost_key), 32)]

        decrypted_data = gost.mode_OFB(data_to_decrypt, prepared_keys, tmp_gost_iv[:64], None, reverse=True)

        decrypted_data = gost.to_str(decrypted_data).split("\n")

        print(decrypted_data)

        curr_client.dh_pub_key = decrypted_data[4] # Сохраняем открытый ключ клиента в его контексте

        # Вычисляем auth_key 
        auth_key = bin(self.calc_aut_key(curr_client))[2:]
        auth_key_hash = sha_one_process(auth_key)

        # Проверяем существование клиента с таким же auth_key

        for client in self.clients:
            if client.auth_key_hash == auth_key_hash:
                response = self.dh_gen_fail(curr_client)
                return response

        # Сохранеяем auth_key для текущего клиента
        curr_client.auth_key = auth_key
        curr_client.auth_key_hash = auth_key_hash

        # Проверяем валидность сообщения
        decrypted_data_hash = decrypted_data[0]

        cheked_payload = "\n".join(decrypted_data[i] for i in range(1, 5))

        print(f"cheked_payload = {cheked_payload}")

        cheked_payload_hash = sha_one_process(cheked_payload)

        if decrypted_data_hash == cheked_payload_hash:
            print("Запрос на установку ключей DH Клиента верифицирован")
        else:
            print("Запрос на установку ключей DH Клиента НЕ верифицирован")
            # В случае неудчной попытки (dh_gen_fail)
            return self.dh_gen_fail(curr_client)

        return self.dh_gen_ok(curr_client)


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

    def set_user_creds(self, client: ClientContext, username):
        client.username = username

    def gen_e2e_dh_parameters(self):
        parameters_dh = dh.generate_parameters(2, 2048)
        return parameters_dh.parameter_numbers().p, parameters_dh.parameter_numbers().g

    def SendMessageToServer(self, request: chat.msg_client_server, context):
        """
        Здесь реализовано взаимодействие клиентов и сервера после установки сессии
        """

        # Сначала расшифруем сообщение

        # Определяем по auth_key_hash[:64] = auth_key_id кому оно направлено и вятгиваем контекст этого клиента

        current_client : ClientContext = None

        for client in self.clients:
            if client.auth_key_hash[:64] == request.auth_key_id:
                current_client = client

        # После определения контекста вызываем kdf_2(c_auth_key, msg_key)
        tmp_key, tmp_iv = self.kdf_2(current_client.auth_key, request.msg_key)

        # расшифруем с ГОСТ

        decrypted_data = self.decrypt_msg(request.encrypted_data, tmp_key, tmp_iv)

        # После расшифровки Определеям тип сообщения (msg_type: str_int number)

        msg_type = int(decrypted_data[1])

        if msg_type == 0:
            # Установка данных пользователя
            self.set_user_creds(current_client, decrypted_data[2])
            
            # Формируем ответ
            response = chat.msg_client_server()
            response.auth_key_id = client.auth_key_hash[:64]

            data = gen_IV(64)
            data += "\n" + "STATUS"
            data += "\n" + "OK" 

            msg_key = util.hex2ba(sha_one_process(data)).to01()

            tmp_key, tmp_iv = self.kdf_2(current_client.auth_key, msg_key)

            response.msg_key = msg_key
            # Формируем зашифрованное сообщение
            response.encrypted_data = self.encrypt_msg(data, tmp_key, tmp_iv)

            return response 

        elif msg_type == 1:
            # ЗАпрос на параметры DH

            p , g = self.gen_e2e_dh_parameters()

            current_client.e2e_g = str(g)
            current_client.e2e_p = str(p)
            
            # Формируем ответ

            response = chat.msg_client_server()

            response.auth_key_id = client.auth_key_hash[:64]

            data = gen_IV(64)
            data += "\n" + p
            data += "\n" + g

            msg_key = util.hex2ba(sha_one_process(data)).to01()

            tmp_key, tmp_iv = self.kdf_2(current_client.auth_key, msg_key)

            response.msg_key = msg_key
            # Формируем зашифрованное сообщение
            response.encrypted_data = self.encrypt_msg(data, tmp_key, tmp_iv)

            return response

        elif msg_type == 2:
            
            # ЗАпрос для проверки входящих е2е чаты
            response = chat.msg_client_server()
            response.auth_key_id = client.auth_key_hash[:64]

            if len(current_client.e2e_requests) == 0:
                # В случае если запросов нет
                data = gen_IV(64)
                data += "\n" + "REQUESTS"
                data += "\n" + "0" 

            else:
                # В случае если есть запрос отправляем данные второму клиенту
                data = gen_IV(64)
                data += "\n" + "REQUESTS"
                data += "\n" + current_client.e2e_requests[-1][0] #Установка имени пользователя, запросившего секретный чат
                data += "\n" + current_client.e2e_requests[-1][1] #Установка id 
                data += "\n" + current_client.e2e_requests[-1][2] #Установка открытого ключа пользователя, запросившего секретный чат

            msg_key = util.hex2ba(sha_one_process(data)).to01()

            tmp_key, tmp_iv = self.kdf_2(current_client.auth_key, msg_key)

            response.msg_key = msg_key
            # Формируем зашифрованное сообщение
            response.encrypted_data = self.encrypt_msg(data, tmp_key, tmp_iv)

            return response

            
        elif msg_type == 3:
            # Запрос на отправку запроса для установления е2е с другим клиентом
            # 1. целевой клиент 2. id сессии 3. откртый ключ клиента источника

            tgt_username = decrypted_data[2]

            # Ищем целевого пользователя и устанавливаем запрос для него
            for client in self.clients:
                if client.username == tgt_username:
                    client.e2e_requests.append([current_client.username, decrypted_data[3], decrypted_data[4]])

            # Формируем ответ
            response = chat.msg_client_server()
            response.auth_key_id = client.auth_key_hash[:64]

            data = gen_IV(64)
            data += "\n" + "STATUS"
            data += "\n" + "OK" 

            msg_key = util.hex2ba(sha_one_process(data)).to01()

            tmp_key, tmp_iv = self.kdf_2(current_client.auth_key, msg_key)

            response.msg_key = msg_key
            # Формируем зашифрованное сообщение
            response.encrypted_data = self.encrypt_msg(data, tmp_key, tmp_iv)

            return response 


        elif msg_type == 4:
            # Принятие е2е запроса от клиента
            # 1. Status 2. tgt_username
            
            if decrypted_data[2] == "ACCEPT":
                # Формируем ответ

                response = chat.msg_client_server()

                response.auth_key_id = client.auth_key_hash[:64]

                for client in self.clients:
                    if client.username == decrypted_data[3]:
                        tgt_client = client

                data = gen_IV(64)
                data += "\n" + tgt_client.e2e_p
                data += "\n" + tgt_client.e2e_g

                tgt_client.e2e_accepted_requests[current_client.username] = "ACCEPT"

                msg_key = util.hex2ba(sha_one_process(data)).to01()

                tmp_key, tmp_iv = self.kdf_2(current_client.auth_key, msg_key)

                response.msg_key = msg_key
                # Формируем зашифрованное сообщение
                response.encrypted_data = self.encrypt_msg(data, tmp_key, tmp_iv)

                return response

            elif decrypted_data[2] == "REJECT":
                # Формируем ответ

                response = chat.msg_client_server()

                response.auth_key_id = client.auth_key_hash[:64]

                for client in self.clients:
                    if client.username == decrypted_data[3]:
                        tgt_client = client

                tgt_client.e2e_accepted_requests[current_client.username] = "REJECT"

                data = gen_IV(64)
                data += "\n" + "STATUS"
                data += "\n" + "REQUEST REJECTED"

                msg_key = util.hex2ba(sha_one_process(data)).to01()

                tmp_key, tmp_iv = self.kdf_2(current_client.auth_key, msg_key)

                response.msg_key = msg_key
                # Формируем зашифрованное сообщение
                response.encrypted_data = self.encrypt_msg(data, tmp_key, tmp_iv)

                return response

        elif msg_type == 5:
            # Передать параметры от клиента к клиенту
            # 1. tgt_username, 2. ID_session 3. g_b 4. Sha(SK)
            payload = decrypted_data[3] + "\n" + decrypted_data[4] + "\n" + decrypted_data[5]

            for client in self.clients:
                    if client.username == decrypted_data[2]:
                        tgt_client = client

            # Сохраняем то, что передал клиент
            tgt_client.e2e_passed_parameters[current_client.username] = payload

            # Формируем ответ
            response = chat.msg_client_server()
            response.auth_key_id = client.auth_key_hash[:64]

            data = gen_IV(64)
            data += "\n" + "STATUS"
            data += "\n" + "OK" 

            msg_key = util.hex2ba(sha_one_process(data)).to01()

            tmp_key, tmp_iv = self.kdf_2(current_client.auth_key, msg_key)

            response.msg_key = msg_key
            # Формируем зашифрованное сообщение
            response.encrypted_data = self.encrypt_msg(data, tmp_key, tmp_iv)

            return response 

        elif msg_type == 6:
            # Проверяем, есть ли переданые параметры от клиентов
            
            if len(current_client.e2e_accepted_requests) > 0:
                last_accepted_client = current_client.e2e_accepted_requests.keys()[-1]

                data = gen_IV(64)
                data += "\n" + current_client.e2e_accepted_requests[last_accepted_client]

                # Формируем ответ
                response = chat.msg_client_server()
                response.auth_key_id = client.auth_key_hash[:64]

                msg_key = util.hex2ba(sha_one_process(data)).to01()

                tmp_key, tmp_iv = self.kdf_2(current_client.auth_key, msg_key)

                response.msg_key = msg_key
                # Формируем зашифрованное сообщение
                response.encrypted_data = self.encrypt_msg(data, tmp_key, tmp_iv)

                return response 

            else:
                 # Формируем ответ
                response = chat.msg_client_server()
                response.auth_key_id = client.auth_key_hash[:64]

                data = gen_IV(64)
                data += "\n" + "STATUS"
                data += "\n" + "OK" 

                msg_key = util.hex2ba(sha_one_process(data)).to01()

                tmp_key, tmp_iv = self.kdf_2(current_client.auth_key, msg_key)

                response.msg_key = msg_key
                # Формируем зашифрованное сообщение
                response.encrypted_data = self.encrypt_msg(data, tmp_key, tmp_iv)

            return response 
        
    def SendMessageE2E(self, request, context):
        return super().SendMessageE2E(request, context)

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
    # port = 8080  # a random port for the server to run on
    # # the workers is like the amount of threads that can be opened at the same time, when there are 10 clients connected
    # # then no more clients able to connect to the server.
    # server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
    # rpc.add_ChatServerServicer_to_server(ChatServer(), server)  # register the server to gRPC
    # # gRPC basically manages all the threading and server responding logic, which is perfect!
    # print('Starting server. Listening...')
    # server.add_insecure_port('[::]:' + str(port))
    # server.start()
    # # Server starts in background (in another thread) so keep waiting
    # # if we don't wait here the main thread will end, which will end all the child threads, and thus the threads
    # # from the server won't continue to work and stop the server
    # try:
    #     while True:
    #         time.sleep(64 * 64 * 100)
    # except (KeyboardInterrupt, SystemExit):
    #     server.stop()
        
