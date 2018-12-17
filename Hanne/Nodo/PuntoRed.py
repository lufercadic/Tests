# coding: utf8
import sys          # se usa para la siguiente linea, y para obtener los parametros de la linea de comandos
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
import threading    # para poder crear el hilo de trabajo
import time         # para poder usar el sleeo
from Nodo import Nodo


# cree esta clase para separar la logica de la consola, del servicio nodo.
# esto evito usar variables globales, y organizo el control de la consola.
class Intermedio(object):
    # constructor
    def __init__(self, cmd="bye"):
        self.continuar = True
        self.mensaje = None
        self.texto = None
        self.cmd_salida = cmd
        self._hilo = None

    # funcion del hilo de la consola.
    # esta funcion obtiene la entrada del teclado
    def teclado(self, i):
        while self.continuar:
            txt = input() # se lee lo que escriba el usuario
            self.texto = txt # esto es mas para debug
            if txt == self.cmd_salida: # si el usuario escribe el comando de salir
                self.continuar = False
            else: # si escribe otra cosa
                # se intenta obtener el mensaje que se desea enviar
                txt = txt.split(" ", 1)
                try: 
                    txt[0] = int(txt[0])
                    if len(txt[1]) > 0:
                        self.mensaje = (txt[0], txt[1])
                except:
                    pass # si no es un mensaje valido no se hace nada

    # inicia el hilo de atender la consola
    def trabajar(self):
        self._hilo = threading.Thread(target=self.teclado, name='teclado', daemon=True, args=(self,))
        self._hilo.start()


# Aqui puse las configuraciones para las redes de ejemplo
def conf_pre_guardada(grupo, secuencia):
    # si es ejemplo de dos nodos
    if grupo == "1":
        if secuencia == "1":
            return (1, 18001, [])
        else:
            return (2, 18002, [18001])
    # si es ejemplo de 3 nodos
    if grupo == "2":
        if secuencia == "1":
            return (1, 18001, [])
        elif secuencia == "2":
            return (2, 18002, [18001, 18003])
        else:
            return (3, 18003, [])
    # si no es ninguno de los ejemplos
    raise ValueError("Combinacion de parametros no valida. XP")


# funcion main. Punto de inicio de la aplicacion
def main(args):
    # las variables que se usan en el proceso
    nodo = None
    con = None

    # obtenemos la configuracion del nodo
    if len(args) == 3:
        nodo = conf_pre_guardada(args[1], args[2])
        nodo = Nodo(nodo[0], nodo[1], nodo[2])
    else:
        raise ValueError("Numero de parametros no valido. XP")

    # creamos el lector de la consola
    con = Intermedio("#1")
    con.trabajar()

    # datos del nodo
    print('')
    print('Nodo:   ' + str(nodo.nombre))
    print('Puerto: ' + str(nodo.puerto))
    print('')
    #time.sleep(5) # un tiempo para iniciar todos los nodos
    nodo.escuchar() # se activa el servidor del nodo
    print(' - Servidor activado.')
    print(' - Consola activada. Escribir #1 para salir.')
    
    # ciclo principal, se repite hasta que el usuario lo detenga
    while con.continuar:
        # revisamos si hay un mensaje para enviar
        if con.mensaje is not None:
            nodo.agregar_mensaje(con.mensaje[0], con.mensaje[1])
            con.mensaje = None
        # realizamos un ciclo de procesamiento
        nodo.procesar()
        # esperamos antes de repetir el ciclo
        time.sleep(0.25)

    # se detiene el servidor del nodo
    print(' - Servidor apagado.')
    print(' - bye')
    print('')


# Inicio de la aplicacion. NoTocar.
if __name__ == '__main__':
	main(sys.argv)



# esto son enlaces utiles. no borrar :D

#import threading
#threadLock = threading.Lock()
#with threadLock:
#    global_counter += 1

#[Manejo de sincronizacion]
#http://effbot.org/zone/thread-synchronization.htm

#[Modos de controlar el input sin bloquear]
#https://stackoverflow.com/questions/5404068/how-to-read-keyboard-input
#https://stackoverflow.com/questions/2408560/python-nonblocking-console-input

#[Convertir entero a bytes y viceversa]
#https://docs.python.org/3/library/stdtypes.html#int.to_bytes

#[Convertir a Json]
#https://docs.python.org/3.4/library/json.html#module-json

#[Serializacion]
#https://docs.python.org/3.4/library/pickle.html
