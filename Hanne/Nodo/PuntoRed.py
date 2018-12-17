# coding: utf8
import sys # se usa para la siguiente linea, y para obtener los parametros de la linea de comandos
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
import threading # para poder crear el hilo de trabajo
import time # para poder usar el sleeo
from Nodo import Nodo
from Mensaje import Mensaje


h_continuar = True
h_mensaje = None
def teclado():
    global h_continuar
    global h_mensaje

    while h_continuar:
        txt = input()
        if txt == '#1':
            h_continuar = False
        else:
            txt = txt.split(" ", 1)
            try: 
                txt[0] = int(txt[0])
                h_mensaje = (txt[0], txt[1])
            except ValueError:
                pass

# ============================== MAIN ==================================
def main():
    global h_continuar
    global h_mensaje

    cod = int(sys.argv[1])
    n = None

    if cod == 201:
        n = Nodo(1, 18001, [])
    elif cod == 202:
        n = Nodo(2, 18002, [18001])

    elif cod == 301:
        n = Nodo(1, 18001, [])
    elif cod == 302:
        n = Nodo(2, 18002, [18001, 18003])
    elif cod == 303:
        n = Nodo(3, 18003, [])

    else:
        return # si no es valido


    print('Nodo ' + str(n.nombre) + ' - ' + str(n.puerto))
    time.sleep(5) # un tiempo para iniciar todos los nodos
    n.escuchar()
    print('Escuchando')
    print('Escribir #1 para salir')

    # iniciar escucha del teclado
    hilo = threading.Thread(target=teclado, name='teclado', daemon=True)
    hilo.start()

    # ciclo de trabajo nodo
    while h_continuar:
        # revisamos si hay mensaje para enviar
        if h_mensaje is not None:
            n.agregar_mensaje(h_mensaje[0], h_mensaje[1])
            h_mensaje = None
        # procesamos el nodo
        n.procesar()
        time.sleep(0.25)   

    # fin
    n.detener()
    print('bye bye.')


# llamado al Main
main()

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
