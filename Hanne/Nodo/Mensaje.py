# coding: utf8
import json

# clase que representa un mensaje en la red
class Mensaje(object):
    # variable de clase
    next_id = 1
    # constructor
    def __init__(self, ndestino=None, ncontenido=None, norigen=None, nentregadopor=None):
        self.id = str(Mensaje.next_id);
        if ndestino is not None:
            self.destino = ndestino
        if norigen is not None:
            self.origen = norigen
        if ncontenido is not None:
            self.contenido = ncontenido
        if nentregadopor is not None:
            self.entregado_por = nentregadopor
        else:
            self.entregado_por = 0

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
    def create_from_json(cls, js, entregado_por=None):
        nu = Mensaje(nentregadopor=entregado_por)
        nu.from_json(js)
        return nu