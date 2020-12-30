from socket import *
from struct import *
import time
import threading

host = 'localhost'
serverUDPPort = 13117
serverTCPPort = 8000

def acceptTcpConn(cv):
    global i
    while not isDoneBroadcasting:
        try:
            connectionSocket, addr = serverSocket.accept()
            teamName = connectionSocket.recv(1024).decode('utf-8')
            if i:
                group1[teamName] = 0
            else:
                group2[teamName] = 0
            i = not i
            threading.Thread(target=openTcpConn, args=(cv, connectionSocket, teamName,)).start()
        except:
            break


def openTcpConn(cv, connectionSocket, teamName):
    cv.acquire()
    while not isDoneBroadcasting:
        cv.wait()
    cv.release()
    counter = 0
    keys1 = group1.keys()
    keys2 = group2.keys()
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
    timeout = time.time() + 10
    while time.time() < timeout:
        connectionSocket.settimeout(timeout - time.time())
        try:
            connectionSocket.recv(1024)
        except:
            break
        counter = counter + 1
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


def calcWinner(cv):
    cv.acquire()
    while not isGameDone:
        cv.wait()
    cv.release()
    if group1 or group2:
        score1 = sum(list(group1.values()))
        score2 = sum(list(group2.values()))
        #print('Game Over!')
        #print('Group 1 typed in ' + str(score1) + ' characters. Group 2 typed in ' + str(score2) + ' characters.')
        if score1 > score2:
            serverSocket.send(bytes(
                """Game Over!
Group 1 typed in """ + str(score1) + """ characters. Group 2 typed in """ + str(score2) + """ characters.
Group 1 wins!\n
Congratulations to the winners:
==\n""" + ''.join(list(group1.keys()))
                , 'utf-8'))
            #print('Group 1 wins!\n')
            #print('Congratulations to the winners:')
            #print('==')
            #print(''.join(list(group1.keys())))
        elif score1 < score2: 
            serverSocket.send(bytes(
                """Game Over!
Group 1 typed in """ + str(score1) + """ characters. Group 2 typed in """ + str(score2) + """ characters.
Group 2 wins!\n
Congratulations to the winners:
==\n""" + ''.join(list(group2.keys()))
                , 'utf-8'))
            #print('Group 2 wins!')
            #print('Congratulations to the winners:')
            #print('==')
            #print(''.join(list(group2.keys())))
        else:
            print('Draw!') 

while 1:
    isDoneBroadcasting = False 
    isGameDone = False
    i = True
    group1 = {}
    group2 = {}
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverTCPPort))
    serverSocket.listen(1)

    cv = threading.Condition()
    tcpThread = threading.Thread(target=acceptTcpConn, args=(cv,))
    tcpThread.start()
    #calcWinnersThread = threading.Thread(target=calcWinner, args=(cv,))
    #calcWinnersThread.start()

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    print('Server started, listening on IP address localhost')
    timeout = time.time() + 10
    while time.time() < timeout:
        sock.sendto(pack('!Ibh', 0xfeedbeef, 0x2, 0x1f40), (host, serverUDPPort))
        time.sleep(1)
    isDoneBroadcasting = True
    cv.acquire()
    cv.notifyAll()
    cv.release()
    sock.close()
    time.sleep(11)
    print('Game over, sending out offer requests...')
    serverSocket.close() 
#isGameDone = True
#cv.acquire()
#cv.notifyAll()
#cv.release()

