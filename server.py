from concurrent import futures

import server_ui as ui

import grpc
import time
import sys
import threading

import generated.chat_pb2 as chat
import generated.chat_pb2_grpc as rpc

from gamma import gen_key as gen_IV

from base_func import prime_gen_rm


from PyQt5 import QtCore, QtGui, QtWidgets

class ClientContext():
    def __init__(self) -> None:
        self.name = ""
        self.IV_128 = 0
        self.IV_256 = 0


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
        # self.server = self.make_server()
        threading.Thread(target=self.make_server, daemon=True).start()

    
    # тут описываем действия окна сервера

    def btn_init(self):
        self.ui.btn_clear_log_box.clicked.connect(self.clear_log_box)
        self.ui.btn_reset_sessions.clicked.connect(self.reset_sessions)
        self.ui.btn_start_recevieng_msg.connect(self.start_recv)
        self.ui.btn_stop_recevieng_msg.connect(self.stop_recv)

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

    # The stream which will be used to send new messages to clients
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

        new_client.IV_128 = request.nonce

        print(new_client.IV_128)
        print(type(new_client.IV_128))

        # Формируем ответ сервера
        server_response = chat.res_pq()

        # Устанавливаем nonce клиента
        server_response.nonce = request.nonce

        # Генерируем nonce сервера
        server_response.server_nonce = gen_IV(128)

        n = None

        while n == None:

            # Формируем параметры RSA -> p и q
            server_p = int(prime_gen_rm(32), 2)
            server_q = int(prime_gen_rm(32), 2)

            # Вычисляем N
            n =  server_p * server_q

            if n < 

        server_response.pq = str(n)

        server_response.pub_key_fingerprint = ""

        return server_response


        # Вырабатываются случайно параметры для пользователей

    # def Req_PQ(self, )

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
        
