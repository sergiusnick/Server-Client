# Import
import sys
import time
import socket
import random
import threading
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QApplication, QMainWindow
from ClientUi import Ui_Client


class MainWindow(QMainWindow, Ui_Client):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.run = False
        self.name = None
        self.sock = None
        self.server = None

        self.SendButton.clicked.connect(self.sending)
        self.SelectRussian.clicked.connect(self.set_ru)
        self.SelectEnglish.clicked.connect(self.set_en)

        # Client
        self.connected = False
        self.JoinButton.clicked.connect(self.join)
        self.LeaveButton.clicked.connect(self.leave)
        self.RandomButton.clicked.connect(self.random)

        # Server
        self.rt = None
        self.shutdown = True
        self.clients = {}
        self.number = 1

        self.StartButton.clicked.connect(self.start)
        self.StopButton.clicked.connect(self.stop)
        self.sMinusButton.clicked.connect(self.minus)
        self.sPlusButton.clicked.connect(self.plus)

        self.key = {'[Si]': '[SERVER IS FULL]',
                    '[Ji]': 'JOINS THE SERVER'}

    def set_ru(self):
        try:
            self.ru_translate_ui()
        except Exception as RuTranslateError:
            self.Display.append('<--RuTranslateError-->')
            self.Display.append(str(RuTranslateError))

    def set_en(self):
        try:
            self.en_translate_ui()
        except Exception as EnTranslateError:
            self.Display.append('<--EnTranslateError-->')
            self.Display.append(str(EnTranslateError))

    def sending(self):
        if self.run:
            # Client Sending
            if self.shutdown:
                try:
                    message = self.SendLine.text()
                    self.Display.append('[' + self.name + '] :: ' + self.SendLine.text())
                    self.SendLine.setText('')
                    self.sock.sendto(message.encode("utf-8"), self.server)
                except Exception as ClientSendingError:
                    self.Display.append('<--ClientSendingError-->')
                    self.Display.append(str(ClientSendingError))

            # Host Sending
            if not self.shutdown:
                try:
                    message = self.name + 'セート' + self.SendLine.text()
                    self.Display.append('[' + self.name + '] :: ' + self.SendLine.text())
                    self.SendLine.setText('')
                    for client in self.clients:
                        self.sock.sendto(message.encode("utf-8"), client)
                except Exception as ServerSendingError:
                    self.Display.append('<--ServerSendingError-->')
                    self.Display.append(str(ServerSendingError))
        else:
            self.Display.append('<-<-<You are not on the server>->->')

    # Client
    def receiving(self):
        while self.connected:
            try:
                data, addr = self.sock.recvfrom(1024)
                if 'セート' in data.decode("utf-8"):
                    name, mess = data.decode("utf-8").split('セート')
                    message = '[' + name + '] :: ' + mess
                    self.Display.append(message)
                else:
                    if '[SERVER IS FULL]' in data.decode("utf-8") or \
                            '[SERVER STOPPED]' in data.decode("utf-8"):
                        self.leave()
                    self.Display.append(data.decode("utf-8"))
            except Exception as ClientReceivingError:
                if ClientReceivingError:
                    pass
            time.sleep(0.2)

    def join(self):
        if not self.connected:
            self.run = True
            # Sock open
            try:
                ip = socket.gethostbyname(socket.gethostname())
                port = int(self.cLocalPort.text())
                self.name = self.cName.text()
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.bind((ip, port))
                self.sock.setblocking(False)
            except Exception as ClientSockError:
                self.run = False
                self.Display.append('<--ClientSockError-->')
                self.Display.append(str(ClientSockError))

            # Set Server
            try:
                self.server = (self.cIPv4.text(), int(self.cPort.text()))
            except Exception as ClientServerError:
                self.run = False
                self.Display.append('<--ClientServerError-->')
                self.Display.append(str(ClientServerError))

            # Start receiving
            try:
                self.connected = True
                self.rt = threading.Thread(target=ex.receiving)
                self.rt.start()
            except Exception as ClientStartReceivingError:
                self.run = False
                self.Display.append('<--ClientStartReceivingError-->')
                self.Display.append(str(ClientStartReceivingError))

            # Connecting to server
            try:
                self.sock.sendto(self.name.encode("utf-8"), self.server)
            except Exception as ClientConnectionError:
                self.run = False
                self.Display.append('<--ClientConnectionError-->')
                self.Display.append(str(ClientConnectionError))

    def leave(self):
        self.run = False
        if self.connected:
            try:
                self.sock.sendto('セート'.encode("utf-8"), self.server)
                self.sock.close()
                self.connected = False
                self.random()
            except Exception as ClientLeaveError:
                self.run = True
                self.Display.append('<--ClientLeaveError-->')
                self.Display.append(str(ClientLeaveError))

    def random(self):
        self.cLocalPort.setText("{}".format(random.randint(10000, 30000)))

    # Server
    def turn_on_server(self):
        self.Display.append('<-<-<SERVER STARTED>->->')
        while not self.shutdown:
            try:
                data, addr = self.sock.recvfrom(1024)
                if 'セート' in data.decode("utf-8"):
                    message = '[' + self.clients[addr] + '] :: ' + '[LEFT THE SERVER]'
                    self.Display.append(message)
                    for client in self.clients:
                        if addr != client:
                            self.sock.sendto(message.encode("utf-8"), client)
                    self.clients.pop(addr)

                elif addr not in self.clients:
                    if len(self.clients) < self.number:
                        self.clients[addr] = data.decode("utf-8")

                        message = '[' + data.decode("utf-8") + '] :: ' + '[Ji]'
                        self.sock.sendto('[You have joined the server]'.encode("utf-8"), addr)

                        self.message((data, addr), '[JOINS THE SERVER]')
                    else:
                        self.sock.sendto(self.key['Si'].encode("utf-8"), addr)
                else:
                    message = '[' + self.clients[addr] + '] :: ' + data.decode("utf-8")
                    self.Display.append(message)

                    message = self.clients[addr] + 'セート' + data.decode("utf-8")
                    for client in self.clients:
                        if addr != client:
                            self.sock.sendto(message.encode("utf-8"), client)

            except Exception as ServerError:
                if ServerError:
                    pass
        self.Display.append('<-<-<SERVER STOPPED>->->')

    def message(self, sell, *args):
        data, addr = sell
        if args:
            k = self.key[args[0]]
            message = '[{}] :: '.format(self.clients[addr]) + k + '//[INFO]'
            for client in self.clients:
                if addr != client:
                    self.sock.sendto(message.encode("utf-8"), client)
        else:
            message = '[{}] :: '.format(self.clients[addr]) + data.decode("utf-8") + '//[PASS]'
            for client in self.clients:
                if addr != client:
                    self.sock.sendto(message.encode("utf-8"), client)

    def start(self):
        self.run = True
        if self.shutdown:
            try:
                self.name = self.sName.text()
                host = self.sIPv4.text()
                port = int(self.sPort.text())
                self.shutdown = False
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.bind((host, port))
                self.rt = threading.Thread(target=ex.turn_on_server)
                self.rt.start()
            except Exception as ServerStartError:
                self.run = False
                self.Display.append('<--ServerStartError-->')
                self.Display.append(str(ServerStartError))

    def stop(self):
        self.run = False
        if not self.shutdown:
            try:
                message = '[SERVER STOPPED]'
                for client in self.clients:
                    self.sock.sendto(message.encode("utf-8"), client)
                self.shutdown = True
                self.sock.close()
                self.rt.join()
            except Exception as ServerStopError:
                self.run = True
                self.Display.append('<--ServerStopError-->')
                self.Display.append(str(ServerStopError))

    def minus(self):
        if self.number > 1:
            self.number -= 1
            self.sNumber.setProperty("intValue", self.number)

    def plus(self):
        if self.number < 10:
            self.number += 1
            self.sNumber.setProperty("intValue", self.number)


app = QApplication(sys.argv)
ex = MainWindow()
ex.show()
sys.exit(app.exec_())
