import socket
import time
import pygame
import threading
from math import floor
import binascii

#This is a really old project of mine, use at your own discretion. I translated the comments to english, but I still don't fully remember how this all worked, you'll have to figure that out yourself :)

def add(a, b):
    c = bin(int(a,2) + int(b,2))	#bitwise sum base 2
    return (c)

def checksum(msg):
    s = "0"
    for i in range(0, len(msg), 2):
        w = bin(int(msg[i] + msg[i+1], 16))[2:].zfill(8)
        s = add(s, w)
    return s

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # to make a negative value it's 0b1...
        val = val - (1 << bits)
    else:	#for a positive value it's 0b0...
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

#clock neccesary for coordination between drone and app
def timer_send():
	global mt
	mt_bin=mt>>0x18
	mt_bin=mt_bin&0x00000000000000000000000000000000000000000000000000ff
	if mt_bin<0x3b:		#if seconds<60
		mt=mt+0x1000000		#increase seconds
	else:
		mt=mt+0x100000000000000	#increase minutes
		mt=mt-0x3b000000	#seconds=0
	mt_hex = hex(mt).rstrip("L") # remove L character in the end
	sock1.send(mt_hex)
	

#compose message to sent to drone
def get():
    
    a=int(floor((j.get_axis(0)+1)*63))	#integer value in awaited scale
    a1='{0:02x}'.format(a)	#hex without 0x
    b=int(floor((j.get_axis(1)-1)*-126))
    b1='{0:02x}'.format(b)
    c=int(floor((j.get_axis(3)+1)*63))
    c1='{0:02x}'.format(c)
    d=int(floor((j.get_axis(4)+1)*63))
    d1='{0:02x}'.format(d)
    commands1="90101002"	#default values during flight
    commands2="90101004"
    global vel;
    global pulsado;
    if (j.get_button(2)==1):	#make a velocity change pressing x button, drone goes faster
	if (pulsado==0):
	    pulsado=1;
	    vel=~vel;
    else:
	pulsado=0;
    if (vel==True):
	commands1="90101000"
	commands2="90101002"
    if (j.get_button(0)==1):
	commands1="90101006"	#to do a  360
	commands2="90101008"
    message="ff08"+b1+a1+d1+c1+commands1;
    chsum=checksum("ff08"+b1+a1+c1+d1+commands2)	#construct full message + checksum
    l0= len(chsum)
    chsum = chsum[l0-8:]	#recorta solo los 8 ultimos caracteres de la suma de comprobacion por si >8
    chsum1 = twos_comp(int(chsum,2), len(chsum))	#2 complement checksum without the 0b
    chsum2=hex(chsum1).lstrip("0x").lstrip("-0x")
    if(len(chsum2)!=2):		# if chain is lesser than 0x10 we manually add 0 on the left
	chsum2="0"+chsum2
    pygame.event.pump()
    return message+chsum2

####################################################################

pygame.init()
j = pygame.joystick.Joystick(0)
j.init()

vel=True;
pulsado=True;

# The IP of the quadcopter plus the UDP port it listens to for control commands
IPADDR = '172.16.10.1'
PORTNUM = 8080

 
# initialize a socket
# SOCK_DGRAM specifies that this is UDP
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
 
# connect the socket
sock1.connect((IPADDR, PORTNUM))

sock1.send(('0f').decode('hex'))
data = sock1.recv(106)
sock1.send(('28').decode('hex'))
data = sock1.recv(106)
sock1.send(('26e10700000900000019000000010000000d000000110000002e000000').decode('hex'))
data = sock1.recv(106)
print data; #drone answers dice timeok

time.sleep(1)
sock1.send(('26e10700000900000019000000010000000d000000110000002f000000').decode('hex'))
time.sleep(1.4)

sock1.send(('1a').decode('hex'))
data = sock1.recv(106)
print data; #drone mirror=1

sock1.send(('26e10700000900000019000000010000000d0000001100000030000000').decode('hex'))
mt=0x26e10700000900000019000000010000000d0000001100000031000000 #initialize timestamp
t= RecurringTimer(1.0, timer_send) #send timestamp every second
t.start_timer()
time.sleep(0.5)

while True:
    
    men=get()
    print men
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
    time.sleep(0.02)	#wait 0.02s to not send packages too fast

s.close()

