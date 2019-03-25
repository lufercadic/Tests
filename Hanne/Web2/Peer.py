# coding: utf8
import sys # solo para la linea de abajo
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
from datetime import datetime
from Mensaje import Mensaje

# clase que representa un mensaje en la red
class Peer(object):
    # constructor
    def __init__(self, nid, nurl, nport, npass):
        self.idnodo = nid          # Identificador del nodo
        self.url = nurl            # Direccion nodo
        self.port = nport          # Puerto de escuha nodo
        self.password = npass      # Password de comunicacion
        self.public = True         # Si el nodo acepta conexiones
        self.last = datetime.now() # Fecha del ultimo acceso nodo
        self.box = []              # Cola de mensajes para entregar
        

    # asigna un id al mensaje, esto para diferenciarlo
    def setLast(self):
        self.last = datetime.now()


    # convierte la instancia en un texto json
    def to_json(self):
        js = dict(zip(["idnodo", "url", "port", "password", "public", "last", "box"],
                 [self.idnodo, self.url, self.port, self.password, self.public, self.last, self._box_to_json(self.box)]))
        return js
        

    # recupera los datos desde un texto json
    def from_json(self, js):
        self.idnodo = js["idnodo"]
        self.url = js["url"]
        self.port = js["port"]
        self.password = js["password"]
        self.public = js["public"]
        self.last = js["last"]
        self.box = _box_from_json(js["box"])

    def _box_from_json(self, b):
        l = []
        for e in b:
            l.append(Mensaje.create_from_json(e))
        return l

    def _box_to_json(self, b):
        l = []
        for e in b:
            l.append(e.to_json())
        return l

    