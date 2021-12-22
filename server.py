import sys, time
import server_ui as ui
import socket
from threading import Thread
from socketserver import ThreadingMixIn

from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork

conn=None

sessions = []

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.server = self.make_server()

    
    # тут описываем действия окна сервера

    def btn_init(self):
        self.ui.btn_clear_log_box.clicked.connect(self.clear_log_box)
        self.ui.btn_reset_sessions.clicked.connect(self.reset_sessions)
        self.ui.btn_start_recevieng_msg.connect(self.start_recv)
        self.ui.btn_stop_recevieng_msg.connect(self.stop_recv)

    def clear_log_box(self):
        self.ui.log_box.clear()

    def reset_sessions(self):
        for session in sessions:
            session.close()

    def start_recv(self):
        pass

    def stop_recv(self):
        pass
    
    def make_server(self):
        server = Server(self)
        return server

    def log_event(self, text):
        self.ui.log_box.append(text)

    # def send(self):
    #     print("+++")

class Server(QtNetwork.QTcpServer):
    def __init__(self, parent=None):
        QtNetwork.QTcpServer.__init__(self, parent)
        self.socket = QtNetwork.QTcpSocket(self)

    def incomingConnection(self, socketDescriptor):
        self.socket.setSocketDescriptor(socketDescriptor)
        print("socket descriptor set up")

class ServerThread(Thread):
    def __init__(self,window):
        Thread.__init__(self)
        self.window = window


    def __del__(self):
        self.tcpServer.shutdown()
        self.tcpServer.close()
        self.close()

    def run(self):
        TCP_IP = '127.0.0.1'
        TCP_PORT = 8080
        BUFFER_SIZE = 20
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpServer.bind((TCP_IP, TCP_PORT))
        threads = []

        self.tcpServer.listen(1)
        while True:
            # try:
            print("Multithreaded Python server : Waiting for connections from TCP clients...") 
            global conn
            (conn, (ip,port)) = self.tcpServer.accept() 
            newthread = ClientThread(ip,port,self.window) 
            newthread.start() 
            threads.append(newthread)
        # else:
        #     self.tcpServer.shutdown(socket.SHUT_RDWR)
        #     self.tcpServer.close()
            # except KeyboardInterrupt:
            #     
            #     

            for t in threads:
                t.join()

class ClientThread(Thread):

    def __init__(self,ip,port,window):
        Thread.__init__(self)
        self.window = window
        self.ip = ip
        self.port = port
        print("[+] New server socket thread started for " + ip + ":" + str(port))
        self.window.log_event("[+] New server socket thread started for " + ip + ":" + str(port))

    # def __del__(self):

    #     self.close()

    def run(self):
        while True:
            global conn
            try:
                data = conn.recv(2048)
                self.window.log_box.setText("get")
                print(data)
            except KeyboardInterrupt:
                conn.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    server_thread = ServerThread(window)
    server_thread.start()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()

