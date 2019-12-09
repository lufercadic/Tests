# coding: utf8
import sys
sys.path.append("")
import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.core.window import Window

# Clase controladora de la pantalla de Seleccion de archivo
class FileScreen(Screen):
    """Implementacion de la pantalla de seleccionar archivo"""

    def __init__(self, **kwargs):
        """Constructor"""
        super(Screen, self).__init__(**kwargs)
        self.root = ObjectProperty(None) # para poder acceder al root mas facil
        Window.bind(on_dropfile=self._on_file_drop) # controlar evento drop file
        self.filepath = None

    def _on_file_drop(self, window, file_path):
        """Controla el evento Drop-File. se invoca sin importar donde se hizo el drop"""
        if self.manager.current == 'file':
            self.filepath = file_path.decode("utf-8")
            #print('Drop-File:', self.filepath)
            self.ids['pfile'].text = self.filepath

    def select(self, *args):
        """Controla el evento, escoger archivo"""
        try:
            #print(args[1][0])
            f = args[1][0]
            self.filepath = f
            self.ids['pfile'].text = self.filepath
        except: pass

    def next(self):
        """Controla el evento click del boton continuar"""
        if self.filepath != None:
            f = self.filepath
            self.filepath = None
            self.ids['pfile'].text = ''
            self.root.file_select(f)