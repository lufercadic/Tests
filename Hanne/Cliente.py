# coding: utf8
import socket

# Clase: cliente para servicio eco
class Cliente:
    # constructor
    def __init__(self, address, port):
        self.direccion = address
        self.puerto = port
        self.__so = None

    # inicia la conexion con el servidor
    def conectar(self):        
        self.__so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__so.connect((self.direccion, self.puerto))

    # envia un mensaje al servidor
    def enviar(self, msg):
        data = msg.encode("utf-8")
        self.__so.sendall(data)

    # recibe un mensaje desde el servidor
    def recibir(self):
        data = self.__so.recv(1024)
        return data.decode("utf-8")

    # envia el comando para que se detenga el servidor
    def apagar_server(self):
        self.enviar("bye")

    # desconecta al cliente
    def desconectar(self):
        self.__so.close()
        self.__so = None

    # procedimiento Main del programa
    def start(self):
        print("Conectando al servidor", self.direccion, ":", self.puerto)
        self.conectar()
        print("Conectado")
        print("Escribir '#1' para apagar el servidor")
        print("Escribir 'bye' para salir")
        while True:
            print("")
            txt = input("Enviar Texto: ")
            if txt == "#1":
                print("Apagando Servidor")
                self.apagar_server()
                break
            elif txt == "bye":
                break
            else:
                try:
                    self.enviar(txt)
                    print("Eco:", self.recibir())
                except socket.error: # no entiendo lo de este error. no sale error al enviar pero al leer sale un error. deberia entregar un timeout. no entiendo
                    print("Servidor fuera de servicio")
                    break
        self.desconectar()

    # version inicial. todo en una sola funcion
    def start_old(self):
        print("Conectando al servidor", self.direccion, ":", self.puerto)
        so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        so.connect((self.direccion, self.puerto))
        print("Conectado")
        print("Escribir '#1' para apagar el servidor")
        print("Escribir 'bye' para salir")
        while True:
            print("")
            txt = input("Enviar Texto: ")
            data = txt.encode("utf-8")
            if txt == "#1":
                print("Apagando Servidor")
                so.sendall(b'bye')
                break
            elif txt == "bye":
                break
            else:
                so.sendall(data)
                data = so.recv(1024)
                txt = data.decode("utf-8")
                print("Eco:", txt)
        so.close()
        so = None



# ***************************************************************************************************************************
# Inicia el programa
if __name__ == "__main__":
    # crea el objeto cliente y lo conecta
    Cliente("localhost", 18001).start()