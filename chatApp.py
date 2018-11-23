#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import pyaes
import base64

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        key = bytes("This_key_for_demo_purposes_only!","utf8")
        msg = "Greetings from the cave! Now type your name and press enter!"
        aes = pyaes.AESModeOfOperationCTR(key)
        t = aes.encrypt(msg)
        client.send(base64.b64encode(t))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    name = client.recv(BUFSIZ)
    key = bytes("This_key_for_demo_purposes_only!","utf8")
    aes = pyaes.AESModeOfOperationCTR(key)
    t = base64.b64decode(name)
    plain = aes.decrypt(t)
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % plain.decode('utf8')
    aes = pyaes.AESModeOfOperationCTR(key)
    t = aes.encrypt(welcome)
    cipher = base64.b64encode(t)
    client.send(cipher)
    msg = "%s has joined the chat!" % plain.decode('utf8')
    aes = pyaes.AESModeOfOperationCTR(key)
    cipher = aes.encrypt(msg)
    t = base64.b64encode(cipher)
    broadcast(t)
    clients[client] = plain.decode('utf8')

    while True:
        msg = client.recv(BUFSIZ)
        aes = pyaes.AESModeOfOperationCTR(key)
        t = base64.b64decode(msg)
        plaintext = aes.decrypt(t)
        if plaintext == bytes("{file}", "utf8"):
            data = client.recv(BUFSIZ)
            t = base64.b64decode(data)
            myfile = open(t.decode('utf8'), 'w')
            data = client.recv(BUFSIZ)
            t = base64.b64decode(data)
            print(t)
            myfile.write(t.decode('utf8'))
            print('writing file ....')
            myfile.close()
            print('finished writing file')
        elif plaintext != bytes("{quit}", "utf8"):
            t = "%s: %s" % (plain.decode('utf8'),plaintext.decode('utf8'))
            aes = pyaes.AESModeOfOperationCTR(key)
            cipher = aes.encrypt(t)
            t = base64.b64encode(cipher)
            broadcast(t)
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            msg = "%s has left the chat." % plain.decode('utf8')
            aes = pyaes.AESModeOfOperationCTR(key)
            cipher = aes.encrypt(msg)
            t = base64.b64encode(cipher)
            broadcast(t)
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(msg)

        
clients = {}
addresses = {}

HOST = ''
PORT = int(input('Enter Port:'))
BUFSIZ = 4096
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
SERVER.close()
