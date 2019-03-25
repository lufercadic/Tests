# coding: utf8
import sys # solo para la linea de abajo
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
from Nodo import Nodo
from Mensaje import Mensaje
from flask import Flask, jsonify, request, abort # cosas servidor web
import threading    # para poder crear el hilo de trabajo
import time         # para poder usar el sleeo
import requests

# datos globales
nodo = Nodo()
app = Flask(__name__)


# FUNCIONES CONTROLADOR WEB
@app.route("/")
def index():
    return '"Hola, Como estan? que tendan un hermoso dia."'

@app.route("/tool/status", methods=['GET', 'POST'])
def tool_status():
    key, data = nodo.Estado()
    if(key == 200):
        return data
    else:
        return '', key

@app.route("/token/new", methods=['POST'])
def token_new():
    key = request.form.get('key')
    data = request.form.get('data')
    key, data = nodo.Token_Crear(key, data)
    if(key == 200):
        return data
    else:
        return '', key

@app.route("/nodo/reg", methods=['POST'])
def nodo_reg():
    key = request.form.get('key')
    data = request.form.get('data')
    key, data = nodo.Nodo_Registrar(key, data)
    if(key == 200):
        return data
    else:
        return '', key

@app.route("/nodo/unreg", methods=['POST'])
def nodo_unreg():
    key = request.form.get('key')
    data = request.form.get('data')
    key, data = nodo.Nodo_Desregistrar(key, data)
    if(key == 200):
        return data
    else:
        return '', key

@app.route("/nodo/send", methods=['POST'])
def nodo_send():
    key = request.form.get('key')
    data = request.form.get('data')
    key, data = nodo.Nodo_Transmitir(key, data)
    if(key == 200):
        return data
    else:
        return '', key

@app.route("/nodo/box", methods=['POST'])
def nodo_box():
    key = request.form.get('key')
    data = request.form.get('data')
    key, data = nodo.Nodo_Mailbox(key, data)
    if(key == 200):
        return data
    else:
        return '', key

@app.route("/client/reg", methods=['POST'])
def client_reg():
    key = request.form.get('key')
    data = request.form.get('data')
    key, data = nodo.Client_Registrar(key, data)
    if(key == 200):
        return data
    else:
        return '', key

@app.route("/client/box", methods=['POST'])
def client_box():
    key = request.form.get('key')
    data = request.form.get('data')
    key, data = nodo.Client_Mailbox(key, data)
    if(key == 200):
        return data
    else:
        return '', key


#Funcion principal
def main(args):
    #global nodo
    if(len(args) == 2):
        if(args[1] == "cfg"):
            nodo.CrearConf("ejemplo")
        else:
            if(nodo.Iniciar(args[1])):
                nodo.Trabajar()
                app.run(host=nodo.url, port=nodo.port)
                nodo.Finalizar()
    
if __name__ == "__main__":
	main(sys.argv)


#Crear Token
#-> key=id nodo
#   value=b64(public key)
#<- json(id, b64(public key))

#Registrar Nodo
#-> key=id token
#   value=pkey(json(id,url,port,security))
#<- pkey(json(id, url, port, password))

#Des-registrar Nodo
#-> key=id nodo
#   value=aes(json(id))