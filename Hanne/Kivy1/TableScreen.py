# coding: utf8
import sys
sys.path.append("")
import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from RedcapPlugin import RedcapPlugin


class TableScreen(Screen):
    """Implementacion de la pantalla que muestra los datos obtenidos"""

    def __init__(self, **kwargs):
        """Constructor"""
        super(Screen, self).__init__(**kwargs)
        self.root = ObjectProperty(None) # para poder acceder al root mas facil
        self.data = None

    def _on_show(self, data):
        self.data = data
        c = self.ids['project']
        c.values = self.data.Redcap.projects_list
        c.text = c.values[0]

    def proyect(self, name):
        self.ids['salida'].text = name