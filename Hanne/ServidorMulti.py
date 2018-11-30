# coding: utf8
import socket
import select

# Clase: Servidor eco 
class ServidorMulti:
    # constructor
    def __init__(self, port):
        self.direccion = "127.0.0.1"
        self.puerto = port
        self.__so = None
        self.__inputs = []
        self.__continuar = True

    # abre el puerto
    def escuchar(self):
        self.__so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__so.bind((self.direccion, self.puerto))
        self.__so.listen()

    # espera la conexion de un cliente, y obtiene el canal de comunicacion
    def atender(self):
        stream, addr = self.__so.accept()
        self.__inputs.append(stream)

    # hace la funcion de recibir y responder
    def eco(self, s):
        data = s.recv(1024) # obtiene lo que envio el cliente
        if not data: return "" # si se termino la conexion del cliente
        else:
            txt = data.decode("utf-8")
            if txt == "bye": return None # si envio el comando de cerrar el servidor
            else:
                s.sendall(data) # enviar de regreso al cliente
                return txt

    # cierra el servidor (libera el puerto)
    def salir(self):
        self.__inputs.remove(self.__so)

        for s in self.__inputs:
            s.shutdown(socket.SHUT_RDWR)
            s.close()

        self.__inputs.clear()
        self.__so.close()
        self.__so = None

    # procedimiento Main del programa
    def start(self):
        print("Iniciando Servidor")
        print("Puerto:", self.puerto)
        self.escuchar()
        print("Puerto abierto")
        print("Esperando Clientes")
        print("")
        # ciclo para atender varias veces
        self.__continuar = True
        self.__inputs.append(self.__so)

        while self.__continuar:
            rr, rw, er = select.select(self.__inputs, [], self.__inputs, 1.0)  # reviso si alguno de los clientes escribio algo

            for e in er: # se procesan los sockets que tienen errores
                if c is self.__so: # error en el socket servidor
                    self.__continuar = False
                    print('Error en Servidor, Se detiene')
                else: # error en algun socket cliente
                    e.shutdown(socket.SHUT_RDWR)
                    e.close()
                    self.__inputs.remove(e)
                    print('Error en Cliente, Se desconecta')

            for c in rr:    # recorremos la lista de sockets que recibieron datos
                if c is self.__so:  # revisamos si es el socket servidor
                    print("Cliente Conectado")
                    self.atender()
                else:   # si es un socket cliente
                    msg = self.eco(c)
                    if msg == None: # se dio orden de apagar
                        self.__continuar = False
                        self.__inputs.remove(c)
                        c.shutdown(socket.SHUT_RDWR)
                        c.close()
                        print('Cliente Envio Orden Apagar')
                    elif msg == "": # el cliente se desconecto
                        self.__inputs.remove(c)
                        c.shutdown(socket.SHUT_RDWR)
                        c.close()
                        print('Cliente Desconectado')
                    else: # el cliente envio un texto
                        print(" > ", msg)

        print("Apagando Servidor")
        self.salir()



# ***************************************************************************************************************************
# Inicia el programa
if __name__ == "__main__":
    # Crea el objeto servidor y lo inicia
    ServidorMulti(18001).start()