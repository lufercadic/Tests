# coding: utf8
import os
#os.environ["KIVY_NO_CONSOLELOG"] = "1"
import sys
sys.path.append("")
from kivy.config import Config # esto debe ir primero que todo, porque sino se resetea
#Config.set('graphics', 'width', 400); # tamaño de la ventana al abrir
#Config.set('graphics', 'height', 400); # tamaño de la ventana al abrir
#Config.set('graphics', 'position', 'custom')
#Config.set('graphics', 'left', 2000) # posicion de la ventana al abrir
#Config.set('graphics', 'top',  50) # posicion de la ventana al abrir

# Cargamos los controladores de las pantallas
import LoginScreen
import LogoutScreen
import ExportScreen
import FileScreen
import TableScreen
import SettingScreen

# Cargamos los objetos que vamos a utilizar
from RedcapPlugin import RedcapPlugin

# Cargamos los componentes de al interfaz
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder


# Cargamos la plantilla de cada pantalla
Builder.load_file('LoginScreen.kv')
Builder.load_file('LogoutScreen.kv')
Builder.load_file('ExportScreen.kv')
Builder.load_file('FileScreen.kv')
Builder.load_file('TableScreen.kv')
Builder.load_file('SettingScreen.kv')


# Objeto Kivy que sirve como raiz de todos los controles
class MyBoxLayout(BoxLayout):
    """Clase hereda de BoxLayout"""

    def Init(self):
        """Una especie de constructor"""
        self.user  = None
        self.filepath = None
        self.data = None

    def sign_in(self, user):
        """Funcion para indicar el inicio de sesion de un usuario"""
        #print("Sign-in:", user)
        #user = {"id": 1, "user": "goku", "email": "goku@saiyan.com", "name": "Son Goku"}
        self.user  = user;
        self.show_imgText(user['id'], user['name'], user['email'])
        self.go_index()

    def sign_out(self):
        """Funcion para indicar el fin de sesion de un usuario"""
        self.user  = None;
        self.show_imgText(0, None, None)
        self.ids['contentpanel'].current = "login"

    def go_index(self):
        """Funcion para mostrar la pantalla index"""
        self.ids['contentpanel'].current = "file"

    def go_login(self):
        """Funcion para mostrar la pantalla login"""
        if self.user == None:
            self.ids['contentpanel'].current = "login"

    def go_file(self):
        """Funcion para mostrar la pantalla file"""
        self.ids['contentpanel'].current = "file"

    def go_table(self):
        """Funcion para mostrar la pantalla table"""
        self.ids['screentable']._on_show(self.data)
        self.ids['contentpanel'].current = "table"

    def show_imgText(self, img, txt1, txt2):
        """Configura la imagen de usuario y el texto asociado"""
        if img == 0:
            self.ids['img'].source = "img/User0.png"
            self.ids['username'].text = "[b]REDPor[/b]"
        else:             
            self.ids['img'].source = "img/User{}.png".format(img)
            self.ids['username'].text = "[b]{}[/b]\n[size=10]{}[/size]".format(txt1, txt2)

    def file_select(self, fp):
        """Funcion para indicar que archivo selecciono el usuario"""
        self.filepath = fp # copiamos la ubicacion
        self.data = RedcapPlugin.load_file(fp) # leemos los datos
        #print(self.data)
        self.go_table()



# Aplicacion Kivy GUI
class ReportApp(App):
    """Clase principal, esta genera la ventana inicial"""
    def build(self):
        """Genera el contenedor de la ventana principal (Elemento raiz)"""
        self.title = 'REDRep: Research Electronic Data Report Generator'
        self.icon = 'img/icon0.png'
        bl = MyBoxLayout()
        bl.Init()
        return bl


# Procedimiento principal, punto de inicio de la aplicacion
def Main(args):
    a = ReportApp()
    a.run()
    
# Inicio de la aplicacion. NoTocar.
if __name__ == '__main__':
	Main(sys.argv)