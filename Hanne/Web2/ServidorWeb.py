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
nodo = None
app = Flask(__name__)

nodo = Nodo("111-111-111", "localhost", 8082)


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
    #global nodo
    #args = [0, 1, 18081] # los queme esta vez
    #nodo = Nodo(args[1], '127.0.0.1', args[2])
    #threading.Thread(target=hilo, name='teclado', daemon=True).start()
    if len(args) > 1:
        r = requests.post("http://localhost:8082/post", data={"key": "llavesita"})
        print(r.text)
    else:
        app.run(host="0.0.0.0", port=8082)#nodo.port)
    
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