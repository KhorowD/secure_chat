# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\server.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(839, 779)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.btn_reset_sessions = QtWidgets.QPushButton(self.centralwidget)
        self.btn_reset_sessions.setObjectName("btn_reset_sessions")
        self.gridLayout.addWidget(self.btn_reset_sessions, 3, 0, 1, 1)
        self.label_log_messages = QtWidgets.QLabel(self.centralwidget)
        self.label_log_messages.setObjectName("label_log_messages")
        self.gridLayout.addWidget(self.label_log_messages, 2, 0, 1, 1)
        self.label_admin_panel = QtWidgets.QLabel(self.centralwidget)
        self.label_admin_panel.setObjectName("label_admin_panel")
        self.gridLayout.addWidget(self.label_admin_panel, 0, 0, 1, 1)
        self.log_box = QtWidgets.QTextEdit(self.centralwidget)
        self.log_box.setReadOnly(True)
        self.log_box.setObjectName("log_box")
        self.gridLayout.addWidget(self.log_box, 1, 0, 1, 1)
        self.btn_start_recevieng_msg = QtWidgets.QPushButton(self.centralwidget)
        self.btn_start_recevieng_msg.setObjectName("btn_start_recevieng_msg")
        self.gridLayout.addWidget(self.btn_start_recevieng_msg, 5, 0, 1, 1)
        self.btn_clear_log_box = QtWidgets.QPushButton(self.centralwidget)
        self.btn_clear_log_box.setObjectName("btn_clear_log_box")
        self.gridLayout.addWidget(self.btn_clear_log_box, 4, 0, 1, 1)
        self.btn_stop_recevieng_msg = QtWidgets.QPushButton(self.centralwidget)
        self.btn_stop_recevieng_msg.setObjectName("btn_stop_recevieng_msg")
        self.gridLayout.addWidget(self.btn_stop_recevieng_msg, 6, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 839, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_reset_sessions.setText(_translate("MainWindow", "Reset all sessions"))
        self.label_log_messages.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">Log Messages</span></p></body></html>"))
        self.label_admin_panel.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:600;\">Admin Panel</span></p></body></html>"))
        self.btn_start_recevieng_msg.setText(_translate("MainWindow", "Start recevieng messages"))
        self.btn_clear_log_box.setText(_translate("MainWindow", "Clear log box"))
        self.btn_stop_recevieng_msg.setText(_translate("MainWindow", "Stop recevieng messages"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
