"""
Define the components of the service of message redistribution
"""

from select import select

import constants
from endpoint import Endpoint
    
class Service:
    """
    Define'' the service of message redistribution
    """
    
    def __init__(self, host, port):
        """
        Define the main components useful for the
        loop
        """
        
        self.__endpoint = Endpoint(host, port)
        self.__connections = []
        self.__pendings = []
    
    def accept_new_conn(self):
        """
        Check if new connection requests have
        been made and add these
        """

        self.__connections += self.__endpoint.accept(constants.ACCEPT_TIMEOUT)
     
    def turn_messages(self):
        """
        Wait for or gather the connections which
        are ready to send or receive messages
        Attends ou recupère les éventuels
        
        If there are ones, close and delete upon
        detection terminated connections
        
        Save each received message to send it to
        all clients, send each message to the
        ready to receive clients that have not
        already received the message and delete
        messages sent to all clients.
        """
         
        ready_rconns, ready_wconns, _ = select(self.__connections, self.__connections, [], constants.RECV_SEND_TIMEOUT)
            
        for conn in ready_rconns:

            # Receive the complete client message
            msg = conn.receive()

            if msg:
                self.__pendings.append(PendingMessage(msg, self.__connections))
                
            else:
                conn.close()
                self.__connections.remove(conn)
        
        self.__send_pendings(ready_wconns)
                
    def close(self):
        """
        Close properly the server and all the
        connection still open
        
        Send the last saved messages but don't
        receive anymore
        """
        
        while self.__pendings:
            _, ready_wconns, _ = select([], self.__connections, [], constants.RECV_SEND_TIMEOUT)
            self.__send_pendings(ready_wconns)
            
        for conn in self.__connections:
            conn.close()
        
        self.__endpoint.close()
        
        
    def __send_pendings(self, conns):
        """
        Send pending messages to the clients
        that can receive them
        
        conns (iterable[Connection])--- the
        connections to the clients that can
        receive a message
        """
        done_pendings = []
        
        for pending in self.__pendings:
            
            # Remove connexions that couldn't
            # send the message
            for conn in pending.send(conns):
                conn.close()
                self.__connections.remove(conn)
                
            if pending.is_done():
                done_pendings.append(pending)
            
        # Remove the messages sent to all clients
        for pending in done_pendings:
            self.__pendings.remove(pending)
        

class PendingMessage:
    """
    Define a message pending to be sent to all
    the clients and allow to follow to which
    clients the message is not sent yet
    """
    
    def __init__(self, msg, connections):
        """
        Initialize the waiting
        
        msg (str) -- the message to send to the
        clients
        connections (iterable[Connection]) -- all
        the connections to the client
        """
        
        self.__msg = msg
        self.__connections = list(connections)
        
    def send(self, connections):
        """
        Send the message by the connections given
        in parameters, that are ready to send a
        message and in the connections that don't
        have sent the messsage yet
        
        Return the connections by which the
        message could not be send, because
        interrupted
        """
        
        for conn in connections:
            
            if conn in self.__connections:
                
                if not conn.send(self.__msg):
                    yield conn
                
                self.__connections.remove(conn)
    
    def is_done(self):
        """
        Return True if all the active connections
        have sent the message, False otherwise.
        """
        
        return not self.__connections
        
if __name__ == "__main__":
    # Create a server and two client in separated
    # threads that send mutually a message by the
    # server
    #
    # Then one client interrupt suddenly while
    # the other send a message
    #
    # Eventually, the server is closed

    import socket
    import time
    from threading import Thread

    service = Service('', 12480)

    def run_client1():
        """
        Execution routine of the first client
        """
        
        client = socket.create_connection(('localhost', 12480))
        client.send(b"Msg du client 1 !\3")
        print(f"1 -> 1 : {client.recv(1024)}")
        # print(f"2 -> 1 : {client.recv(1024)}")
        client.close()
        
    def run_client2():
        """
        Execution routine of the second client
        """
        
        client = socket.create_connection(('localhost', 12480))
        print(f"1 -> 2 : {client.recv(1024)}")
        client.send(b"Msg du client 2 !\3")
        print(f"2 -> 2 : {client.recv(1024)}")
        client.close()
        
    client1_thread = Thread(target=run_client1)
    client2_thread = Thread(target=run_client2)
    client1_thread.start()
    client2_thread.start()
    service.accept_new_conn()
    
    
    service.turn_messages()
    time.sleep(.1)
    service.turn_messages()
    time.sleep(.1)
    service.turn_messages()

    client2_thread.join()
    client1_thread.join()
    
    
    
    