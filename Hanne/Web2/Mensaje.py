# coding: utf8
import sys # solo para la linea de abajo
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
from datetime import datetime
from Utiles import Utiles


# clase que representa un mensaje en la red
class Mensaje(object):
    # variable de clase
    next_id = 0 # uso esta como un contador global para los id de los mensajes

    # constructor
    def __init__(self):
        self.id = 0;               # codigo del mensaje
        self.origenNodo = None     # nodo origen. es un texto
        self.origenCliente = None  # cliente origen. es un numero
        self.destinoNodo = None    # nodo destino. es un texto
        self.destinoCliente = None # cliente destino. es un numero
        self.destinoRed = None     # SubRed destino
        self.contenido = ''        # Contenido del mensaje. se trata como un texto
        self.entregado_por = None  # nodo que entrego el mensaje. no es igual al que lo envia
                
    # asigna un id al mensaje, esto para diferenciarlo
    def set_id(self):
        if(Mensaje.next_id == 0):
            dt = datetime.now()
            dt = (dt.microsecond * 100) + dt.minute
            Mensaje.next_id = dt;

        self.id = Mensaje.next_id
        Mensaje.next_id += 1

    # convierte la instancia en un texto json
    def to_json(self):
        js = dict(zip(["id", "fn", "fc", "tn", "tc", "nt", "co"],
                 [self.id, self.origenNodo, self.origenCliente, self.destinoNodo, self.destinoCliente, self.destinoRed, self.contenido]))
        #js = json.dumps(js)
        return js

    # recupera los datos desde un texto json
    def from_json(self, js):
        #js = json.loads(js)
        self.id = js["id"]
        self.origenNodo = js["fn"]
        self.origenCliente = js["fc"]
        self.destinoNodo = js["tn"]
        self.destinoCliente = js["tc"]
        self.destinoRed = js["nt"]
        self.contenido = js["co"]

    # verifica que tenga un destino. Debe tener almenos unos de los valores destinoXXX
    def hay_destino(self):
        if(self.destinoCliente is None and self.destinoNodo is None and self.destinoRed is None):
            return False
        else:
            return True

    # verifica que tenga un origen. Debe tener ambos valores origenXXX
    def hay_origen(self):
        if(self.origenNodo is None or self.origenCliente is None):
            return False
        else:
            return True

    # verifica que tenga tanto un origen como un destino
    def esta_completo(self):
        return (self.hay_destino() and self.hay_origen())

    # si un mensaje es para enviar a toda la sub-red o si es especifico
    def es_broadcast(self):
        return (self.destinoNodo is None)

    # Obtiene un identificador unico del mensaje
    def sha(self):
        js = Utiles.json_encode(self.to_json())
        js = Utiles.sha256_generar_str(js)
        return (self.id, js)

    # procedimiento de clase, crea un mensaje desde un json
    @classmethod
    def create_from_json(cls, js, entregado_por=None):
        nu = Mensaje()
        nu.entregado_por = entregado_por
        nu.from_json(js)
        return nu