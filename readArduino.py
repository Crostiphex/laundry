import serial
import time

port = serial.Serial('COM3', 9600)

while True:
    # print port.read()
    status = port.read()

    if (status == "A"):
        print ' in use'
    elif (status == "F"):
        print 'not in use'
    else:
        print "ShIT"

    time.sleep(2)

# print port.name


port.close()
