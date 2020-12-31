from socket import *
from struct import *
from pynput import *
import time
import msvcrt

teamName = 'Rom\n'
IP = 'localhost'
UDPPort = 13117
gameDuration = 10

while 1:
    UDPSocket = socket(AF_INET, SOCK_DGRAM)
    try:
        UDPSocket.bind((IP, UDPPort))
    except:
        UDPSocket.close()   #in case port is taken, try again
        continue
    print('Client started, listening for offer requests...')
    try:
        data, addr = UDPSocket.recvfrom(1024)
    except:
        UDPSocket.close()
        continue
    serverIP = addr[0]
    magicCookie = hex(unpack('!Ibh', data)[0])
    serverTCPPort = unpack('!Ibh', data)[2]
    if magicCookie != '0xfeedbeef': #accept only messages containing the magic cookie
        UDPSocket.close()
        continue
    print('Received offer from {}, attempting to connect...'.format(serverIP))
    UDPSocket.close()
    TCPSocket = socket(AF_INET, SOCK_STREAM)
    TCPSocket.connect((serverIP, serverTCPPort))
    TCPSocket.send(pack(str(len(teamName))+'s', bytes(teamName, 'utf-8'))) # send team name
    try:
        print(TCPSocket.recv(1024).decode('utf-8')) # receive game start message
    except:
        TCPSocket.close()
        continue
    timeout = time.time() + gameDuration #there are 10s to type chars

    while time.time() < timeout:
        if msvcrt.kbhit(): #if key pressed, send info to server
            msvcrt.getch()
            try:
                TCPSocket.send(pack(str(len(teamName))+'s', bytes(teamName, 'utf-8')))
            except:
                break

    try:
        print(TCPSocket.recv(1024).decode('utf-8'))
    except:
        TCPSocket.close()
        print('Error')
    print('Server disconnected, listening for offer requests...')
    TCPSocket.close()
