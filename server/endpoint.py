"""
Low-level endpoint of the application, which
define the server which the client can connect to
and communicate with
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
        Constructor, creates and starts the
        server
        """
        
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind((host, port))
        self.__sock.listen(wait_conn_max)
        print("Un serveur écoute à présent sur {}:{}".format(host, port))
        
    def accept(self, timeout=None):
        """
        Wait for one or several clients
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
        
            # Connect client(s)
            for s_s in server_socks:
                c_s, (host, port) = s_s.accept()
                yield Connection(c_s, host, port)
            
            server_socks, _, _ = select([self.__sock], [], [], 0)
    
    def close(self):
        """
        Close properly the server
        """
        
        self.__sock.shutdown(2)
        self.__sock.close()
        
    
class Connection:
    """
    Define a connection to a client wich listen
    to messages coming from the client and which
    can send it messages too
    """
    
    def __init__(self, sock, host, port):
        """
        Constructor which defines attributes of
        connection
        """
        
        self.__sock = sock
        self.__host = host
        self.__port = port
        
        print(f"Le client {host}:{port} vient de se connecter")
        
    def receive(self):
        """
        Wait for a message from the client in
        order to return it
        
        The call is blocking until receiving
        a message

        Return None if the connection is
        interrupted
        """
        
        msg = ""
        
        while not msg.endswith("\3"):
            recept = self.__sock.recv(1024)
            
            # If the connection is interrupted
            if recept == b"":
                return None
            
            msg += recept.decode()
        
        # Remove the control character
        return msg[:-1]
        
    def send(self, msg):
        """
        Send a message to the client
        
        msg (str) --- the message to send
        
        Return True if the message has been
        correctly send, False if the connection
        is interrupted
        """
        
        # Add end of message character
        msg += "\3"
        sent = self.__sock.send(msg.encode())
        
        return sent != 0
        
    def fileno(self):
        """
        Return un fileno which in order the
        function select.select(...)
        to identifies the connection when it can
        send a message or when she has a message
        to receive
        """
        
        return self.__sock.fileno()
     
    def close(self):
        """
        Close properly the connection with the
        client
        """
        self.__sock.shutdown(2)
        self.__sock.close()
        

if __name__ == "__main__":
    # Do a test by making a naive server wich
    # accepts a connection, sends a message and
    # receives another, then closes the
    # connection
        
    # Test of killing client socket while active
    
    print("client accept")
    servers, _, _ = select([server], [], [], 0)
    client_msg = servers[0].receive()
    
    if client_msg != "Bonjour du client !!":
        print(f"Erreur : le message reçu par le serveur est :\n{client_msg}")
    else:
        print("Ok : client -> serveur")
    
    client_alive = False
    client_thread.join()
    print(server.send("Un message irrecevable"))
    
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

    