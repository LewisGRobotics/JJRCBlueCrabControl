import socket
import sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('172.16.10.1', 8888))

word='000102030405060708092525'.decode('hex')
word1='000102030405060708092828'.decode('hex')

s.send(word)
data = s.recv(106) 
s.send(word)
data = s.recv(106) 

SOURCE_PORT = 8888
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.bind(('0.0.0.0', SOURCE_PORT))
sock.connect(('172.16.10.1', 8888))
sock.send(word1)
data = sock.recv(106)

while 1: #write replace by while 1 if you want this to not stop
    n=0
    while n<80:
	data = sock.recv(1460)
	sys.stdout.write(data)
	n=n+1
    sock.send(word1)
s.close()
