import socket
import sys
import time
import pygame
import threading
from math import floor
import binascii

###################################################################

def add(a, b):
    c = bin(int(a,2) + int(b,2))	#suma bit a bit, definimos enteros en base dos
    return (c)

def checksum(msg):
    s = "0"
    for i in range(0, len(msg), 2):
        w = bin(int(msg[i] + msg[i+1], 16))[2:].zfill(8)
        s = add(s, w)
    return s		# s tiene formato int

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # si es un valor negativo 0b1...
        val = val - (1 << bits)        # le resto 1 desplazado 8 veces
    else:	#si el valor es positibo 0b0...
	val = (1 << bits) - val
    return val 

class RecurringTimer(threading._Timer):
     
    def __init__ (self, *args, **kwargs):
        threading._Timer.__init__ (self, *args, **kwargs) 
        self.setDaemon (True)
        self._running = 0
        self._destroy = 0
        self.start()
 
    def run (self):
        while True:
            self.finished.wait (self.interval)
            if self._destroy:
                return;
            if self._running:
                self.function (*self.args, **self.kwargs)
 
    def start_timer (self):
        self._running = 1
 
    def stop_timer (self):
        self._running = 0
 
    def is_running (self):
        return self._running
 
    def destroy_timer (self):
        self._destroy = 1;

def timer_send():
	global mt
	global word1
	mt_bin=mt>>0x18
	mt_bin=mt_bin&0x00000000000000000000000000000000000000000000000000ff
	if mt_bin<0x3b:		#si segundos<60
		mt=mt+0x1000000		#aumento segundos
	else:
		mt=mt+0x100000000000000	#aumento minutos
		mt=mt-0x3b000000	#segundos=0
	mt_hex = hex(mt).rstrip("L") # para quitar la L del final y pasarlo al formato correcto	
	sock1.send(mt_hex)
	sock.send(word1)

def get():
    
    a=int(floor((j.get_axis(0)+1)*63))	#valor entero en la escala que espera el dron
    a1='{0:02x}'.format(a)	#formato hexadecimal sin 0x
    b=int(floor((j.get_axis(1)-1)*-126))
    b1='{0:02x}'.format(b)
    c=int(floor((j.get_axis(3)+1)*63))
    c1='{0:02x}'.format(c)
    d=int(floor((j.get_axis(4)+1)*63))
    d1='{0:02x}'.format(d)
    commands1="90101002"	#valores por defecto durante el vuelo, al final 0/30% 1/60% 2/100% 6/giro
    commands2="90101004"
    if (j.get_button(0)==1):	#para hacer 360
	commands1="90101006"	
	commands2="90101008"
    message="ff08"+b1+a1+d1+c1+commands1;
    chsum=checksum("ff08"+b1+a1+c1+d1+commands2)	#sumo 2 al mensaje porque asi da el valor esperado
    l0= len(chsum)
    chsum = chsum[l0-8:]	#recorta solo los 8 ultimos caracteres de la suma de comprobacion por si >8
    chsum1 = twos_comp(int(chsum,2), len(chsum))	#hace el complemento a 2 de la chsum SIN el 0b
    chsum2=hex(chsum1).lstrip("0x").lstrip("-0x")	#lstrip busca y quita la cadena citada
    if(len(chsum2)!=2):		#si la cadena es menor que 0x10 tenemos que poner manualmente el 0 a la izquierda
	chsum2="0"+chsum2
    pygame.event.pump()
    return message+chsum2

####################################################################

pygame.init()
j = pygame.joystick.Joystick(0)
j.init()

#Socket control
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock1.connect(('172.16.10.1', 8080))

#Socket camara
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('172.16.10.1', 8888))

word='000102030405060708092525'.decode('hex')
word1='000102030405060708092828'.decode('hex')

#Conectar camara
s.send(word)
data = s.recv(106) 
s.send(word)
data = s.recv(106) 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('172.16.10.1', 8888))
sock.send(word1)
data = sock.recv(106)

#Conectar control
sock1.send(('0f').decode('hex'))
data = sock1.recv(106)
sock1.send(('28').decode('hex'))
data = sock1.recv(106)
sock1.send(('26e10700000900000019000000010000000d000000110000002e000000').decode('hex'))
data = sock1.recv(106)
print data; #aqui dice timeok
time.sleep(1)
sock1.send(('26e10700000900000019000000010000000d000000110000002f000000').decode('hex'))
time.sleep(1.4)
sock1.send(('1a').decode('hex'))
data = sock1.recv(106)
print data; #aqui dice mirror=1
sock1.send(('26e10700000900000019000000010000000d0000001100000030000000').decode('hex'))
mt=0x26e10700000900000019000000010000000d0000001100000031000000 #inicializa la marca temporal
t= RecurringTimer(1.0, timer_send) #inicia el timer para mandar cada segundo la marca temporal
t.start_timer()
time.sleep(0.5)

while 1: #write replace by while 1 if you want this to not stop
    
    data = sock.recv(1460)
    sys.stdout.write(data)
    men='ff087e3f403f901010a06b'
    #men=get()
    #print men
    if (j.get_button(4)==1):
	men='ff087e3f403f90101040cb'
	print "despegando"
    if (j.get_button(1)==1):
	men='ff087e3f403f901010a06b'
	print "parada emergencia"
    if (j.get_button(5)==1):
	men='ff08003f403f1010100009'
	print "aterrizando"
    sock1.send(men.decode('hex'))


    #time.sleep(0.1)	#una pequena espera para no mandar paquetes excesivamente rapido

s.close()

