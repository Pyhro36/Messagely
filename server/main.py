"""
Definit la boucle principale du serveur
"""

from select import select

import constants
from endpoint import Endpoint
    
class Service:
    """
    Definit l'hébergement de la boucle
    principale su serveur
    """
    
    def __init__(self, host, port):
        """
        Définit les services principaux
        de la boucle
        """
        
        self.__endpoint = Endpoint(host, port)
        self.__connections = []
        
    
    def accept_new_conn(self):
        """
        Vérifie si des nouvelles demandes
        de connexion on été faites et les
        ajoute
        """
           
        # Regarde si de nouveaux
        # clients se sont connectés
        # à chaque tour
        self.__connections += self.__endpoint.accept(ACCEPT_TIMEOUT)
     
    def select_conn(self, timeout=null):
    """
    Attends ou recupère les éventuels
    connexion prêtes à recevoir ou
    envoyer des messages
     
    Renvoie un tuple des connexions
    prêtes à recevoir et un tuple des
    connexions prêtes à envoyer
     
    timeout -- le temps d'attente
    maximal, si Nonr ou non défini, la
    méthode attends jusqu'à trouver
    un 
    """
     
        __ready_rconns, __ready_wconns, _ = select(self.__connections, self.__connections, [], RECV_SEND_TIMEOUT)
        
        for conn in ready_rconns:
            
            # Reçoit le message complet du
            # client
            conn.receive()
        
         # Confirme la réception des messages
         for client in ready_wclients:
             
            if client in clients_to_ack:
                 
                
                clients_to_ack.remove(client)
             
    print("Fermeture de la connexion")
    
    for client in clients:
    
        
        
if __name__ == "__main__":
    
    

## Initialisation des listes de gestion des clients

clients = []
clients_to_ack = []

## boucle principale de communication clients/serveur

