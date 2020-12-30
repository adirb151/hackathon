from socket import *
from struct import *
import time
import threading

host = 'localhost' #localhost because our ip 172.1.0.62 doesn't work on the server
serverUDPPort = 13117
serverTCPPort = 8000

def acceptTcpConn(cv):
    global i
    while not isDoneBroadcasting:
        try:
            connectionSocket, addr = serverSocket.accept() #accept connections and assign them to groups
            try:
                teamName = connectionSocket.recv(1024).decode('utf-8')
            except:
                continue
            if i:
                group1[teamName] = 0
            else:
                group2[teamName] = 0
            i = not i
            threading.Thread(target=openTcpConn, args=(cv, connectionSocket, teamName,)).start() #start game thread
        except:
            break


def openTcpConn(cv, connectionSocket, teamName):
    cv.acquire()
    while not isDoneBroadcasting: #wait for server to finish broadcasting
        cv.wait()
    cv.release()
    counter = 0
    keys1 = group1.keys()
    keys2 = group2.keys()
    try:
        connectionSocket.send(bytes(
        """Welcome to Keyboard Spamming Battle Royale.
    Group 1:
    ==\n""" + 
    ''.join(list(keys1))
    + """
    Group 2:
    ==\n""" +
    ''.join(list(keys2))
    +
    """\nStart pressing keys on your keyboard as fast as you can!!""",
            'utf-8'))
    except:
        print('Could not send welcome message')
    timeout = time.time() + 10
    while time.time() < timeout:
        connectionSocket.settimeout(timeout - time.time())
        try:
            connectionSocket.recv(1024)
        except:
            break
        counter = counter + 1               #when receiving chars, increment and update value
        if teamName in group1:
            group1.update({teamName : counter})
        else:
            group2.update({teamName : counter})
    score1 = sum(list(group1.values()))
    score2 = sum(list(group2.values()))
    if score1 > score2:
        connectionSocket.send(bytes(
            """Game Over!
Group 1 typed in """ + str(score1) + """ characters. Group 2 typed in """ + str(score2) + """ characters.
Group 1 wins!\n
Congratulations to the winners:
==\n""" + ''.join(list(group1.keys()))
                , 'utf-8'))
    elif score1 < score2: 
        connectionSocket.send(bytes(
            """Game Over!
Group 1 typed in """ + str(score1) + """ characters. Group 2 typed in """ + str(score2) + """ characters.
Group 2 wins!\n
Congratulations to the winners:
==\n""" + ''.join(list(group2.keys()))
                , 'utf-8'))
    else:
        connectionSocket.send(bytes(
            """Game Over!
Group 1 typed in """ + str(score1) + """ characters. Group 2 typed in """ + str(score2) + """ characters.
It's a draw!\n""", 'utf-8'))
    connectionSocket.close()

#MAIN
while 1:
    isDoneBroadcasting = False 
    i = True # random boolean value for deciding client group assignment
    group1 = {}
    group2 = {}
    serverSocket = socket(AF_INET, SOCK_STREAM) #TCP socket
    serverSocket.bind(('', serverTCPPort))
    serverSocket.listen(1)

    cv = threading.Condition()
    tcpThread = threading.Thread(target=acceptTcpConn, args=(cv,))
    tcpThread.start()

    sock = socket(AF_INET, SOCK_DGRAM) #UDP socket
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    print('Server started, listening on IP address ' + host)
    timeout = time.time() + 10
    while time.time() < timeout: 
        sock.sendto(pack('!Ibh', 0xfeedbeef, 0x2, 0x1f40), (host, serverUDPPort)) #send packet every sec for 10s
        time.sleep(1)
    isDoneBroadcasting = True
    cv.acquire()
    cv.notifyAll() # notify game threads that we're done broadcasting and ready to play
    cv.release()
    sock.close()
    time.sleep(11) # wait for game to finish
    print('Game over, sending out offer requests...')
    serverSocket.close() 