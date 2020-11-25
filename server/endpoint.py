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
        server_socks, _, _ = select([self.__soc], [], [], timeout())
    
        # Connecte le(s) client(s)
        for ss in server_socks
        
            cs, (host, port) = ss.accept()
            
            yield Connection(cs, host, port)
    
    def close(self):
        """
        Ferme proprement le serveur
        """
        
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
        
    def recieve(self):
        """
        Attend un message du client pour
        le renvoyer
        
        L'appel est bloquant jusqu'à la
        réception d'un message
        
        """
        
        msg = ""
        
        while not msg.endswith("\3"):
            
            recept = client.recv(1024)
            msg += recept.decode()
        
        # On retire le caractère de
        # contrôle
        return msg[:-1]
        
    def send(msg):
        """
        Envoie un message au client
        
        msg --- le message a envoyer
        (string)
        """
        
        # Ajout du caractère de fin de
        # message
        msg += "\3"
        
        self.__sock.send(msg.encode())
        
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
        
        self.__sock.close()
        


    
       
