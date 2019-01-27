# coding: utf8
import sys # solo para la linea de abajo
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
from Nodo import Nodo
from Mensaje import Mensaje
from flask import Flask, jsonify # cosas servidor web
import threading    # para poder crear el hilo de trabajo
import time         # para poder usar el sleeo


# datos globales
nodo = None
app = Flask(__name__)

# FUNCIONES CONTROLADOR WEB
@app.route("/")
def index():
    return "Hola,  El nodo nodito los saluda"

@app.route("/cliente/enviar/<int:destino>/<contenido>")
def cliente_enviar(destino, contenido):
    id = nodo.agregar_mensaje(destino, contenido)
    return jsonify({"estado":"ok", "nodo":nodo.nombre, "idmsg":id})

@app.route("/cliente/recibir")
def cliente_recibir():
    res = []
    items = nodo.ver_mensajes();
    for i in items:
        n = {"id":i[0], "origen":i[1], "contenido":i[2]}
        res.append(n)
    return jsonify(res)

@app.route("/cliente/borrar")
def cliente_borrar():
    nodo.borrar_mensajes();
    return jsonify({"estado":"ok", "nodo":nodo.nombre})

@app.route("/servidor/saludar/<int:id>/<url>/<int:port>")
def servidor_hello(id, url, port):
    nodo.nodo_registrar(id, url, port)
    return jsonify({"estado":"ok", "nodo":nodo.nombre})

@app.route("/servidor/enviar/<int:id>/<contenido>")
def servidor_recibir(id, contenido):
    nodo.nodo_mensaje(id, contenido)
    return jsonify({"estado":"ok", "nodo":id})




# FUNCIONES APLICACION
def hilo():
    time.sleep(2)
    print("")
    print("Servidor: ", nodo.nombre)
    print("URL: ", nodo.url, nodo.port)
    print("")
    while True:
        nodo.procesar()
        time.sleep(0.25)


#Funcion principal
def main(args):
    global nodo
    args = [0, 1, 8081] # los queme esta vez
    nodo = Nodo(args[1], '127.0.0.1', args[2])
    threading.Thread(target=hilo, name='teclado', daemon=True).start()
    app.run(host="0.0.0.0", port=nodo.port)
    
if __name__ == "__main__":
	main(sys.argv)