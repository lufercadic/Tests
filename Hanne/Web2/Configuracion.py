# coding: utf8
import sys # solo para la linea de abajo
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
from Utiles import Utiles
import json
import datetime


# clase que almacena la configuracion basica
class Configuracion(object):
    # constructor
    def __init__(self, puerto=None, url=None):
        self.id = None
        self.puerto = 18001
        self.url = '127.0.0.1'
        self.nombre = 'Nodo Adam'
        self.fecha = datetime.datetime.now()
        self.semillas = []

        self.id = Utiles.generar_id() #genera un nuevo id para el nodo
        # asignamos los parametros que si se entregaron
        if puerto is not None:
            self.puerto = 18001
        if url is not None:
            self.url = '127.0.0.1'
            
    # calcula y asigna un nuevo id
    def nuevo_id(self):
        self.id = Utiles.generar_id()

    # convierte la instancia en un texto json
    def json_write(self):
        js = {'id': self.id, 'puerto': self.puerto, 'url': self.url,
              'nombre': self.nombre, 'fecha': self.fecha.strftime("%Y-%m-%d %H:%M:%S"),
              'semillas': self.semillas}
        js = json.dumps(js) #json.dumps(js, indent=4)
        return js #js.encode("utf-8") <-esto si lo quiero en modo vector

    # recupera los datos desde un texto json
    def json_read(self, js):
        js = json.loads(js)
        self.id = js['id']
        self.puerto = js['puerto']
        self.url = js['url']
        self.nombre = js['nombre']
        self.fecha = datetime.datetime.strptime(js['fecha'], "%Y-%m-%d %H:%M:%S")
        self.semillas = js['semillas']
        if not isinstance(self.semillas, list):
            self.semillas = []

    # crea un instancia y la llena con los datos del json
    @classmethod
    def json_create(cls, js):
        c = Configuracion()
        c.json_read(js)
        return c
    
    # almacena el objeto en un archivo con formato json
    def file_write(self, path):
        Utiles.archivo_texto_guardar(path, self.json_write())

    # recupera un objeto desde un archivo con formato json
    def file_read(self, path):
        self.json_read(Utiles.archivo_texto_leer(path))
    
    # crea una instancia y la llena con los datos en un archivo json
    @classmethod
    def file_create(self, path):
        c = Configuracion()
        c.file_read(js)
        return c