# coding: utf8
import sys # solo para la linea de abajo
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
from Utiles import Utiles
import requests
from datetime import datetime, timedelta
from Mensaje import Mensaje
import time # para poder usar el sleep

# Implementacion de un nodo de la red
class CProxy(object):
    # constructor
    def __init__(self, url="localhost", port=18001, name="nodo1", net="red1"):
        self.id = Utiles.generar_id()
        self.urlServer = url
        self.portServer = port
        self.passServer = ""
        self.nodoid = ""
        self.name = name
        self.net = net

    def registrar(self):
        # genero llaves asimetricas
        ppkeys = Utiles.rsa_generar_clave()
        ppkeys = (ppkeys['public_key'], ppkeys['private_key'])
        # hago peticion de token
        r1 = requests.post('http://{}:{}/token/new'.format(self.urlServer, self.portServer), data={"key": self.id, "data": Utiles.b64_encode(ppkeys[0])})
        r1 = Utiles.json_decode(r1.text)["value"]
        # hago peticion de registro
        r2 = dict(zip(["id", "name", "net", "security"],
                        [self.id, self.name, self.net, Utiles.generar_id6()]))
        r2 = Utiles.rsa_cifrar_str(Utiles.b64_decode(r1["pkey"]), Utiles.json_encode(r2))
        r2 = requests.post('http://{}:{}/client/reg'.format(self.urlServer, self.portServer), data={"key": r1["id"], "data": r2})
        # proceso respuesta
        r2 = Utiles.rsa_descifrar_str(ppkeys[1], r2.text)
        r2 = Utiles.json_decode(r2)["value"]
        self.id = r2["id"]
        self.passServer = r2["password"]
        self.nodoid = r2["nodo"]


    def leer_mensaje(self):
        # creo peticion de leer mensaje
        r = '{ "op": "get" }'
        r = Utiles.aes_cifrar_str(self.passServer, r)
        r = requests.post('http://{}:{}/client/box'.format(self.urlServer, self.portServer), data={"key": self.id, "data": r})
        # proceso respuesta
        r = Utiles.aes_descifrar_str(self.passServer, r.text)
        r = Utiles.json_decode(r)["value"]
        if (r is None):
            return None
        m = Mensaje.create_from_json(r)
        # envio peticionde borrar mensaje
        r = '{ "op": "del" }'
        r = Utiles.aes_cifrar_str(self.passServer, r)
        r = requests.post('http://{}:{}/client/box'.format(self.urlServer, self.portServer), data={"key": self.id, "data": r})
        # aqui toca mirar si se pudo borrar
        return m
        

    def enviar_mensaje(self, destinoCliente, destinoRed, destinoNodo=None, contenido=""):
        # creo peticion de leer mensaje
        r = dict(zip(["node", "client", "subnet", "content"], [destinoNodo, destinoCliente, destinoRed, contenido]))
        r = Utiles.json_encode(r)
        r = Utiles.aes_cifrar_str(self.passServer, r)
        r = requests.post('http://{}:{}/client/send'.format(self.urlServer, self.portServer), data={"key": self.id, "data": r})
        # proceso respuesta
        r = Utiles.aes_descifrar_str(self.passServer, r.text)
        r = Utiles.json_decode(r)
        msgid = r["value"]
        r = r["status"]
        if (r == 0):
            return msgid
        else:
            return None
        
            


# main aqui, esta parte es para pruebas

def LeerMensaje(c):
    print("Leer Mensaje", c.name)
    m = c.leer_mensaje()
    if(m is None): print("No Hay Mensaje")
    else: print("Mensaje", m.id, m.contenido)

def EnviarMensaje(c1, c2):
    m = c1.enviar_mensaje(c2.id, c2.net, c2.nodoid, "de {} para {}, saludos".format(c1.name, c2.name))
    print("Mensaje Enviado", c1.name, c2.name, m)

def EnviarRed(c):
    m = c.enviar_mensaje(None, c.net, None, "de {} para red {}, saludos".format(c.name, c.net))
    print("Mensaje Enviado", c.name, c.net, m)

def EnviarNombre(c):
    txt = input("digite nombre: ")
    m = c.enviar_mensaje(txt, c.net, None, "de {} para nombre {}, saludos".format(c.name, txt))
    print("Mensaje Enviado", c.name, txt, m)


def main(args):
    c1 = CProxy("localhost", 18001, "cali", "colombia")
    c2 = CProxy("localhost", 18002, "bogota", "colombia")
    c3 = CProxy("localhost", 18003, "medellin", "colombia")

    print("Registrando c1")
    c1.registrar()
    print("c1 =", c1.id)

    print("Registrando c2")
    c2.registrar()
    print("c2 =", c2.id)

    print("Registrando c3")
    c3.registrar()
    print("c3 =", c3.id)


    while True:
        text = input("opcion: ")
        if(text == "bye"): break
        elif(text == "c1"): LeerMensaje(c1)
        elif(text == "c2"): LeerMensaje(c2)
        elif(text == "c3"): LeerMensaje(c3)
        elif(text == "m12"): EnviarMensaje(c1, c2)
        elif(text == "m13"): EnviarMensaje(c1, c3)
        elif(text == "m21"): EnviarMensaje(c2, c1)
        elif(text == "m23"): EnviarMensaje(c2, c3)
        elif(text == "m31"): EnviarMensaje(c3, c1)
        elif(text == "m32"): EnviarMensaje(c3, c2)
        elif(text == "r1"): EnviarRed(c1)
        elif(text == "r2"): EnviarRed(c2)
        elif(text == "r3"): EnviarRed(c3)
        elif(text == "n1"): EnviarNombre(c1)
        elif(text == "n2"): EnviarNombre(c2)
        elif(text == "n3"): EnviarNombre(c3)


# funcion main
if __name__ == "__main__":
	main(sys.argv)