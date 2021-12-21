import sys, time
import server_ui as ui
import socket
from threading import Thread
from socketserver import ThreadingMixIn

from PyQt5 import QtCore, QtGui, QtWidgets

conn=None

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):

        super().__init__()
        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)
    
    # тут описываем действия окна сервера

    def send(self):
        print("+++")

class ServerThread(Thread):
    def __init__(self,window):
        Thread.__init__(self)
        self.window = window

    def run(self):
        TCP_IP = '127.0.0.1'
        TCP_PORT = 8080
        BUFFER_SIZE = 20
        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpServer.bind((TCP_IP, TCP_PORT))
        threads = []

        tcpServer.listen(4)
        while True:
            print("Multithreaded Python server : Waiting for connections from TCP clients...") 
            global conn
            (conn, (ip,port)) = tcpServer.accept() 
            newthread = ClientThread(ip,port,self.window) 
            newthread.start() 
            threads.append(newthread)

        for t in threads:
            t.join()

class ClientThread(Thread):

    def __init__(self,ip,port,window):
        Thread.__init__(self)
        self.window = window
        self.ip = ip
        self.port = port
        print("[+] New server socket thread started for " + ip + ":" + str(port))

    def run(self):
        while True:
            global conn

            data = conn.recv(2048)
            self.window.log_box.setText("get")
            print(data)



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    server_thread = ServerThread(window)
    server_thread.start()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

