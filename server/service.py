#pylint:disable=C0301
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
        self.__waits = []
    
    def accept_new_conn(self):
        """
        Vérifie si des nouvelles demandes
        de connexion on été faites et les
        ajoute
        """
           
        # Regarde si de nouveaux
        # clients se sont connectés
        # à chaque tour
        self.__connections += self.__endpoint.accept(constants.ACCEPT_TIMEOUT)
     
    def select_conn(self):
        """
        Attends ou recupère les éventuels
        connexion prêtes à recevoir ou
        envoyer des messages
        
        Le cas échéant, ferme et supprime
        automatiquement les connexions
        terminées
         
        Renvoie un tuple des connexions
        prêtes à recevoir et un tuple des
        connexions prêtes à envoyer
         
        timeout -- le temps d'attente
        maximal, si Nonr ou non défini, la
        méthode attends jusqu'à trouver
        un
        """
         
        ready_rconns, ready_wconns, _ = select(self.__connections, self.__connections, [], constants.RECV_SEND_TIMEOUT)
            
        for conn in ready_rconns:
                
            # Reçoit le message complet du
            # client
            msg = conn.receive()
            
            if msg:
                self.__waits += WaitingMessage(msg, self.__connections)
                
            else:
                conn.close()
                self.__connections.remove(conn)
        
        self.__send_waits(ready_wconns)
                
    def close(self):
        """
        Ferme le serveur et toutes les
        connexions encore ouvertes
        proprement
        
        Envoie les derniers messages encore en
        cours mais n'en rençois plus
        """
        
        while self.__waits:
            _, ready_wconns, _ = select([], self.__connections, [], constants.RECV_SEND_TIMEOUT)
            self.__send_waits(ready_wconns)
            
        for conn in self.__connections:
            conn.close()
        
        self.__endpoint.close()
        
        
    def __send_waits(self, conns):
        
        # Envoie les messages en attente
        # aux clients qui peuvent en
        # recevoir
        done_waits = []
        
        for wait in self.__waits:
            
            # Retire les connexions qui n'ont pas
            # pu recevoir le message
            for conn in wait.send(conns):
                conn.close()
                self.__connections.remove(conn)
                
            if wait.is_done():
                done_waits += wait
            
        # Retire les messages envoyés à
        # tous les clients
        for wait in done_waits:
             
            self.__waits.remove(wait)
        

class WaitingMessage:
    """
    Représente un message en attente
    d'envoi à tous les clients et permet
    de suivre à quels clients il faut
    encore l'envoyer
    """
    
    def __init__(self, msg, connections):
        """
        Initialise l'attente
        
        msg -- le message à envoyer aux
        clients
        connections -- la séquence des
        connections aux clients
        """
        
        self.__msg = msg
        self.__connections = list(connections)
        
    def send(self, connections):
        """
        Envoie le message aux connexions
        dans la séquence de connexions
        prêtes à envoyer le message au
        client passée en paramètre qui
        n'ont pas encore envoyé le message
        et les retire de liste des
        connexions qui doivent encore
        envoyer le message.
        
        Renvoie la liste des connexions
        à qui le message n'a pas pu être
        envoyé
        """
        
        for conn in connections:
            
            if conn in self.__connections:
                
                if not conn.send(self.__msg):
                    yield conn
                
                self.__connections.remove(conn)
    
    def is_done(self):
        """
        Renvoie True si toutes les
        connexions ont reçu le message,
        False sinon.
        """
        
        return not self.__connections
        
if __name__ == "__main__":
    # Initie un serveur et deux clients qui
    # s'envoient mutuellement un message
    #
    # Puis un client se ferme brusquement
    # pendant que l'autre envoie un message
    #
    # Et enfin le serveur est fermé

    import socket
    from threading import Thread

    service = Service('', 12480)
    client1 = socket.create_connection(('localhost', 12480))
    
    client2_alive = True
    def run_client2(client2):
        """
        Routine d'éxecution du deuxième client
        """
        
        client2 = socket.create_connection(('localhost', 12480))
        
    client2_thread = Thread(target=run_client2, args=(lambda : client2_alive, ))
    client2_thread.start()
        
    service.accept_new_conn()
    