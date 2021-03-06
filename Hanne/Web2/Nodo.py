# coding: utf8
import sys # solo para la linea de abajo
sys.path.append("") # toco hacer esto, porque no importaba los archivos Peer y Mensaje
#from queue import Queue  # cola de mensajes
from Mensaje import Mensaje
from Utiles import Utiles
from Peer import Peer
from Client import Client
from Configuracion import Configuracion
import requests
from datetime import datetime, timedelta
from threading import Thread, Lock
import time # para poder usar el sleep

# Implementacion de un nodo de la red
class Nodo(object):
    # constructor
    def __init__(self):
        self.nombreCfg = ""
        self.idnodo = ""       # codigo identificador del nodo
        self.url = "localhost" # url del servidor
        self.port = 18001      # puerto por el que escucha el servidor
        self.tokens = []       # listado de tokens pendientes
        self.peers = {}        # lista de peers (osea servidores/nodos)
        self.users = {}        # lista de clientes
        self.msg = []          # cola de mensajes para procesar
        self.old = []          # historico de mensajes recibidos.
        self.semaforo = Lock() # control de concurrencia
        self.continuar = True  # bandera del hilo de trabajo
        self.cfg = Configuracion()


    ######################################################################################################################
    # Crea un token de seguridad para el registro de Nodos y Clientes
    def Token_Crear(self, key, value):
        if(key is None or value is None): # no envieron los datos
            return (400, None)

        dt = datetime.now()
        id = str(round(dt.timestamp() * 1000))
        keys = Utiles.rsa_generar_clave()
        id = (id, keys['public_key'], keys['private_key'], Utiles.b64_decode(value), dt)
        self.semaforo.acquire()
        self.tokens.append(id);
        self.semaforo.release()
        keys = {"status":0, "value": { "id": id[0], "pkey":Utiles.b64_encode(keys['public_key']) } }
        print("Creando Token", id[0])
        return (200, Utiles.json_encode(keys))


    # Busca un token en la lista de token
    def Token_Buscar(self, idtoken):
        """
        Procedimiento que busca un token especifico
        :param idtoken: Codigo del token
        :return: Datos del token o None si no se encuentra
        """
        for t in self.tokens:
            if(t[0] == idtoken):
                return t
        return None
    

    # borra un token especifico
    def Token_Borrar(self, idtoken):
        i = len(self.tokens)-1
        while (i >= 0):
            if (self.tokens[i][0] == idtoken):
                self.semaforo.acquire()
                self.tokens.pop(i)
                self.semaforo.release()
                break
            i = i - 1
        

    # Borra los token que tengan mas de 5 minutos
    def Token_Limpieza(self):
        i = len(self.tokens)-1
        dt = datetime.now()
        self.semaforo.acquire()
        while (i >= 0):
            if ((dt - self.tokens[i][4]).total_seconds() >= 300):
                self.tokens.pop(i)
            i = i - 1
        self.semaforo.release()
    

    ######################################################################################################################
    # Registra un nodo en el servidor local
    def Nodo_Registrar(self, key, value):
        if(key is None or value is None): # no envieron los datos
            return (400, None)

        t = self.Token_Buscar(key) # obtengo el token de seguridad
        if(t is None): # si el token no existe
            return (401, None)
        else: # el token existe
            data = Utiles.rsa_descifrar_str(t[2], value) # descrifro los datos enviados
            data = Utiles.json_decode(data) # obtento el objeto del json
            pw = Utiles.generar_id10() # genero una cadena de 10 caracteres
            pw = data["security"][0:3] + pw + data["security"][3:] # se crea el password usando los 6 caracteres que envia el nodo cliente
            nuevo = Peer(data["id"], data["url"], data["port"], pw)
            #nuevo = {"idnodo": data["id"], "url": data["url"], "port": data["port"], "password": pw,  "public": True, "last": datetime.now(), "box": queue.Queue()}
            self.semaforo.acquire()
            self.peers[nuevo.idnodo] = nuevo # agrego el nodo nuevo a la lista. si ya existe se actualiza
            self.semaforo.release()
            self.Token_Borrar(t[0]) # borro el token de seguridad
            data = {"id": self.idnodo, "url": self.url, "port": self.port, "password": pw} # creo la respuesta
            data = {"status": 0, "value": data} # se crea el objeto respuesta web
            data = Utiles.json_encode(data) # convierto en una cadena json
            print("Registrando Nodo", nuevo.idnodo)
            return (200, Utiles.rsa_cifrar_str(t[3], data)) # retorno los datos encriptados


    # Borra el registro de un nodo
    def Nodo_Desregistrar(self, key, value):
        if(key is None or value is None): # no envieron los datos
            return (400, None)

        nd = self.peers.get(key) # buscamos registro del nodo-cliente
        if(nd is None): # no se encuentra el registro
            return (401, None)
        else:
            txt = Utiles.aes_descifrar_str(nd.password, value) # recupero la informacion
            txt = Utiles.json_decode(txt)
            if(txt["id"] == key): # si son iguales se borra el registro
                self.semaforo.acquire()
                self.peers.pop(key, None)
                self.semaforo.release()
                print("Quitando Nodo", key)
                return (200, '{"status": 0, "value": "ok"}')
            else:
                return (403, None) # si no son iguales, no se borra y generamos error
            

    # sirve para revisar si el nodo responde a las peticiones web
    def Estado(self):
        return (200, Utiles.json_encode({"status": 0, "value": "ok"}))


    # recibe un mensaje a ser transmitido desde otro nodo
    def Nodo_Transmitir(self, key, value):
        print("Mensaje Nodo-Nodo", key)
        if(key is None or value is None): # no envieron los datos
            return (400, None)

        nd = self.peers.get(key) # buscamos registro del nodo-cliente
        if(nd is None): # no se encuentra el registro
            return (401, None)
        else:
            txt = None
            # desencriptamos
            try: txt = Utiles.aes_descifrar_str(nd.password, value) # recupero la informacion
            except: return (401, None)
            # recuperamos el mensaje
            nd.setLast() # actualizamos la fecha
            try:
                txt = Utiles.json_decode(txt)
                txt = Mensaje.create_from_json(txt, key)
                if(txt.esta_completo()):
                    # agregmos a la cosa de mensajes por procesar
                    self.semaforo.acquire()
                    self.msg.append(txt)
                    self.semaforo.release()
                    return (200, Utiles.aes_cifrar_str(nd.password, '{"status": 0, "value": "ok"}'))
                else:
                    # el mensaje no tiene los valores correctos
                    return (200, Utiles.aes_cifrar_str(nd.password, '{"status": 1, "value": "Message is not complete"}'))
            except: return (400, None) # el mensaje no es valido


    # opera sobre el mailbox de un nodo
    def Nodo_Mailbox(self, key, value):
        if(key is None or value is None): # no envieron los datos
            return (400, None)

        nd = self.peers.get(key) # buscamos registro del nodo-cliente
        if(nd is None): # no se encuentra el registro
            return (401, None)
        else:
            txt = None
            # desencriptamos
            try: txt = Utiles.aes_descifrar_str(nd.password, value) # recupero la informacion
            except: return (401, None)
            # recuperamos el mensaje
            nd.setLast() # actualizamos la fecha
            try:
                txt = Utiles.json_decode(txt)
                txt = txt.get("op")
                if(txt is None): return (400, None)
                elif(txt == 'get'): # operacion leer el mailbox
                    if(len(nd.box) > 0):
                        # si hay algun mensaje en el mailbox
                        txt = nd.box[0]
                        txt = Utiles.json_encode({"status": 0, "value": txt.to_json()})
                        return (200, Utiles.aes_cifrar_str(nd.password, txt))
                    else:
                        # no hay nada en el mailbox
                        txt = Utiles.json_encode({"status": 0, "value": None})
                        return (200, Utiles.aes_cifrar_str(nd.password, txt))
                elif(txt == 'del'): # operacion borrar el primer mensaje del mailbox
                    if(len(nd.box) > 0):
                        # si hay se borra el mensaje
                        self.semaforo.acquire()
                        txt = nd.box.pop(0)
                        self.semaforo.release()
                        txt = Utiles.json_encode({"status": 0, "value": txt.id})
                        return (200, Utiles.aes_cifrar_str(nd.password, txt))
                    else:
                        # si no hay nada
                        txt = Utiles.json_encode({"status": 0, "value": None})
                        return (200, Utiles.aes_cifrar_str(nd.password, txt))
                elif(txt == 'cls'): # operacion borrar todos los mensajes
                    txt = 0
                    if(len(nd.box) > 0):
                        # si borra la lista
                        self.semaforo.acquire()
                        txt = len(nd.box)
                        nd.box.clear()
                        self.semaforo.release()
                    txt = Utiles.json_encode({"status": 0, "value": txt})
                    return (200, Utiles.aes_cifrar_str(nd.password, txt))
                else:
                    return (403, None) # no es una operacion valida
            except:
                return (400, None) # algo no esta bien


    # #####################################################################################################################
    # Registra un cliente en el servidor local
    def Client_Registrar(self, key, value):
        if(key is None or value is None): # no envieron los datos
            return (400, None)
        t = self.Token_Buscar(key) # obtengo el token de seguridad
        if(t is None): # si el token no existe
            return (401, None)
        else: # el token existe
            try:
                data = Utiles.rsa_descifrar_str(t[2], value) # descrifro los datos enviados
                data = Utiles.json_decode(data) # obtengo el objeto del json
                pw = Utiles.generar_id10() # genero una cadena de 10 caracteres
                pw = data["security"][0:3] + pw + data["security"][3:] # se crea el password usando los 6 caracteres que envia el cliente
                nuevo = Client(data["id"], data["name"], data["net"], pw)
                self.semaforo.acquire()
                self.users[nuevo.idcliente] = nuevo # agrego el cliente nuevo a la lista. si ya existe se actualiza
                self.semaforo.release()
                self.Token_Borrar(t[0]) # borro el token de seguridad
                print("Registrando Cliente", nuevo.idcliente)
                data = {"id": nuevo.idcliente, "password": pw, "nodo": self.idnodo} # creo la respuesta
                data = {"status": 0, "value": data} # se crea el objeto respuesta web
                data = Utiles.json_encode(data) # convierto en una cadena json
                return (200, Utiles.rsa_cifrar_str(t[3], data)) # retorno los datos encriptados
            except:
                return (400, None)


    # opera sobre el mailbox de un cliente
    def Client_Mailbox(self, key, value):
        print("MailBox Cliente", key)
        if(key is None or value is None): # no envieron los datos
            return (400, None)

        nd = self.users.get(key) # buscamos registro del cliente
        if(nd is None): # no se encuentra el registro
            return (401, None)
        else:
            txt = None
            # desencriptamos
            try: txt = Utiles.aes_descifrar_str(nd.password, value) # recupero la informacion
            except: return (401, None)
            # recuperamos el mensaje
            nd.setLast() # actualizamos la fecha
            try:
                txt = Utiles.json_decode(txt)
                txt = txt.get("op")
                if(txt is None): return (400, None)
                elif(txt == 'get'): # operacion leer el mailbox
                    if(len(nd.box) > 0):
                        # si hay algun mensaje en el mailbox
                        txt = nd.box[0]
                        txt = Utiles.json_encode({"status": 0, "value": txt.to_json()})
                        return (200, Utiles.aes_cifrar_str(nd.password, txt))
                    else:
                        # no hay nada en el mailbox
                        txt = Utiles.json_encode({"status": 0, "value": None})
                        return (200, Utiles.aes_cifrar_str(nd.password, txt))
                elif(txt == 'del'): # operacion borrar el primer mensaje del mailbox
                    if(len(nd.box) > 0):
                        # si hay se borra el mensaje
                        self.semaforo.acquire()
                        txt = nd.box.pop(0)
                        self.semaforo.release()
                        txt = Utiles.json_encode({"status": 0, "value": txt.id})
                        return (200, Utiles.aes_cifrar_str(nd.password, txt))
                    else:
                        # si no hay nada
                        txt = Utiles.json_encode({"status": 0, "value": None})
                        return (200, Utiles.aes_cifrar_str(nd.password, txt))
                elif(txt == 'cls'): # operacion borrar todos los mensajes
                    txt = 0
                    if(len(nd.box) > 0):
                        # si borra la lista
                        self.semaforo.acquire()
                        txt = len(nd.box)
                        nd.box.clear()
                        self.semaforo.release()
                    txt = Utiles.json_encode({"status": 0, "value": txt})
                    return (200, Utiles.aes_cifrar_str(nd.password, txt))
                else:
                    return (403, None) # no es una operacion valida
            except:
                return (400, None) # algo no esta bien


    # recibe un mensaje desde un cliente para ser transmitido
    def Client_Enviar(self, key, value):
        print("Mensaje Cliente-Nodo", key)
        if(key is None or value is None): # no envieron los datos
            return (400, None)

        nd = self.users.get(key) # buscamos registro del cliente
        if(nd is None): # no se encuentra el registro
            return (401, None)
        else:
            txt = None
            # desencriptamos
            try: txt = Utiles.aes_descifrar_str(nd.password, value) # recupero la informacion
            except: return (401, None)
            # recuperamos el mensaje
            try:
                txt = Utiles.json_decode(txt)
                msg = Mensaje()
                msg.set_id()
                msg.origenNodo = self.idnodo
                msg.origenCliente = nd.idcliente
                msg.destinoNodo = txt.get("node", None)
                msg.destinoCliente = txt.get("client", None)
                msg.destinoRed = txt.get("subnet", None)
                msg.contenido = txt.get("content", "")
                if(msg.esta_completo()):
                    # agregmos a la cosa de mensajes por procesar
                    self.semaforo.acquire()
                    self.msg.append(msg)
                    self.semaforo.release()
                    return (200, Utiles.aes_cifrar_str(nd.password, Utiles.json_encode({"status": 0, "value": msg.id})))
                else:
                    # el mensaje no tiene los valores correctos
                    return (200, Utiles.aes_cifrar_str(nd.password, '{"status": 1, "value": "Message is not complete"}'))
            except: return (400, None) # el mensaje no es valido


    ######################################################################################################################
    # revisa si un nodo responde
    def Nodo_IrSaludar(self, url, port):
        try:
            # hago peticion
            r = requests.get('http://{}:{}/tool/status'.format(url, port))
            r = Utiles.json_decode(r.text)
            if(r["status"] == 0): return True
            else: return False
        except:
            return False


    # registra este nodo en otro servidor nodo
    def Nodo_IrRegistrar(self, url, port):
        print("Ir a Registrar Nodo", url, port)
        try:
            # genero llaves asimetricas
            ppkeys = Utiles.rsa_generar_clave()
            ppkeys = (ppkeys['public_key'], ppkeys['private_key'])
            # hago peticion de token
            r1 = requests.post('http://{}:{}/token/new'.format(url, port), data={"key": "0000-0000-0000-0000", "data": Utiles.b64_encode(ppkeys[0])})
            r1 = Utiles.json_decode(r1.text)["value"]
            # hago peticion de registro
            r2 = dict(zip(["id", "url", "port", "security"],
                          [self.idnodo, self.url, self.port, Utiles.generar_id6()]))
            r2 = Utiles.rsa_cifrar_str(Utiles.b64_decode(r1["pkey"]), Utiles.json_encode(r2))
            r2 = requests.post('http://{}:{}/nodo/reg'.format(url, port), data={"key": r1["id"], "data": r2})
            # proceso respuesta
            r2 = Utiles.rsa_descifrar_str(ppkeys[1], r2.text)
            r2 = Utiles.json_decode(r2)["value"]
            r1 = Peer(r2["id"], r2["url"], r2["port"], r2["password"])
            self.semaforo.acquire()
            self.peers[r1.idnodo] = r1 # agrego el nuevo nodo
            self.semaforo.release()
            return True
        except Exception as e:
            return False


    # para un solo nodo, leer los mensajes
    def RecuperamosMensajes_n(self, peer):
        # creo peticion de leer mensaje
        r = '{ "op": "get" }'
        r = Utiles.aes_cifrar_str(peer.password, r)
        r = requests.post('http://{}:{}/nodo/box'.format(peer.url, peer.port), data={"key": self.idnodo, "data": r})
        # proceso respuesta
        r = Utiles.aes_descifrar_str(peer.password, r.text)
        r = Utiles.json_decode(r)["value"]
        if (r is None):
            return None
        m = Mensaje.create_from_json(r)
        # envio peticionde borrar mensaje
        r = '{ "op": "del" }'
        r = Utiles.aes_cifrar_str(peer.password, r)
        r = requests.post('http://{}:{}/nodo/box'.format(peer.url, peer.port), data={"key": self.idnodo, "data": r})
        r = Utiles.aes_descifrar_str(peer.password, r.text)["status"]
        if(r == 0):
            self.semaforo.acquire()
            self.msg.append(m)
            self.semaforo.release()


    # para cada nodo, lee los mensajes que tenga pendientes
    def RecuperamosMensajes(self):
        for p in self.peers:
            p = self.peers[p]
            if(p.public):
                try:
                    self.RecuperamosMensajes_n(p)
                except: pass


    # Envia un mensaje a otro nodo
    def Nodo_PasarMensaje(self, nodo, m):
        try:
            data = Utiles.aes_cifrar_str(nodo.password, Utiles.json_encode(m.to_json()))
            # hago peticion de token
            r = requests.post('http://{}:{}/nodo/send'.format(nodo.url, nodo.port), data={"key": self.idnodo, "data": data})
            r = Utiles.aes_descifrar_str(nodo.password, r.text)
            r = Utiles.json_decode(r)["status"]
            if (r == 0): return True
            else: return False
        except:
            return False


    # Intenta registrar todos las semillas iniciales
    def RegistrarNodosNuevos(self):
        for s in self.cfg.semillas:
            self.Nodo_IrRegistrar(s[0], s[1])
        self.cfg.semillas.clear()
   
                 
    # Verifica si los nodos se pueden acceder directamente
    def VerificarNodos(self):
        r = False
        for n in self.peers:
            r = self.Nodo_IrSaludar(self.peers[n].url, self.peers[n].port)
            self.peers[n].public = r
            print("Publico:", self.peers[n].url, self.peers[n].port, r)


    # Copia un mensaje al mailbox de todos los nodos
    def ProcesarMensajes_nodos(self, msg):
        self.semaforo.acquire()
        try:
            print("email para nodos")
            for n in self.peers:
                if(msg.entregado_por != self.peers[n].idnodo):
                    print("email agregado nodo", n)
                    self.peers[n].box.append(msg)
        except: pass
        finally: self.semaforo.release()


    # Copia un mensaje a todos los clientes de una subnet
    def ProcesarMensajes_clientes(self, msg):
        self.semaforo.acquire()
        try:
            print("email clientes red")
            for c in self.users:
                if(msg.destinoRed == self.users[c].subred and (msg.origenNodo != self.idnodo or msg.origenCliente != self.users[c].idcliente)):
                    print("email agregado cliente", c)
                    self.users[c].box.append(msg)
        finally: self.semaforo.release()


    # Copia un mensaje a todos los clientes de una subnet y mismo nombre
    def ProcesarMensajes_clientes2(self, msg):
        self.semaforo.acquire()
        try:
            print("email cliente nombre")
            for c in self.users:
                if(msg.destinoRed == self.users[c].subred and msg.destinoCliente == self.users[c].nombre):
                    print("email agregado cliente2", c)
                    self.users[c].box.append(msg)
        finally: self.semaforo.release()


    # revisa si un mensaje esta en el historico, sino esta lo agrega
    def Historico(self, m):
        sha = m.sha()
        for d in self.old:
            if(d[0] == sha[0] and d[1] == sha[1]):
                return True
        self.old.append(sha)
        return False


    # Procesa los mensajes pendientes
    def ProcesarMensajes(self):
        while(len(self.msg) > 0):
            self.semaforo.acquire()
            m = self.msg.pop(0) # obtengo el mensaje
            self.semaforo.release()
            if(self.Historico(m)): continue # ya estaba antes
            if(m.es_broadcast()): #si es multi-cliente
                self.ProcesarMensajes_nodos(m)
                if(m.destinoCliente is None): # si se envio a una subnet
                    self.ProcesarMensajes_clientes(m)
                else: # si se envio a un cliente en subnet
                    self.ProcesarMensajes_clientes2(m)
            else: # se envio a un cliente especifico
                if(m.destinoNodo == self.idnodo): #si es este nodo
                    self.semaforo.acquire()
                    try:
                        print("email cliente especifico", m.destinoCliente)
                        cl = self.users.get(m.destinoCliente, None)
                        if(cl is not None):
                            print("email cliente localizado")
                            self.users[m.destinoCliente].box.append(m)
                    except: pass
                    finally: self.semaforo.release()
                else: # es otro nodo
                    self.ProcesarMensajes_nodos(m)


    # envia mensajes a los nodos que tienen acceso publico
    def EnviarMensajes(self):
        for n in self.peers:
            n1 = self.peers[n]
            if(n1.public):
                while (len(n1.box)>0):
                    if(self.Nodo_PasarMensaje(n1, n1.box[0])):
                        self.semaforo.acquire()
                        n1.box.pop(0)
                        self.semaforo.release()
                    else: break


    # ciclo de trabajo del nodo
    def Procesar(self):
        dtok = datetime.now() + timedelta(minutes = 10)
        dreg = datetime.now() + timedelta(seconds = 5)
        dver = datetime.now() + timedelta(minutes = 1)
        dbox = datetime.now() + timedelta(seconds = 10)
        dtmp = datetime.now() + timedelta(seconds = 15)
        dt = datetime.now()
        while (self.continuar):
            dt = datetime.now() # fecha actual
            if(dtok <= dt):
                self.Token_Limpieza() # borramos tokens viejos
                dtok = dt + timedelta(minutes = 10)
            if(dreg <= dt):
                self.RegistrarNodosNuevos() # registramos los nodos que tengamos pendientes
                dreg = dt + timedelta(minutes = 1)
            if(dver <= dt):
                self.VerificarNodos() # revisamos a cuales nodos podemos acceder directamente
                dver = dt + timedelta(minutes = 2)
            if(dbox <= dt):
                self.RecuperamosMensajes() # obtenemos los mensajes desde los servidores publicos
                dbox = dt + timedelta(seconds = 10)                            
            self.ProcesarMensajes() # procesamos los mensajes en la cola
            self.EnviarMensajes() # enviamos los mensajes a otros nodos
            time.sleep(1) # tiempo de espera antes de repetir el ciclo


    ######################################################################################################################
    # Evento inicializar nodo
    def Iniciar(self, nombre):
        try:
            print("Configuracion", "{}.cfg".format(nombre))
            self.nombreCfg = nombre
            self.cfg = Configuracion.file_create("{}.cfg".format(nombre))
            self.idnodo = self.cfg.id
            self.url = self.cfg.url
            self.port = self.cfg.puerto
            #self.peers = Peer.read_file("{}-p.txt".format(nombre))
            #if(self.peers is None): self.peers = {}
            #self.users = Client.read_file("{}-c.txt".format(nombre))
            #if(self.users is None): self.users = {}

            return True
        except Exception as e:
            print("Configuracion", "Hubo un error.", e)
            return False


    # Iniciar proceso de trabajo
    def Trabajar(self):
        self.continuar = True
        Thread(target=self.Procesar, name='trabajandito', daemon=True).start()


    # Finalizar proceso de trabajo
    def Finalizar(self):
        self.continuar = False
        Peer.save_file(self.peers, "{}-p.txt".format(self.nombreCfg))
        Client.save_file(self.users, "{}-c.txt".format(self.nombreCfg))
        pass #aqui guardaria la conf, los peers, los users


    # Crea un archivo de configuracion
    def CrearConf(self, nombre):
        try:
            print("Configuracion", "{}.cfg".format(nombre))
            c = Configuracion()
            c.nuevo_id()
            c.semillas.append(("127.0.0.1", 18002))
            c.semillas.append(("127.0.0.1", 18003))
            c.file_write("{}.cfg".format(nombre))
            return True
        except:
            print("Configuracion", "Hubo un error.")
            return False