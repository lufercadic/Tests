# coding: utf8
import socket

# Clase: Servidor eco 
class Servidor:
    # constructor
    def __init__(self, port):
        self.direccion = "127.0.0.1"
        self.puerto = port
        self.__so = None
        self.__stream = None

    # abre el puerto
    def escuchar(self):
        self.__so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__so.bind((self.direccion, self.puerto))
        self.__so.listen()

    # espera la conexion de un cliente, y obtiene el canal de comunicacion
    def atender(self):
        self.__stream, addr = self.__so.accept()

    # recibe lo que envia el cliente (no la use)
    def recibir(self):
        data = self.__stream.recv(1024)
        return data.decode("utf-8")

    # envia al cliente (no la use)
    def enviar(self, txt):
        self.__stream.sendall(txt.encode("utf-8"))

    # hace la funcion de recibir y responder
    def eco(self):
        data = self.__stream.recv(1024) # obtiene lo que envio el cliente
        if not data: return "" # si se termino la conexion del cliente
        else:
            txt = data.decode("utf-8")
            if txt == "bye": return None # si envio el comando de cerrar el servidor
            else:
                self.__stream.sendall(data) # enviar de regreso al cliente
                return txt

    # desconecta al cliente (libera el canal de com)
    def desconectar(self):
        if self.__stream != None:
            self.__stream.shutdown(socket.SHUT_RDWR) # No seguro de este
            self.__stream.close() # Cierra el socket conectado con el cliente
            self.__stream = None

    # cierra el servidor (libera el puerto)
    def salir(self):
        self.desconectar()
        self.__so.close()
        self.__so = None

    # procedimiento Main del programa
    def start(self):
        print("Iniciando Servidor")
        print("Puerto:", self.puerto)
        self.escuchar()
        print("Puerto abierto")
        # ciclo para atender varias veces
        repetir = True
        while repetir:
            print("")
            print("Esperando Cliente")
            self.atender()
            print("Cliente conectado")
            while True:
                msg = self.eco()
                if msg == None:
                    repetir = False
                    break
                elif msg == "":
                   break
                else:
                    print(" > ", msg)
            print('Desconectado')
            self.desconectar()
        print("Apagando Servidor")
        self.salir()

    # version inicial. todo en una sola funcion
    def start_old(self):
        print("Iniciando Servidor")
        so = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creo el socket para la conexion
        print("Puerto:", self.puerto)
        so.bind((self.direccion, self.puerto)) # enlaza el socket con el puerto a abrir
        so.listen() # inicia la escucha de clientes
        print("Puerto abierto")
        # ciclo de atencion al cliente
        repetir = True
        while repetir:
            print("")
            print("Esperando Cliente")
            stream, addr = so.accept() # espera la conexion de un cliente, entrega el canal de comunicacion
            print("Cliente conectado")
            while True:
                data = stream.recv(1024) # lee lo que envia el cliente
                if not data: break # cuando el cliente se desconecta llega vacio
                else:
                    print(" > ", data.decode("utf-8"))
                    if data.decode("utf-8") == "bye": repetir = False # uso la palabra bye para poder cerrar el server
                    else: stream.sendall(data) # se envia de regreso al cliente
            print('Salir')
            stream.shutdown(socket.SHUT_RDWR) # No seguro de este
            stream.close() # Cierra el socket conectado con el cliente
        so.close() # Cierra el socket del server



# ***************************************************************************************************************************
# Inicia el programa
if __name__ == "__main__":
    # Crea el objeto servidor y lo inicia
    Servidor(18001).start()