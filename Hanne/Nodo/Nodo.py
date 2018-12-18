# coding: utf8
import sys # solo para la linea de abajo
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
import socket
import select # usar funcion select
import queue  # cola de mensajes
from Peer import Peer
from Mensaje import Mensaje

# Implementacion de un nodo de la red
class Nodo(object):
    # constructor
    def __init__(self, nnombre, npuerto, nlinks):
        self.nombre = nnombre     # nombre del nodo, es un numero que sirve como id, debe ser unico para cada nodo
        self.puerto = npuerto     # puerto por donde recibe las conexiones entrantes. parte servidor
        self.server = None        # socket para modo servidor
        self.peers = []           # lista de peers (osea sockets encapsulados). un peer fijo es uno al que debe reconectarse
        self._msg = queue.Queue() # cola de mensajes para procesar
        self._old = []            # historico de mensajes recibidos.
        self.evento_error = None  # evento de reportar error. error(string)
        self.evento_log = None    # evento de nodo, reporta que ocurre con los mensajes procesados. log(int, int, string)
        self.evento_recibido = None # evento mensaje recibido, entrga el contenido de un mensaje que llego para el nodo. mensaje(int, int, string, int)
        # los puertos 'nlinks' se vuelven peers fijos
        for l in nlinks:
            tp = Peer()
            tp.puerto = l
            tp.es_fijo = True
            self.peers.append(tp)


    # permite lanzar el evento error
    def _onError(self, txt):
        if self.evento_error is not None:
            self.evento_error(txt)
    

    # permite lanzar el evento seguimiento
    def _onLog(self, msgid, peerid, tipo):
        if self.evento_log is not None:
            self.evento_log(msgid, peerid, tipo)


    # permite lanzar el evento entregar mensaje
    def _onMsg(self, msgid, origenid, contenido, peerid):
        if self.evento_recibido is not None:
            self.evento_recibido(msgid, origenid, contenido, peerid)


    # convierte un vector de socket en un vector con sus respectivos peers
    def _to_Peer(self, v):
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


    # crea un vector con los sockets activos y el socket servidor (esto para la funcion select)
    def _to_Vector(self):
        res = [self.server]  # agrega el socket servidor
        for p in self.peers: # recorre los peers y agrega el socket. si el peer no esta conectado lo ignora
            if p.socket is not None:
                res.append(p.socket)
        return res


    # revisa si un mensaje ya habia llegado antes
    def _mensaje_existe(self, ms):
        for m in self._old:
            if m == ms.id:
                return True
        return False


    # envia un mensaje a todos los peers menos al que entrego el mensaje
    def _repartir_mensaje(self, ms):
        c = 0 # contador de peer al que se envia un mensaje
        for p in self.peers:
            if p.nombre != ms.entregado_por: # no envia al peer que lo entrego
                p.enviar(ms.to_json())
                c += 1
        return (c > 0) # si almenos se envio a un peer


    # envia un mensaje a la red
    def agregar_mensaje(self, destino, texto):
        ms = Mensaje(ndestino=destino, norigen=self.nombre, ncontenido=texto)
        ms.set_id(self.nombre) # crea un id unico para el mensaje
        self._msg.put(ms) # lo agrega a la cola de mensajes


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


    # funcion principal del nodo, es la que realiza toda la magia
    def procesar(self):
        # Se reconectan los nodos originales (los que se entregaron como parametros)
        for i in self.peers:
            if (i.es_fijo) and (i.socket == None):
                i.conectar(self.nombre)

        # revisamos que nodos enviaron algo, o generaron error (se cerraron)
        inp = self._to_Vector();
        rr, rw, er = select.select(inp, [], inp, 0.25)  # reviso si alguno de los clientes escribio algo

        # revisar sockets que tienen errores
        if len(er) > 0: # si hay algun socket con error
            rw = self._to_Peer(er) # obtenemos los peers que generaron error
            for e in rw: # recorrer los peers
                if e is None: # error en el socket servidor
                    #print('Error en Servidor, Se detiene.')
                    self._onError('Error en Servidor, Se detiene.')
                else: # error en algun socket cliente
                    if not e.es_fijo: # los fijos no se borran de la lista
                        self.peers.remove(e)
                    #print('Error en Cliente ' + str(e.nombre)  + ', Se desconecta.')
                    self._onError('Error en Cliente ' + str(e.nombre)  + ', Se desconecta.')
                    e.desconectar()

        # revisar socket que enviaron datos
        if len(rr) > 0: # si hay algun socket envio datos
            rw = self._to_Peer(rr) # obtenemos los peers que generaron error
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
                        #print(' > [msg ' + ms.id + '] Cartero ' + str(s.nombre))
                        self._onLog(ms.id, s.nombre, 'recibido') # reporta que mensaje recibido

        # procesamos los mensajes recibidos
        while self._msg.qsize() > 0: # si hay algun mensaje por procesar
            ms = self._msg.get() # obtenemos un mensaje de la cola
            if self._mensaje_existe(ms): # revisamos si ya habia llegado
                #print(' > [msg ' + ms.id + '] Repetido')
                self._onLog(ms.id, ms.entregado_por, 'repetido') # mensaje repetido. el mensaje muere aqui.
            else:
                # el mensaje es nuevo
                self._old.append(ms.id) # agregamos al historico de mensajes
                if ms.destino == self.nombre: # revisamos si es para este nodo
                    #print(' > [msg ' + ms.id + '] De ' + str(ms.origen) + ', ' + ms.contenido)
                    self._onMsg(ms.id, ms.origen, ms.contenido, ms.entregado_por) # somos el destinatario
                elif self._repartir_mensaje(ms): # se envia el mensaje a los peers
                    # si se logra enviar almenos a uno peer
                    if ms.origen == self.nombre: # revisamos si es un mensaje que creamos
                        #print(' > [msg ' + ms.id + '] Enviado')
                        self._onLog(ms.id, ms.entregado_por, 'enviado') # mensaje nuestro
                    else:
                        #print(' > [msg ' + ms.id + '] Re-enviado')
                        self._onLog(ms.id, ms.entregado_por, 'reenviado') # mensaje de otro nodo
                else:
                    #print(' > [msg ' + ms.id + '] Fin Camino')
                    self._onLog(ms.id, ms.entregado_por, 'perdido') # no hay mas peers a quien enviarlo. el mensaje muere aqui.
