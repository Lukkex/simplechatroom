'''
server.py (port number):
    Start on specified port, TCP socket
    When connects to client, create new thread to handle (POSIX)
    If >10 users registered, send to client “Too many users!” and close connection
    If already registered, discard new JOIN requests and send status back to client
    If command sent that the server doesn’t recognize, send to client “Unknown Command”
    Server will provide updates in terminal on messages sent/received, requests, ID clients by IP and port #
    Show to all clients who joins chatroom and who leaves
    Error checking is thorough

Client.py (hostname) (port number):
    Connect to server on specified port
    JOIN (username) – (15 points)
        Sends JOIN request w/ alphanumeric username, no spaces / special chars
        Username validation not needed
        NO other services provided unless registered through JOIN
    LIST – (15 points)
        Server will send list of all currently registered clients on individual lines (\n’s)
    MESG (username) (message) – (15 points)
        Messages user using server as a relay in between
        If user sending message isn’t registered, have server send status saying they’re not registered and to join w/ JOIN instructions
        If receiving end user is not registered, send to client “Unknown recipient”
    BCST (message) – (15 points)
        If client is registered, broadcast this message to all other users (not the sender)
    QUIT – (10 points)
        Client disconnects and server removes them from the database of registered users; unregistered users can do this too but it won’t remove any data
'''
# Hunter Brown, Connor Yep, William Lorence
# Prof. Badruddoja 
# CSC 138-04
# 17 Apr. 2024

from socket import *
import random
import sys
import errno
import threading

# Fixed size of 10; if all slots are filled, do not allow new clients to register
userRegistry = []

def setRegistry(newReg):
    userRegistry = newReg

# Will return true if member successfully added to registry
# Will return false if member cannot join (list is full)
def join(clientSocket, clientAddress, username):
    try:
        if (len(userRegistry) <= 10):
            userRegistry.append((clientSocket, (clientAddress, username)))
            return True
        return False
    except Exception as e:
        print("Error: " + str(e))

# Will return true if member is within the registry
# Will return false if member is not in the registry
def checkIfMember(clientAddress):
    try:
        if (len(userRegistry) > 0):
            # Separates tuple into list of all addresses and usernames
            regSockets, userTuples = zip(*userRegistry)
            regAddresses, regUsernames = zip(*userTuples)

            for i in regAddresses:
                if (i == clientAddress):
                    return True
            return False
        else:
            return False
    except Exception as e:
        print("Error: " + str(e)) 

def regToString(list):
    regSockets, userTuples = zip(*list)
    return ',\n'.join(map(str, userTuples))

# Handles how to dispatch types of messages
def serverMessageHandler(targSocket, message, type):
    try:
        if (len(userRegistry) > 0):
            # Separates tuple into list of all addresses and usernames
            regSockets, userTuples = zip(*userRegistry)
            # for broadcasts - sender
            if(type == 0):
                for socket in regSockets:
                    if (socket != targSocket):
                        socket.send(message.encode())
            # for broadcasts (everyone)
            if(type == 1):
                for socket in regSockets:
                    socket.send(message.encode())
            # for direct messages
            if(type == 2):
                for socket in regSockets:
                    if (socket == targSocket):
                        socket.send(message.encode())
            return True
        else:
            return False


    except Exception as e:
        print("Error: " + str(e))

# returns tuple of user (not functional, wont run first line when called)
'''
def getUserTuple(clientSocket):
    try:
        if (len(userRegistry) > 0):
            print('tuple 0')
            # Separates tuple into list of all addresses and usernames
            regSockets, userTuples = zip(*userRegistry)
            i = 0
            print('tuple 1')
            for socket in regSockets:
                if (socket == clientSocket):
                    return userRegistry[i]
                i += 1

    except Exception as e:
        print("Error: " + str(e))
    
    return None
'''

# returns name of user (not functional, wont run first line when called)
'''
def getUsername(clientSocket):
    print('wtf')
    try:
        if (len(userRegistry) > 0):
            i = 0
            for users in userRegistry:
                if (userRegistry[i][0] == clientSocket):
                    return userRegistry[i][1][1]
                i += 1

    except Exception as e:
        print("Error: " + str(e))
    
    return None
'''

# Removes user from registry
def removeUser(clientSocket):
    try:
        if (len(userRegistry) > 0):
            # Separates tuple into list of all addresses and usernames
            
            try:
                if (len(userRegistry) > 0):
                    # Separates tuple into list of all addresses and usernames
                    regSockets, userTuples = zip(*userRegistry)
                    i = 0
                    for socket in regSockets:
                        if (socket == clientSocket):
                            clientTuple = userRegistry[i]
                        i += 1

            except Exception as e:
                print("Error: " + str(e))
            
            userRegistry.remove(clientTuple)
            # setRegistry(newReg)
            print('Removed user from list!')
            return True
        else:
            return False

    except Exception as e:
        print("Error: " + str(e))
    
