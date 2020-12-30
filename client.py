from socket import *
from struct import *
from pynput import *
import time
import msvcrt

teamName = 'Rom\n'
def on_press(key):
    try:
        print('key {0} pressed'.format(key.char))
        tcpSocket.send(pack(str(len(teamName))+'s', bytes(teamName, 'utf-8')))
    except:
        print('bad shit')
        tcpSocket.close()
        return False

def on_release(key):
    print('{0} released'.format(key.char))

serverName = 'localhost'
serverPort = 13117
while 1:
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind((serverName, serverPort))
    print('Client started, listening for offer requests...')
    data, addr = clientSocket.recvfrom(1024)
    serverName = addr[0]
    magicCookie = hex(unpack('!Ibh', data)[0])
    serverTCPPort = unpack('!Ibh', data)[2]
    port = unpack('!Ibh', data)[2]
    if magicCookie != '0xfeedbeef':
        continue
    print('Received offer from {}, attempting to connect...'.format(addr[0]))
    clientSocket.close()
    tcpSocket = socket(AF_INET, SOCK_STREAM)
    tcpSocket.connect((serverName, port))
    tcpSocket.send(pack(str(len(teamName))+'s', bytes(teamName, 'utf-8')))
    print(tcpSocket.recv(1024).decode('utf-8'))
    timeout = time.time() + 10

    while time.time() < timeout:
        if msvcrt.kbhit():
            msvcrt.getch()
            try:
                tcpSocket.send(pack(str(len(teamName))+'s', bytes(teamName, 'utf-8')))
            except:
                #tcpSocket.close()
                break

    print(tcpSocket.recv(1024).decode('utf-8'))
    print('Server disconnected, listening for offer requests...')
    tcpSocket.close()
#sentence = input('Input lowercase sentence:')
#size = len(sentence)
#with keyboard.Listener(
#        on_press=on_press,
#        on_release=on_release) as listener:
#    listener.join()
#modifiedSentence = unpack(str(size)+'s',clientSocket.recv(1024))
#print('From Server:', modifiedSentence[0].decode("utf-8"))
