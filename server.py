from concurrent import futures

import server_ui as ui

import grpc
import time
import sys
import threading
from random import randint
from bitarray import util

import generated.chat_pb2 as chat
import generated.chat_pb2_grpc as rpc

from gamma import gen_key as gen_IV
from base_func import prime_gen_rm
from sha_one import sha_one_process
import gost
import rsa

from PyQt5 import QtCore, QtGui, QtWidgets


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

class ClientContext():
    """
    Структура содержащая информацию о подключаемых клиентах
    """
    def __init__(self) -> None:
        self.name = ""
        self.nonce = ""
        self.nonce_new = ""
        self.pq = ""
        self.p = ""
        self.q = ""
        self.server_nonce = ""
        self.server_rsa_priv_key = ""
        self.server_rsa_n_value = ""
        self.dh_pub_key = ""
        self.dh_priv_key = ""
        

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

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
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
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
        rpc.add_ChatServerServicer_to_server(ChatServer(), server)  # register the server to gRPC
        # gRPC basically manages all the threading and server responding logic, which is perfect!
        print('Starting server. Listening...')
        server.add_insecure_port('[::]:' + str(port))
        server.start()
        # Server starts in background (in another thread) so keep waiting
        # if we don't wait here the main thread will end, which will end all the child threads, and thus the threads
        # from the server won't continue to work and stop the server
        try:
            while True:
                time.sleep(64 * 64 * 100)
        except (KeyboardInterrupt, SystemExit):
            server.stop()

    def log_event(self, text):
        self.ui.log_box.append(text)

class ChatServer(rpc.ChatServerServicer):  # inheriting here from the protobuf rpc file which is generated

    def __init__(self):
        # List with all the chat history
        self.chats = []
        self.clients = []

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

    def SendNote(self, request: chat.Note, context):
        """
        This method is called when a clients sends a Note to the server.
        :param request:
        :param context:
        :return:
        """
        # this is only for the server console
        print("[{}] {}".format(request.name, request.message))
        # Add it to the chat history
        self.chats.append(request)
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

        # Опредляем индекс клиента запросившего параметры DH
        current_client_index = None

        for client in self.clients:
            if client.nonce == request.nonce and client.server_nonce == request.server_nonce:
                current_client_index = self.clients.index(client)

        decoded_data = rsa.decode(request.encrypted_data, self.clients[current_client_index].server_rsa_priv_key, self.clients[current_client_index].server_rsa_n_value)
        
        decoded_data = decoded_data.split("\n")

        

        response = chat.res_DH_params()


        pass

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
        
