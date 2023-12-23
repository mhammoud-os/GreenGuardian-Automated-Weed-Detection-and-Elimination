import pygame
import time
import sys
import serial
def sendDataOverSerialPort(data):
    ser = serial.Serial(port='/dev/ttyACM0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1)

    if ser.isOpen():
        try:
            ser.flushInput()
            ser.flushOutput()
            ser.write(bytes(data,'iso-8859-1'))
        except Exception as e1:
            logMsg ='[serialPrinter]: Communication error...:' + str(e1)
            print(logMsg)    
   
       

pygame.init()

screen = pygame.display.set_mode((100, 100))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Get the state of all keys
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        sendDataOverSerialPort("0")
        print("left")
    elif keys[pygame.K_RIGHT]:
        sendDataOverSerialPort("2")
    elif keys[pygame.K_UP]:
        sendDataOverSerialPort("1")
    elif keys[pygame.K_DOWN]:
        sendDataOverSerialPort("3")
    elif keys[pygame.K_SPACE]:
        sendDataOverSerialPort("4")
    else:
        sendDataOverSerialPort("5")


    pygame.time.Clock().tick(30)

