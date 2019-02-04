# coding: utf8
import sys # solo para la linea de abajo
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
import queue  # cola de mensajes
from Mensaje import Mensaje
import requests

# Implementacion de un nodo de la red
class Nodo(object):
    # constructor
    def __init__(self, nid, nurl, nport):
        self.nombre = nid         # codigo del nodo, es un numero que sirve como id, debe ser unico para cada nodo
        self.url = nurl
        self.port = nport
        self.peers = []           # lista de peers (osea sockets encapsulados). un peer fijo es uno al que debe reconectarse
        self.msgs = []
        self._msg = queue.Queue() # cola de mensajes para procesar
        self._old = []            # historico de mensajes recibidos.
        
           
    # revisa si un mensaje ya habia llegado antes
    def _mensaje_existe(self, ms):
        for m in self._old:
            if m == ms.id:
                return True
        return False


    # logica para transmitir un mensaje a otro nodo
    def _enviar_otro_nodo(self, nd, js):
        try:
            requests.get('http://{}:{}/servidor/enviar/{}/{}'.format(nd[1], nd[2], self.nombre, js))
        except Exception as e:
            pass


    # envia un mensaje a todos los peers menos al que entrego el mensaje
    def _repartir_mensaje(self, ms):
        c = 0 # contador de peer al que se envia un mensaje
        for p in self.peers:
            if p[0] != ms.entregado_por: # no envia al peer que lo entrego
                self._enviar_otro_nodo(p, ms.to_json())
                c += 1
        return (c > 0) # si almenos se envio a un peer


    # envia un mensaje a la red
    def agregar_mensaje(self, destino, texto):
        ms = Mensaje(ndestino=destino, norigen=self.nombre, ncontenido=texto)
        ms.set_id(self.nombre) # crea un id unico para el mensaje
        self._msg.put(ms) # lo agrega a la cola de mensajes

        print("Cliente Envia Mensaje:", ms.id)
        return ms.id

    # funcion retornar mensajes en mailbox
    def ver_mensajes(self):
        res = []
        for i in self.msgs:
            res.append((i.id, i.origen, i.contenido))
        return res

    # borra todos los mensajes del mailbox
    def borrar_mensajes(self):
        self.msgs = []

    # agregar datos de un nodo
    def nodo_registrar(self, id, nurl, nport):
        print("Nodo Registrado:", id, nurl, nport)
        self.peers.append((id, nurl, nport))
        return True

    # cuando un nodo nos trasmite un mensaje
    def nodo_mensaje(self, nodo, contenido):
        try:
            ms = Mensaje.create_from_json(contenido, nodo)
            self._msg.put(ms) # lo agrega a la cola de mensajes
            return True
        except:
            return False

    # crear vinculo con un nodo
    def nodo_irsaludar(self, url, puerto):
        print("Nodo Crea Vinculo", url, puerto)
        try:
            r = requests.get('http://{}:{}/servidor/saludar/{}/{}/{}'.format(url, puerto, self.nombre, self.url, self.port))
            r.connection.close()
            if r.status_code == 200:
                res = r.json()
                self.nodo_registrar(res["nodo"], url, puerto)
        except Exception as e:
            pass
        

    # funcion principal del nodo, es la que realiza toda la magia
    def procesar(self):
        # procesamos los mensajes recibidos
        while self._msg.qsize() > 0: # si hay algun mensaje por procesar
            ms = self._msg.get() # obtenemos un mensaje de la cola
            if self._mensaje_existe(ms): # revisamos si ya habia llegado
                print("Mensaje Repetido: ", ms.id, " - Entregado:", ms.entregado_por) # mensaje repetido. el mensaje muere aqui.
            else:
                # el mensaje es nuevo
                self._old.append(ms.id) # agregamos al historico de mensajes
                if ms.destino == self.nombre: # revisamos si es para este nodo
                    self.msgs.append(ms)
                    print("Mensaje Mailbox: ", ms.id, " - Entregado:", ms.entregado_por) # somos el destinatario
                elif self._repartir_mensaje(ms): # se envia el mensaje a los peers
                    # si se logra enviar almenos a uno peer
                    if ms.origen == self.nombre: # revisamos si es un mensaje que creamos
                        print("Mensaje Transmitido: ", ms.id) # mensaje nuestro
                    else:
                        print("Mensaje Re-Transmitido: ", ms.id, " - Entregado:", ms.entregado_por) # mensaje de otro nodo
                else:
                    print("Mensaje Perdido: ", ms.id, " - Entregado:", ms.entregado_por) # no hay mas peers a quien enviarlo. el mensaje muere aqui.
