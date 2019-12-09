# coding: utf8
import sys
sys.path.append("")
import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty


class LogoutScreen(Screen):
    """Implementacion de la pantalla de log-out"""

    def __init__(self, **kwargs):
        """Constructor"""
        super(Screen, self).__init__(**kwargs)
        self.root = ObjectProperty(None) # para poder acceder al root mas facil

    def sigout_button(self):
        """Funcion para controlar el evento click en el boton sign-out"""
        self.root.sign_out()

    def cancel_button(self):
        """Funcion para controlar el evento click en el boton Cancelar"""
        self.root.go_index()