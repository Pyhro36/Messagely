"""
Module de serveur de l'application
"""

import socket

from select import select

class Endpoint:
    """
    Représente le serveur qui écoute et
    ouvre les connexions
    """
    
    def __init__(self, host, port, wait_conn_max=5):
        """
        Constructeur, crée et démarre le
        serveur
        """
        
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind((host, port))
        self.__sock.listen(wait_conn_max)
        print("Un serveur écoute à présent sur {}:{}".format(host, port))
        
    def accept(self, timeout=None):
        """
        Attend qu'un ou plusieurs clients
        aient demandé à se connecter et
        ouvre et renvoie la liste des
        connexions correspondantes
        
        timeout -- le temps en secondes
        d'attente avant de rendre la main
        sans créer de conexion si aucun
        client ne s'est présenté. Si None
        ou non défini, attend
        indéfiniment un client, si vaut 0
        n'attend pas et retourne
        directement si pas de clients
        """
        
        # Synchronisation clients/serveur
        server_socks, _, _ = select([self.__sock], [], [], timeout)
        
        while server_socks:
        
            # Connecte le(s) client(s)
            for ss in server_socks:
                cs, (host, port) = ss.accept()
                yield Connection(cs, host, port)
            
            server_socks, _, _ = select([self.__sock], [], [], timeout)
    
    def close(self):
        """
        Ferme proprement le serveur
        """
        
        self.__sock.shutdown(2)
        self.__sock.close()
        
    
class Connection:
    """
    Représente une connexion à un client
    qui écoute les messages du client
    et peut lui envoyer des messages
    """
    
    def __init__(self, sock, host, port):
        """
        Constructeur qui définit les
        attributs de la connection
        """
        
        self.__sock = sock
        self.__host = host
        self.__port = port
        
        print(f"Le client {host}:{port} vient de se connecter")
        
    def receive(self):
        """
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
    except Error as error:    
        print(f"Erreur : fermeture de la connexion :\n{error}")
    else:
        print("Ok : fermeture de la connexion")
        
    # Test de kill du socket en cours
    from threading import Thread
    
    def client_run(is_alive):
        client = socket.create_connection(('localhost', 12480))
        client.send(b"Bonjour du client !!\3")
        
        while is_alive():
            time.sleep(.2)

    client_alive = True
    client_thread = Thread(target=client_run, args=(lambda : client_alive, ))
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
    
    if client_msg != None:
        print(f"Erreur : le message reçu par le serveur est :\n{client_msg}")
    else:
        print("Ok : client -> serveur")
    
    try:
        server.close()    
    except Error as error:    
        print(f"Erreur : fermeture de la connexion :\n{error}")
    else:    
        print("Ok : fermeture de la connexion")
    
    try:
        endpoint.close()
    except Error as error:
        print(f"Erreur : fermeture de l'endpoint :\n{error}")
    else:
        print("Ok : fermeture de l'endpoint")
    
    

    