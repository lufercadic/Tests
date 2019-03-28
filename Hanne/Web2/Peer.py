# coding: utf8
import sys # solo para la linea de abajo
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
from datetime import datetime
from Mensaje import Mensaje
from Utiles import Utiles

# clase que representa un mensaje en la red
class Peer(object):
    # constructor
    def __init__(self, nid=None, nurl=None, nport=None, npass=None):
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
                 [self.idnodo, self.url, self.port, self.password, self.public, self.last.strftime("%Y-%m-%d %H:%M:%S"), self._box_to_json(self.box)]))
        return js
        

    # recupera los datos desde un texto json
    def from_json(self, js):
        self.idnodo = js["idnodo"]
        self.url = js["url"]
        self.port = js["port"]
        self.password = js["password"]
        self.public = js["public"]
        self.last = datetime.strptime(js["last"], "%Y-%m-%d %H:%M:%S")
        self.box = self._box_from_json(js["box"])

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


    # procedimiento de clase, almacena los peers en un archivo json
    @classmethod
    def save_file(cls, vector, path):
        l = []
        try:
            for v in vector:
                l.append(vector[v].to_json())
            l = Utiles.json_encode(l)
            Utiles.archivo_texto_guardar(path, l)
            return True
        except Exception as e:
            print("Error Archivo", e)
            return False

    # procedimiento de clase, recupera una lista de peers desde un archivo json
    @classmethod
    def read_file(cls, path):
        try:
            res = {}
            tmp = None
            l = Utiles.archivo_texto_leer(path)
            l = Utiles.json_decode(l)
            for v in l:
                tmp = Peer()
                tmp.from_json(v)
                res[tmp.idnodo] = tmp
            return res
        except:
            return None


    