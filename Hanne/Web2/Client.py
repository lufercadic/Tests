# coding: utf8
import sys # solo para la linea de abajo
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
from datetime import datetime
from Mensaje import Mensaje
from Utiles import Utiles

# clase que representa un mensaje en la red
class Client(object):
    # constructor
    def __init__(self, nid, nname, nred, npass):
        self.idcliente = nid       # Identificador del cliente
        self.nombre = nname         # Nombre del nodo
        self.subred = nred        # Nombre de la red de trabajo
        self.password = npass      # Password de comunicacion
        self.last = datetime.now() # Fecha del ultimo acceso nodo
        self.box = []              # Cola de mensajes para entregar

    # asigna un id al mensaje, esto para diferenciarlo
    def setLast(self):
        self.last = datetime.now()


    # convierte la instancia en un texto json
    def to_json(self):
        js = dict(zip(["id", "nombre", "subred", "password", "last", "box"],
                 [self.idcliente, self.nombre, self.subred, self.password, self.last.strftime("%Y-%m-%d %H:%M:%S"), self._box_to_json(self.box)]))
        return js


    # recupera los datos desde un texto json
    def from_json(self, js):
        self.idcliente = js["id"]
        self.nombre = js["nombre"]
        self.subred = js["subred"]
        self.password = js["password"]
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
        
    # procedimiento de clase, almacena los clientes en un archivo json
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
            print(e)
            return False

    # procedimiento de clase, recupera una lista de clientes desde un archivo json
    @classmethod
    def read_file(cls, path):
        try:
            res = {}
            tmp = None
            l = Utiles.archivo_texto_leer(path)
            l = Utiles.json_decode(l)
            for v in l:
                tmp = Client(None, None, None, None)
                tmp.from_json(v)
                res[tmp.idcliente] = tmp
            return res
        except Exception as e:
            print(e)
            return None