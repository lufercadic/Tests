# coding: utf8
import sys
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
import socket
import select
import queue
import threading
import time
from Peer import Peer
from Mensaje import Mensaje

# Implementacion de un nodo de la red
class Nodo(object):
    def __init__(self, nnombre, npuerto, nlinks):
        self.nombre = nnombre
        self.puerto = npuerto
        self.server = None
        self.peers = []
        self._msg = queue.Queue()
        self._old = []

        for l in nlinks:
            tp = Peer()
            tp.puerto = l
            tp.es_fijo = True
            self.peers.append(tp)
       
    # de un vector de socket, retorna un vector con sus respectivos peers
    def __to_Peer(self, v):
        res = []
        for i in v:
            if i is self.server:
                res.append(None)
                continue
            for p in self.peers:
                if i is p.socket:
                    res.append(p)
                    break
        return res

    # crea un vector con los sockets activos y el socket servidor
    def __to_Vector(self):
        res = [self.server]
        for p in self.peers:
            if p.socket is not None:
                res.append(p.socket)
        return res

    # revisa si un mensaje ya habia llegado antes
    def _mensaje_existe(self, ms):
        for m in self._old:
            if m.id == ms.id:
                return True
        return False

    # envia un mensaje a todos los peers menos al que entrego el mensaje
    def _repartir_mensaje(self, ms):
        c = 0
        for p in self.peers:
            if p.nombre != ms.entregado_por:
                p.enviar(ms.to_json())
                c += 1
        return (c > 0)

    # inicia el servidor
    def escuchar(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', self.puerto))
        self.server.listen(5)

    # desconecta todos los sockets
    def detener(self):
        self.server.close()
        self.server = None        
        self._msg = None
        self._old = None
        for p in self.peers:
            p.desconectar()
        self.peers = None

    def procesar(self):
        # Se reconectan los nodos originales (los que se entregaron como parametros)
        for i in self.peers:
            if (i.es_fijo) and (i.socket == None):
                i.conectar(self.nombre)

        # revisamos que nodos enviaron algo, o generaron error (se cerraron)
        inp = self.__to_Vector();
        rr, rw, er = select.select(inp, [], inp, 0.5)  # reviso si alguno de los clientes escribio algo

        # revisar sockets que tienen errores
        if len(er) > 0: # si hay algun socket con error
            rw = self.__to_Peer(er) # obtenemos los peers que generaron error
            for e in rw: # recorrer los peers
                if e is None: # error en el socket servidor
                    print('Error en Servidor, Se detiene.')
                else: # error en algun socket cliente
                    if not e.es_fijo: # los fijos no se borran de la lista
                        self.peers.remove(e)
                    print('Error en Cliente ' + str(e.nombre)  + ', Se desconecta.')
                    e.desconectar()

        # revisar socket que enviaron datos
        if len(rr) > 0: # si hay algun socket envio datos
            rw = self.__to_Peer(rr) # obtenemos los peers que generaron error
            for s in rw: # recorrer los peers
                if s is None: # nuevo cliente conectado
                    stream, addr = self.server.accept()
                    addr = Peer.create_from_socket(stream, self.nombre) # se hace el protocolo de conexion
                    self.peers.append(addr) # se agrega a los peers
                else: # es un peer que envio datos
                    ms = s.recibir()
                    if ms is not None:
                        ms = Mensaje.create_from_json(ms, s.nombre)
                        self._msg.put(ms) # se lee el mensaje y se agrega a la cola
                        print(' > [msg ' + ms.id + '] Cartero ' + str(s.nombre))

        # procesamos los mensajes recibidos
        while self._msg.qsize() > 0:
            ms = self._msg.get()
            if self._mensaje_existe(ms):
                print(' > [msg ' + ms.id + '] Repetido')
            else:
                self._old.append(ms)
                if ms.destino == self.nombre:
                    print(' > [msg ' + ms.id + '] De ' + str(ms.origen) + ', ' + ms.contenido)
                elif self._repartir_mensaje(ms):
                    if ms.origen == self.nombre:
                        print(' > [msg ' + ms.id + '] Enviado')
                    else:
                        print(' > [msg ' + ms.id + '] Re-enviado')
                else:
                    print(' > [msg ' + ms.id + '] Fin Camino')

    # envia un mensaje a la red
    def agregar_mensaje(self, destino, texto):
        ms = Mensaje(ndestino=destino, norigen=self.nombre, ncontenido=texto)
        ms.set_id(self.nombre)
        self._msg.put(ms)


h_continuar = True
h_mensaje = None
def teclado():
    global h_continuar
    global h_mensaje

    while h_continuar:
        txt = input()
        if txt == '#1':
            h_continuar = False
        else:
            txt = txt.split(" ", 1)
            try: 
                txt[0] = int(txt[0])
                h_mensaje = (txt[0], txt[1])
            except ValueError:
                pass

# ============================== MAIN ==================================
def main():
    global h_continuar
    global h_mensaje

    cod = int(sys.argv[1])
    n = None

    if cod == 201:
        n = Nodo(1, 18001, [])
    elif cod == 202:
        n = Nodo(2, 18002, [18001])

    elif cod == 301:
        n = Nodo(1, 18001, [])
    elif cod == 302:
        n = Nodo(2, 18002, [18001, 18003])
    elif cod == 303:
        n = Nodo(3, 18003, [])

    else:
        return # si no es valido


    print('Nodo ' + str(n.nombre) + ' - ' + str(n.puerto))
    time.sleep(5) # un tiempo para iniciar todos los nodos
    n.escuchar()
    print('Escuchando')
    print('Escribir #1 para salir')

    # iniciar escucha del teclado
    hilo = threading.Thread(target=teclado, name='teclado', daemon=True)
    hilo.start()

    # ciclo de trabajo nodo
    while h_continuar:
        # revisamos si hay mensaje para enviar
        if h_mensaje is not None:
            n.agregar_mensaje(h_mensaje[0], h_mensaje[1])
            h_mensaje = None
        # procesamos el nodo
        n.procesar()
        time.sleep(0.25)   

    # fin
    n.detener()
    print('bye bye.')


# llamado al Main
main()

#import threading
#threadLock = threading.Lock()
#with threadLock:
#    global_counter += 1

#[Manejo de sincronizacion]
#http://effbot.org/zone/thread-synchronization.htm

#[Modos de controlar el input sin bloquear]
#https://stackoverflow.com/questions/5404068/how-to-read-keyboard-input
#https://stackoverflow.com/questions/2408560/python-nonblocking-console-input

#[Convertir entero a bytes y viceversa]
#https://docs.python.org/3/library/stdtypes.html#int.to_bytes

#[Convertir a Json]
#https://docs.python.org/3.4/library/json.html#module-json

#[Serializacion]
#https://docs.python.org/3.4/library/pickle.html