def handleClientConnection(clientSocket, clientAddress):
    while True:
        try:
            clientSocket.settimeout(300)
            data = clientSocket.recv(1024).decode('utf-8')

            if data:
                print('Received from ' + str(clientAddress) + ': ' + data)

                # Splits data/command by spaces
                data_tokens = data.split()

                # JOIN COMMAND
                if (data_tokens[0] == 'JOIN'):
                    if (len(data_tokens) == 2):
                        # Makes sure client isn't already a member
                        if (checkIfMember(clientAddress)):
                            clientSocket.send('You\'re already a member!'.encode())
                        # Assumes username is alphanumeric
                        # Checks if there is room for user to join
                        elif (join(clientSocket, clientAddress, data_tokens[1])):
                            clientSocket.send('Successfully joined! Enjoy!'.encode())
                            print(str(data_tokens[1] + " joined!"))
                            serverMessageHandler(clientSocket, str(data_tokens[1]) + ' joined!', 0)
                        else:
                            clientSocket.send('Too many users in registry, try again later!'.encode())
                        
                    else:
                        clientSocket.send('Invalid number of arguments for JOIN.\n\nTry: \'JOIN <username>\''.encode())
                
                # LIST COMMAND
                elif (data_tokens[0] == 'LIST'):
                    if (checkIfMember(clientAddress)):
                        userList = str(regToString(userRegistry))
                        clientSocket.send(userList.encode())
                        print('Sent list!')
                    else:
                        clientSocket.send('You\'re not registered yet!'.encode())
                
                # BCST COMMAND
                elif(data_tokens[0] == 'BCST'):
                    # removes fluff at beginning of message
                    data_tokens.remove(data_tokens[0])
                    broadcastmsg = ' '.join(data_tokens)
                    # gets username of current socket
                    try:
                        if (len(userRegistry) > 0):
                            i = 0
                            for users in userRegistry:
                                if (userRegistry[i][0] == clientSocket):
                                    userName = userRegistry[i][1][1]
                                i += 1
                    except Exception as e:
                        print("Error: " + str(e))

                    clientSocket.send((str(userName) + ' is sending a broadcast\n').encode())
                    serverMessageHandler(clientSocket, str(userName) + ': ' + str(broadcastmsg), 1)
                
                # MESG COMMAND
                elif(data_tokens[0] == 'MESG'):
                    # removes fluff at beginning of message while storing target
                    target = data_tokens[1]
                    data_tokens.remove(data_tokens[1])
                    data_tokens.remove(data_tokens[0])
                    message = ' '.join(data_tokens)
                    # gets username of current socket, and then sends message to target socket
                    try:
                        if (len(userRegistry) > 0):
                            i = 0
                            j = 0
                            for users in userRegistry:
                                if (userRegistry[i][0] == clientSocket):
                                    userName = userRegistry[i][1][1]
                                i += 1
                            for users in userRegistry:
                                if (userRegistry[j][1][1] == target):
                                    serverMessageHandler(userRegistry[j][0], str(userName) + '(private): ' + str(message), 2)
                                j += 1
                    except Exception as e:
                        print("Error: " + str(e))

                # QUIT COMMAND
                elif (data_tokens[0] == 'QUIT'):
                    clientSocket.send('QUIT'.encode())
                    clientSocket.close()
                    removeUser(clientSocket)
                    return
                
                # Otherwise
                else:
                    clientSocket.send('\nInvalid command.\n\nPlease use one of the following:\nJOIN <username>\nLIST\nMESG <recipient> <message>\nBCST <message>\nQUIT\n\n'.encode())
                #clientSocket.send('PONG!'.encode())
        
        except timeout:
            print("Connection with " + str(clientAddress) + " timed out.")
            break

        except Exception as e:
            pass

        '''
        except IOError as e:
            if e.errno == errno.EPIPE:
                print("Pipe Error: " + str(e))
        '''
    
    try:
        clientSocket.send('Connection timed out, please rejoin. \n(You took too long to send another message!)'.encode())
        clientSocket.close()
    except Exception as e:
        pass
    removeUser(clientSocket)
       
# If the amount of arguments is anything other than 2, 
# it will say in the console an invalid number of args and  kill the process.
if (len(sys.argv) != 2):
    print('Invalid number of arguments.')
    quit()

# Takes in the server port and creates a TCP socket on the server end
serverPort = sys.argv[1]
serverSocket = socket(AF_INET, SOCK_STREAM)
host = '0.0.0.0'
serverSocket.bind((host, int(serverPort)))
serverSocket.listen(5)

# Once the socket is setup, the server prints that it is ready to receive messages
print(f'The server is ready! \nListening on {host}:{serverPort}')

# Loop that continues until terminated manually, continuously listens for any incoming connection requests from clients. 
while True:
    try:
        clientSocket, clientAddress = serverSocket.accept()
        print(f'Connection from {clientAddress}')
        t = threading.Thread(target=handleClientConnection, args=(clientSocket, clientAddress,))
        t.start()
    except Exception as e:
        print("Error: " + str(e))
serverSocket.close()
    
