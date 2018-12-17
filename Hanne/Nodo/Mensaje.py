# coding: utf8
import json

# clase que representa un mensaje en la red
class Mensaje(object):
    # variable de clase
    next_id = 1 # uso esta como un contador global para los id de los mensajes

    # constructor
    def __init__(self, ndestino=None, ncontenido=None, norigen=None, nentregadopor=None):
        self.id = str(Mensaje.next_id); # codigo del mensaje
        self.destino = 0       # nodo destino. es un numero
        self.origen = 0        # nodo origen. es un numero
        self.contenido = ''    # texto del mensaje
        self.entregado_por = 0 # nodo que entrego el mensaje. no es igual al que lo envia
        # asignamos los parametros que si se entregaron
        if ndestino is not None:
            self.destino = ndestino
        if norigen is not None:
            self.origen = norigen
        if ncontenido is not None:
            self.contenido = ncontenido
        if nentregadopor is not None:
            self.entregado_por = nentregadopor


    # asigna un id al mensaje, esto para diferenciarlo
    def set_id(self, prefix):
        self.id = str(prefix) + 'N' + str(Mensaje.next_id)
        Mensaje.next_id += 1


    # convierte la instancia en un texto json
    def to_json(self):
        js = {'to': self.destino, 'msg': self.contenido, 'id': self.id, 'from': self.origen}
        js = json.dumps(js)
        return js


    # recupera los datos desde un texto json
    def from_json(self, js):
        js = json.loads(js)
        self.destino = js['to']
        self.contenido = js['msg']
        self.id = js['id']
        self.origen = js['from']


    # procedimiento de clase, crea un mensaje desde un json
    @classmethod
    def create_from_json(cls, js, entregado_por=0):
        nu = Mensaje(nentregadopor=entregado_por)
        nu.from_json(js)
        return nu