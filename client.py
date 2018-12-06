import socket, threading, time
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from ServerUi import Ui_MainWindow


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        host = socket.gethostbyname(socket.gethostname())
        port = 0

        self.server = ("192.168.1.219", 9090)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((host, port))
        self.s.setblocking(0)
        key = 8194
        # alias = input("Name: ")
        self.alias = '[eq'

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Enter - 1:
            self.textBrowser.append(self.lineEdit.text())
            try:
                message = self.lineEdit.text()
                if message != "":
                    self.s.sendto(("[" + self.alias + "] :: " + message).encode("utf-8"), self.server)
                time.sleep(0.2)
            except Exception as Er:
                self.textBrowser.append(str(Er))
            self.lineEdit.setText('')



app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())

shutdown = False
join = False

'''
def receving(name, sock):
    while not shutdown:
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                decrypt = "";
                k = False
                for i in data.decode("utf-8"):
                    if i == ":":
                        k = True
                        decrypt += i
                    elif k == False or i == " ":
                        decrypt += i
                    else:
                        decrypt += chr(ord(i) ^ key)
                ex.self.textBrowser.append(decrypt)
                # End
                time.sleep(0.2)
        except:
            pass

while shutdown == False:
    if join == False:
        s.sendto(("[" + alias + "] => join chat ").encode("utf-8"), server)
        join = True
    else:
        try:
            message = ex.keyPressEvent()

            # Begin
            crypt = ""
            for i in message:
                crypt += chr(ord(i) ^ key)
            message = crypt
            # End

            if message != "":
                s.sendto(("[" + alias + "] :: " + message).encode("utf-8"), server)

            time.sleep(0.2)
        except:
            s.sendto(("[" + alias + "] <= left chat ").encode("utf-8"), server)
            shutdown = True

rT.join()
s.close()
'''
