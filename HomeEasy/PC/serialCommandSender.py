
import sys
import os
import serial
from plotUtils import homeEasyCommMng

#---------------

'''
 Tres valores especiales que duran mas de 2550 us
  y por lo tanto no se pueden codificar en un byte:
 - 5000 us - codificado como TEMP_5000_US
 - 10000 us - codificado como TEMP_10000_US
 - Final de trama - codificado como END_MSG
'''

#---------------

'''
print("Path at terminal when executing this file")
print(os.getcwd() + "\n")

print("This file path, relative to os.getcwd()")
print(__file__ + "\n")

print("This file full path (following symlinks)")
full_path = os.path.realpath(__file__)
print(full_path + "\n")

print("This file directory and name")
path, file = os.path.split(full_path)
print(path + ' --> ' + file + "\n")

print("This file directory only")
print(os.path.dirname(full_path))
'''

#strFolder = "/home/vabarca/RaspberryPi/HomeEasy" #"C:/HomeEasy"
strFolder = os.getcwd()

HEMng = homeEasyCommMng()
HEMng.loadDir(strFolder)

#---------------

'''
if sys.platform.startswith('win'):
    HEMng.loadDir()
else:
    HEMng.loadDir()
'''

ser = serial.Serial()

bExit = False

try:
    if sys.platform.startswith('win'):
        ser = serial.Serial('COM6', 57600, timeout=3)
    else:
        ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=3) 
except:
    print "No podemos conectar con el puerto serie, peluo!"
    ser.close()
    bExit = True

if ser.isOpen() == False:
    ser.open()


while not(bExit):

    ser.flushInput()
    ser.flushOutput()

    var = raw_input(" \n Enter action: \n " \
       "   - s - Send command \n " \
       "   - p - Print commands \n " \
       "   - q - quit \n\n > ")

    if var == 'p':
        print "\n Commands: \n"
        for key, value in HEMng.cmmObjs.iteritems():
            print "- " + key
    elif var == 's':
        var = raw_input("\n Enter command> ")
        for key, value in HEMng.cmmObjs.iteritems():
            if key == var:
                print " Sending msg..."
                ser.write('W')
                ser.write('H')
                ser.write('D')
                ser.write('O')
                lenght = int(len(value._arrayTimeRAW))
                ser.write(chr(0x000000FF & (lenght >> 8)))
                ser.write(chr(lenght & 0x000000FF))
                ser.write(chr(value._arrayState[0]))
                for timeValue in value._arrayTimeRAW:
                    ser.write(chr(timeValue))
                ser.write('M')
                ser.write('S')
                ser.write('L')
                ser.write('P')
                ser.flushOutput()
                print " send it!"
                print " " + ser.readline()
    elif var == 'q':
        ser.close()
        bExit = True

