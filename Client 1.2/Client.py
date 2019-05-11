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

        self.log = [time.asctime() + ' PyChat start']

        self.SendButton.clicked.connect(self.sending)
        self.SelectRussian.clicked.connect(self.set_ru)
        self.SelectEnglish.clicked.connect(self.set_en)
        self.SaveButton.clicked.connect(self.save)

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
                    '[Ji]': '[JOINS THE SERVER]',
                    '[Le]': '[LEFT THE SERVER1]',
                    '[Ss]': '[SERVER STOPPED]'}

    def set_ru(self):
        try:
            self.ru_translate_ui()
        except Exception as RuTranslateError:
            self.log.append('\n[{}]'.format(time.asctime()) + ' ' + str(RuTranslateError))
            self.Display.append('<--RuTranslateError-->')
            self.Display.append(str(RuTranslateError))

    def set_en(self):
        try:
            self.en_translate_ui()
        except Exception as EnTranslateError:
            self.log.append('\n[{}]'.format(time.asctime()) + ' ' + str(EnTranslateError))
            self.Display.append('<--EnTranslateError-->')
            self.Display.append(str(EnTranslateError))

    def sending(self):
        if self.run:
            # Client Sending
            if self.shutdown:
                try:
                    message = self.SendLine.text()
                    self.Display.append(f'[{self.name}] :: {self.SendLine.text()}')
                    self.sock.sendto(f'{message}//[PASS]'.encode("utf-8"), self.server)
                    self.SendLine.setText('')
                except Exception as ClientSendingError:
                    self.log.append(f'\n[{time.asctime()}] {ClientSendingError}')
                    self.Display.append('<--ClientSendingError-->')
                    self.Display.append(str(ClientSendingError))

            # Host Sending
            if not self.shutdown:
                try:
                    message = f'[{self.name}] :: {self.SendLine.text()}//[PASS]'
                    display = '[' + self.name + '] :: ' + self.SendLine.text()
                    self.Display.append(display)
                    self.SendLine.setText('')
                    for client in self.clients:
                        self.sock.sendto(message.encode("utf-8"), client)
                except Exception as ServerSendingError:
                    self.log.append(f'\n[{time.asctime()}] {ServerSendingError}')
                    self.Display.append('<--ServerSendingError-->')
                    self.Display.append(str(ServerSendingError))
        else:
            self.Display.append('<-<-<You are not on the server>->->')

    def save(self):
        try:
            file = open('log.txt', 'w')
            for i in self.log:
                file.write(i)
            file.close()
        except Exception as SaveError:
            self.log.append(f'\n[{time.asctime()}] {SaveError}')
            self.Display.append('<--SaveError-->')
            self.Display.append(str(SaveError))

    # Client
    def receiving(self):
        while self.connected:
            try:
                data, addr = self.sock.recvfrom(1024)
                cell = data.decode("utf-8").split('//')
                if cell[-1] == '[FLAG]':
                    self.Display.append(cell[0])
                    self.leave()
                if cell[-1] == '[INFO]':
                    self.Display.append(cell[0])
                elif cell[-1] == '[PASS]':
                    self.Display.append(cell[0])
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
                self.log.append(f'\n[{time.asctime()}] {ClientSockError}')
                self.run = False
                self.Display.append('<--ClientSockError-->')
                self.Display.append(str(ClientSockError))

            # Set Server
            try:
                self.server = (self.cIPv4.text(), int(self.cPort.text()))
            except Exception as ClientServerError:
                self.log.append(f'\n[{time.asctime()}] {ClientServerError}')
                self.run = False
                self.Display.append('<--ClientServerError-->')
                self.Display.append(str(ClientServerError))

            # Start receiving
            try:
                self.connected = True
                self.rt = threading.Thread(target=ex.receiving)
                self.rt.start()
            except Exception as ClientStartReceivingError:
                self.log.append(f'\n[{time.asctime()}] {ClientStartReceivingError}')
                self.run = False
                self.Display.append('<--ClientStartReceivingError-->')
                self.Display.append(str(ClientStartReceivingError))

            # Connecting to server
            try:
                message = f'{self.name}//[NAME]'
                self.sock.sendto(message.encode("utf-8"), self.server)
            except Exception as ClientConnectionError:
                self.log.append(f'\n[{time.asctime()}] {ClientConnectionError}')
                self.run = False
                self.Display.append('<--ClientConnectionError-->')
                self.Display.append(str(ClientConnectionError))

    def leave(self):
        self.run = False
        if self.connected:
            try:
                self.sock.sendto('//[LEAVE]'.encode("utf-8"), self.server)
                self.sock.close()
                self.connected = False
                self.random()
                self.Display.append('[You left the server]')
            except Exception as ClientLeaveError:
                self.log.append(f'\n[{time.asctime()}] {ClientLeaveError}')
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
                cell = data.decode("utf-8").split('//')
                if cell[-1] == '[LEAVE]':
                    message = '[' + self.clients[addr] + '] :: ' + '[LEFT THE SERVER]'
                    self.Display.append(message)
                    self.message((data, addr), '[Le]')
                    self.clients.pop(addr)

                elif addr not in self.clients:
                    if len(self.clients) < self.number:
                        print(1)
                        self.clients[addr] = cell[0]
                        self.sock.sendto('[You have joined the server]//[PASS]'.encode("utf-8"), addr)
                        message = f'[{cell[0]}] :: {self.key["[Ji]"]}'
                        self.Display.append(message)
                        self.message((cell[0], addr), '[JOINS THE SERVER]')
                    else:
                        self.sock.sendto((self.key['Si'] + '//[FLAG]').encode("utf-8"), addr)
                else:
                    message = f'[{self.clients[addr]}] :: {cell[0]}'
                    self.Display.append(message)
                    self.message((data, addr))

            except Exception as ServerError:
                if ServerError:
                    pass
        self.Display.append('<-<-<SERVER STOPPED>->->')

    def message(self, cell, *args):
        if args and cell:
            data, addr = cell
            message = f'[{self.clients[addr]}] :: {self.key[args[0]]}//[INFO]'
            for client in self.clients:
                if addr != client:
                    self.sock.sendto(message.encode("utf-8"), client)
        elif cell and not args:
            data, addr = cell
            message = f'[{self.clients[addr]}] :: {data.decode("utf-8")}//[PASS]'
            for client in self.clients:
                if addr != client:
                    self.sock.sendto(message.encode("utf-8"), client)
        elif args and not cell:
            for client in self.clients:
                self.sock.sendto(f'{self.key[args[0]]}//[FLAG]'.encode("utf-8"), client)

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
                self.log.append(f'\n[{time.asctime()}] {ServerStartError}')
                self.run = False
                self.Display.append('<--ServerStartError-->')
                self.Display.append(str(ServerStartError))

    def stop(self):
        self.run = False
        if not self.shutdown:
            try:
                self.message(False, '[Ss]')
                self.shutdown = True
                self.clients = {}
                self.sock.close()
                self.rt.join()
            except Exception as ServerStopError:
                self.log.append(f'\n[{time.asctime()}] {ServerStopError}')
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
