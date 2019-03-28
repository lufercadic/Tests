# coding: utf8
import io
import uuid
from base64 import b64encode, b64decode
#https://www.pycryptodome.org - Libreria Crypto
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from datetime import datetime
import random
import json


# clase con funciones de apoyo
class Utiles(object):
    # genera un codigo aleatorio
    @classmethod
    def generar_id(cls):
        return str(uuid.uuid4())

    # genera un codigo aleatorio de 6 caracteres
    @classmethod
    def generar_id6(cls):
        dt = datetime.now().strftime("%f, %m/%d/%Y, %H:%M:%S, %a")
        dt = SHA256.new(dt.encode('utf-8')).hexdigest()
        rd = random.randint(0,57)
        return dt[rd:(rd+6)]

    # genera un codigo aleatorio de 6 caracteres
    @classmethod
    def generar_id10(cls):
        dt = datetime.now().strftime("%f, %m/%d/%Y, %H:%M:%S, %a")
        dt = SHA256.new(dt.encode('utf-8')).hexdigest()
        rd = random.randint(0,53)
        return dt[rd:(rd+10)]

    ####################################################################################
    # almacena un texto en un archivo
    @classmethod
    def archivo_texto_guardar(cls, path, contenido):
        with open(path, mode='w', encoding='utf-8') as archivo:
            archivo.write(contenido)

    # lee el contenido de un archivo de texto
    @classmethod
    def archivo_texto_leer(cls, path):
        with open(path, mode='r', encoding='utf-8') as archivo:
            return archivo.read()

    ####################################################################################
    # encripta un vector de bytes
    @classmethod
    def aes_cifrar(cls, key, plainbytes):
        pkey = SHA256.new(key.encode('utf-8')).digest() # genero clave con los bit necesarios
        cipher = AES.new(pkey, AES.MODE_CFB)
        cipherbytes = cipher.encrypt(plainbytes)
        cipherbytes = cipher.iv + cipherbytes
        return cipherbytes

    # desencripta un vector de bytes
    @classmethod
    def aes_descifrar(cls, key, cipherbytes):
        pkey = SHA256.new(key.encode('utf-8')).digest() # genero clave con los bit necesarios
        cipher = AES.new(pkey, AES.MODE_CFB, iv=cipherbytes[:16])
        plainbytes = cipher.decrypt(cipherbytes[16:])
        return plainbytes

    # encripta una cadena de texto
    @classmethod
    def aes_cifrar_str(cls, key, plaintext):
        pkey = SHA256.new(key.encode('utf-8')).digest() # genero clave con los bit necesarios
        cipher = AES.new(pkey, AES.MODE_CFB)
        ciphertext = cipher.encrypt(plaintext.encode('utf-8'))
        ciphertext = cipher.iv + ciphertext
        return b64encode(ciphertext).decode('utf-8')

    # desencripta una cadena de texto
    @classmethod
    def aes_descifrar_str(cls, key, ciphertext):
        pkey = SHA256.new(key.encode('utf-8')).digest() # genero clave con los bit necesarios
        ciphertext = b64decode(ciphertext)
        cipher = AES.new(pkey, AES.MODE_CFB, iv=ciphertext[:16])
        plaintext = cipher.decrypt(ciphertext[16:])
        return plaintext.decode('utf-8')

    ####################################################################################
    # genera el par de claves necesarias para la encriptacion RSA
    @classmethod
    def rsa_generar_clave(cls):
        key = RSA.generate(2048)
        return dict(zip(['type', 'public_key', 'private_key'],
                        ['RSA', key.publickey().export_key(), key.export_key()]))

    # cifra un vector de bytes usando el algoritmo de RSA
    @classmethod
    def rsa_cifrar(cls, publickey, plainbytes):
        publickey = RSA.import_key(publickey)
        cipher_rsa = PKCS1_OAEP.new(publickey)
        return cipher_rsa.encrypt(plainbytes)

    # descifra un vector de bytes usando el algoritmo de RSA
    @classmethod
    def rsa_descifrar(cls, privatekey, cipherbytes):
        privatekey = RSA.import_key(privatekey)
        #privatekey.size_in_bytes()
        cipher_rsa = PKCS1_OAEP.new(privatekey)
        return cipher_rsa.decrypt(cipherbytes)

    # cifra una cadena de texto usando el algoritmo de RSA
    @classmethod
    def rsa_cifrar_str(cls, publickey, plaintext):
        r = cls.rsa_cifrar(publickey, plaintext.encode('utf-8'))
        return b64encode(r).decode('utf-8')

    # descifra una cadena de texto usando el algoritmo de RSA
    @classmethod
    def rsa_descifrar_str(cls, privatekey, ciphertext):
        r = cls.rsa_descifrar(privatekey, b64decode(ciphertext))
        return r.decode('utf-8')

    ####################################################################################
    # Calcula el SHA256 para una cadena de texto
    @classmethod
    def sha256_generar_str(cls, str):
        return SHA256.new(str.encode('utf-8')).hexdigest()

    # Calcula el SHA256 para un vector
    @classmethod
    def sha256_generar(cls, data):
        return SHA256.new(data).digest()

    ####################################################################################
    # Convierte una cadena en Base64 a bytes
    @classmethod
    def b64_decode(cls, b64string):
        return b64decode(b64string)

    # Convierte un vector de bytes a una cadena Base64
    @classmethod
    def b64_encode(cls, databytes):
        return b64encode(databytes).decode('utf-8')
    
    ####################################################################################
    # Convierte un objeto a una cadena json
    @classmethod
    def json_decode(cls, jsonstr):
        return json.loads(jsonstr)

    # Convierte una cadena json a un objeto
    @classmethod
    def json_encode(cls, data):
        return json.dumps(data)