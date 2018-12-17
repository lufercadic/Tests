# coding: utf8
import socket

# Clase para contener los socket activos y permitir la comunicacion
class Peer(object):
    # constructor
    def __init__(self):
        self.es_fijo = False # si es un peer fijo. es decir debe reconectarse
        self.socket = None   # socket de comunicacion con el peer
        self.puerto = 0      # puerto para la comunicacion. es solo para los fijos
        self.nombre = 0      # codigo del peer. esto lo envia al iniciar la comunicacion

    # procedimiento de la clase, pensado para los peers que se conectan. osea los no fijos
    @classmethod
    def create_from_socket(cls, socket, nombre):
        nu = Peer()
        nu.socket = socket
        nu.enviar(str(nombre))        # envia el nombre del nodo actual
        nu.nombre = int(nu.recibir()) # recibe el nombre del nodo con el que se conecto
        return nu
        

    # Envia un texto por el socket
    def enviar(self, msg):
        v = msg.encode("utf-8")                  # el texto lo convierte a un vector de bytes
        vl = len(v).to_bytes(2, byteorder='big') # obtiene un vector de 2 bytes de la longitud de la cadena
        v = vl + v                               # concatena los dos vectores
        self.socket.sendall(v)                   # envia por el socket


    # procedimiento privado, recibir una cantidad especifica de bytes
    def __recibir(self, num):
        buff = b''
        nb = 0
        din = None
        while len(buff) < num:         # repetir mientras falte leer algun byte
            if num - len(buff) > 1024: # evitamos que la lectura sea muy grande
                nb = 1024              # numero maximo a leer del buffer
            else:
                nb = num - len(buff)   # numero de bytes restantes
            din = self.socket.recv(nb) # se hace la siguiente lectura del socket
            # si llega vacio es que se corto la com, hacer esa evaluacion
            if len(din) < 1:
                break
            #if len(din) > 0:           # confirmamos que se leyo algo
            else:
                buff = buff + din      # concatenamos los bytes
        din = None
        return buff
    

    # recibir un texto desde el socket
    def recibir(self):
        din = self.__recibir(2)                        # lee la cabecera, 2 bytes indican el tamaño del envio
        if len(din) > 0:
            lg = int.from_bytes(din[0:2], byteorder='big') # numero de bytes a recibir
            din = self.__recibir(lg)                       # recibe el contenido completo
            return din.decode("utf-8")                     # se vuelve una cadena de texto
        else:
            return None


    # permite conectar vinculo de tipo fijo
    def conectar(self, nombre):
        if self.es_fijo:
            try:
                # se inicia la conexion
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect(('localhost', self.puerto))
                # se envia el nombre del nodo
                self.enviar(str(nombre))
                # se obtiene el nombre del nodo con el que se conecto
                self.nombre = int(self.recibir())
            except socket.error:
                self.socket = None
                self.nombre = 0


    # desconectar el nodo
    def desconectar(self):
        try:
            #self.socket.shutdown(socket.SHUT_RDWR) # sigo sin saber si es necesario
            self.socket.close()
            self.socket = None
            self.nombre = 0
        except:
            self.socket = None
            self.nombre = 0