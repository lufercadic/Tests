import socket
import threading
import sys
import pickle


class Servidor():
    """docstring for Servidor"""

    def __init__(self, host="localhost", port=4004):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((str(host), int(port)))
        self.sock.connect((str(host), int(4000)))

        msg_recv = threading.Thread(target=self.msg_recv)

        msg_recv.daemon = True

        self.sock.listen(10)
        self.sock.setblocking(False)
        msg_recv.start()







        self.clientes = []

        #self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.bind((str(host), int(port)))


        aceptar = threading.Thread(target=self.aceptarCon)
        procesar = threading.Thread(target=self.procesarCon)

        aceptar.daemon = True
        aceptar.start()

        procesar.daemon = True
        procesar.start()

        while True:
            msg = input('->')
            if msg != 'salir':
                self.send_msg(msg)
            else:
                self.sock.close()
                sys.exit()

    def msg_recv(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if data:
                    print(pickle.loads(data))
            except:
                pass

    def msg_to_all(self, msg, cliente):
        for c in self.clientes:
            try:
                if c != cliente:
                    c.send(msg)
            except:
                self.clientes.remove(c)

    def aceptarCon(self):
        print("aceptarCon iniciado")
        while True:
            try:
                conn, addr = self.sock.accept()
                conn.setblocking(False)
                self.clientes.append(conn)
            except:
                pass

    def procesarCon(self):
        print("ProcesarCon iniciado")
        while True:
            if len(self.clientes) > 0:
                for c in self.clientes:
                    try:
                        data = c.recv(1024)
                        if data:
                            self.msg_to_all(data, c)
                    except:
                        pass

    def send_msg(self, msg):
        self.sock.send(pickle.dumps(msg))


s = Servidor()