# coding: utf8
import sys
sys.path.append("")
import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

#from kivy.lang import Builder
#Builder.load_file('kivi.kv')

class LoginScreen(Screen):
    """Implementacion de la pantalla de login"""

    def __init__(self, **kwargs):
        """Constructor"""
        super(Screen, self).__init__(**kwargs)
        self.root = ObjectProperty(None) # para poder acceder al root mas facil

    def sigin_button(self):
        """Funcion para controlar el evento click en el boton sign-in"""
        if self.ids.login.text == "alvaro":
            self.ids.msg.text = "Ese man no puede entrar"
        elif self.ids.login.text == "goku" or self.ids.login.text == "vegeta":
            u = self.ids.login.text
            self.ids.msg.text = ""
            self.ids.login.text = ""
            self.ids['pass'].text = ""
            #App.get_running_app().root.sign_in({"id": 1, "user": "goku", "email": "goku@saiyan.com", "name": "Son Goku"})
            if u == "goku":
                self.root.sign_in({"id": 1, "user": "goku", "email": "goku@saiyan.com", "name": "Son Goku"})
            else:
                self.root.sign_in({"id": 2, "user": "vegeta", "email": "vegeta@saiyan.com", "name": "Vegeta  IV"})
        else:
            self.ids.msg.text = "User/Password not valid"




# Aplicacion Kivy GUI
class LoginScreenApp(App):
    """Clase principal, esta genera la ventana inicial"""
    def build(self):
        return LoginScreen()

# Inicio de la aplicacion. NoTocar.
if __name__ == '__main__':
	LoginScreenApp().run()