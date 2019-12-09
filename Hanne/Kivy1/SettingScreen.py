# coding: utf8
import sys
sys.path.append("")
import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty


class SettingScreen(Screen):
    """Implementacion de la pantalla de configuracion"""

    def __init__(self, **kwargs):
        """Constructor"""
        super(Screen, self).__init__(**kwargs)
        self.root = ObjectProperty(None) # para poder acceder al root mas facil