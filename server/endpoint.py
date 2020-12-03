"""
Module de serveur de l'application
"""

import socket

from select import select

class Endpoint:
    """
    Define a server which listen to new clients
    and open connections
    """
    
    def __init__(self, host, port, wait_conn_max=5):
        """
        Constructor, create and start the server
        """
        
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind((host, port))
        self.__sock.listen(wait_conn_max)
        print("Un serveur écoute à présent sur {}:{}".format(host, port))
        
    def accept(self, timeout=None):
        """
        Waits for one or several clients
        requesting to connect, open and return
        a list of new connections.
        
        timeout -- the time in sec of waiting
        before return without creating any
        connection because no client came out.
        If None or undefined, waits forever at
        least one client, if equals 0, does not
        wait and return directly if no client
        """
        
        #Client/server synchronization
        server_socks, _, _ = select([self.__sock], [], [], timeout)
        
        while server_socks:
        
            # Connects client(s)
            for s_s in server_socks:
                c_s, (host, port) = s_s.accept()
                yield Connection(c_s, host, port)
            
            server_socks, _, _ = select([self.__sock], [], [], timeout)
    
    def close(self):
        """
        Closes properly the server
        """
        
        self.__sock.shutdown(2)
        self.__sock.close()
        
    
class Connection:
    """
    Defines a connection to a client wich listen
    to messages coming from the client and which
    can send it messages too
    """
    
    def __init__(self, sock, host, port):
        """
        Constructor which define attributes of
        connection
        """
        
        self.__sock = sock
        self.__host = host
        self.__port = port
        
        print(f"Le client {host}:{port} vient de se connecter")
        
    def receive(self):
        """
        Waits for a message from the 
        Attend un message du client pour
        le renvoyer
        
        L'appel est bloquant jusqu'à la
        réception d'un message
        
        Renvoie None si la connexion a
        été interrompue
        
        """
        
        msg = ""
        
        while not msg.endswith("\3"):
            recept = self.__sock.recv(1024)
            
            # Si la connexion a été
            # interrompue
            if recept == b"":
                return None
            
            msg += recept.decode()
        
        # On retire le caractère de
        # contrôle
        return msg[:-1]
        
    def send(self, msg):
        """
        Envoie un message au client
        
        msg --- le message a envoyer
        (string)
        
        Renvoie True si le message a bien
        été envoyé, False si la connexion
        a été interrompue
        """
        
        # Ajout du caractère de fin de
        # message
        msg += "\3"
        sent = self.__sock.send(msg.encode())
        
        return sent != 0
        
    def fileno(self):
        """
        Renvoie un numéro de fichier
        permettant d'identifier la
        connexion avec la fonction
        select.select(...) comme ayant un
        message à recevoir
        """
        
        return self.__sock.fileno()
     
    def close(self):
        """
        Ferme proprement la connexion avec
        le client
        """
        self.__sock.shutdown(2)
        self.__sock.close()
        

if __name__ == "__main__":
    # Fait un test en fabriquant un
    # serveur naîf qui accepte une
    # connexion,envoie un message et en
    # reçois un, puis ferme la connexion
    
    import time
    
    endpoint = Endpoint('localhost', 12480)
    client = socket.create_connection(('localhost', 12480))
    server = list(endpoint.accept())[0]
    
    client.send(b"Bonjour du client !!\3")
    time.sleep(1)
    servers, _, _ = select([server], [], [], 0)
    client_msg = servers[0].receive()
    
    if client_msg != "Bonjour du client !!":
        print(f"Erreur : le message reçu par le serveur est :\n{client_msg}")
    else:
        print("Ok : client -> serveur")
    
    _, servers, _ = select([], [server], [])
    servers[0].send("Bonjour du client !")
    server_msg = client.recv(1024)
    
    if server_msg != b"Bonjour du client !\3":
        print(f"Erreur : le message reçu par le client est :\n{server_msg}")
    else:
        print("Ok : serveur -> client")
       
    try:
        server.close()
    except socket.error as error:
        print(f"Erreur : fermeture de la connexion :\n{error}")
    else:
        print("Ok : fermeture de la connexion")
        
    # Test de kill du socket en cours
    from threading import Thread
    
    def client_run(is_alive):
        """
        Routine de fonctionnement du client en
        parallèle
        """
        clt = socket.create_connection(('localhost', 12480))
        clt.send(b"Bonjour du client !!\3")
        
        while is_alive():
            time.sleep(.2)
    
    #pylint:disable=C0103
    client_alive = True
    client_thread = Thread(target=client_run, args=(lambda: client_alive, ))
    client_thread.start()
    print("client run")
    time.sleep(.5)
    server = list(endpoint.accept())[0]
    print("client accept")
    servers, _, _ = select([server], [], [], 0)
    client_msg = servers[0].receive()
    
    if client_msg != "Bonjour du client !!":
        print(f"Erreur : le message reçu par le serveur est :\n{client_msg}")
    else:
        print("Ok : client -> serveur")
    
    client_alive = False
    client_thread.join()
    
    servers, _, _ = select([server], [], [], 0)
    client_msg = servers[0].receive()
    
    if client_msg is not None:
        print(f"Erreur : le message reçu par le serveur est :\n{client_msg}")
    else:
        print("Ok : client -> serveur")
    
    try:
        server.close()
    except socket.error as error:
        print(f"Erreur : fermeture de la connexion :\n{error}")
    else:
        print("Ok : fermeture de la connexion")
    
    try:
        endpoint.close()
    except socket.error as error:
        print(f"Erreur : fermeture de l'endpoint :\n{error}")
    else:
        print("Ok : fermeture de l'endpoint")
    
    

    