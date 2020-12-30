from socket import *
from struct import *
from pynput import *
import time
import msvcrt

teamName = 'AdiRom\n'
serverName = 'localhost'
serverPort = 13117

while 1:
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind((serverName, serverPort))
    print('Client started, listening for offer requests...')
    try:
        data, addr = clientSocket.recvfrom(1024)
    except:
        break
    serverName = addr[0]
    magicCookie = hex(unpack('!Ibh', data)[0])
    serverTCPPort = unpack('!Ibh', data)[2]
    port = unpack('!Ibh', data)[2]
    if magicCookie != '0xfeedbeef': #accept only messages containing the magic cookie
        continue
    print('Received offer from {}, attempting to connect...'.format(addr[0]))
    clientSocket.close()
    tcpSocket = socket(AF_INET, SOCK_STREAM)
    tcpSocket.connect((serverName, port))
    tcpSocket.send(pack(str(len(teamName))+'s', bytes(teamName, 'utf-8'))) # send team name
    try:
        print(tcpSocket.recv(1024).decode('utf-8'))
    except:
        break
    timeout = time.time() + 10 #there are 10s to type chars

    while time.time() < timeout:
        if msvcrt.kbhit(): #if key pressed, send info to server
            msvcrt.getch()
            try:
                tcpSocket.send(pack(str(len(teamName))+'s', bytes(teamName, 'utf-8')))
            except:
                break

    try:
        print(tcpSocket.recv(1024).decode('utf-8'))
    except:
        print('Error')
    print('Server disconnected, listening for offer requests...')
    tcpSocket.close()
