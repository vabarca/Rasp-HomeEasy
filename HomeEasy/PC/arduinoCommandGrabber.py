import sys
import serial
import time
from plotUtils import homeEasyComm
from plotUtils import homeEasyCommMng
import os

#---------------

'''
 Tres valores especiales que duran mas de 2550 us
  y por lo tanto no se pueden codificar en un byte:
 - 5000 us - codificado como TEMP_5000_US
 - 10000 us - codificado como TEMP_10000_US
 - Final de trama - codificado como END_MSG
'''

END_MSG          =  255
TEMP_10000_US    =  254
TEMP_5000_US     =  253

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
strFolderTestFile = strFolder

if sys.platform.startswith('win'):
    strFolderTestFile = strFolderTestFile +"\\test.cmm"
else:
    strFolderTestFile = strFolderTestFile +"/test.cmm"

ser = serial.Serial()
HEMng = homeEasyCommMng()

bExit = False

try:
    if sys.platform.startswith('win'):
        ser = serial.Serial('COM6', 57600, timeout=0)
    else:
        ser = serial.Serial('/dev/ttyUSB0', 57600) 
except:
    print "No podemos conectar con el puerto serie, peluo!"
    ser.close()
    bExit = True

while not(bExit):
    var = raw_input(" \n Print: \n " \
       "-'a' Set up system for grabb msg \n " \
       "-'v' show incomming msg verbose output \n " \
       "-'l' show incomming msg ascii output \n " \
       "-'s' save incomming msg \n " \
       "-'p' plot last incomming msg \n " \
       "-'t' transmit incomming msg \n " \
       "-'q' quit \n\n > ")

    if var == 'a':
        print " \n *Attach \n"
        ser.write('a')
        ser.flush()
        time.sleep(0.1)
    elif var == 'v':
        print " \n *Verbose \n"
        ser.write('v')
        ser.flush()
        time.sleep(0.1)
        try:
            bLoop = True
            serialBuffer = ''
            while bLoop:
                serialBufferTemp = ser.readline()
                serialBuffer += serialBufferTemp
                if serialBufferTemp.find("255") != -1:
                    bLoop = False
            print serialBuffer
        except ser.SerialTimeoutException:
            print('Data could not be read')
            time.sleep(1)
        targetFile = open(strFolderTestFile, 'w')
        targetFile.write(serialBuffer)
        targetFile.close()
    elif var == 'l':
        print " \n *Log \n"
        ser.write('l')
        ser.flush()
        time.sleep(0.1);
        try:
            bLoop = True
            serialBuffer = ''
            while bLoop:
                serialBufferTemp = ser.readline()
                serialBuffer += serialBufferTemp
                if serialBufferTemp.find("255") != -1:
                    bLoop = False
            print serialBuffer
            time.sleep(1)
        except ser.SerialTimeoutException:
            print('Data could not be read')
            time.sleep(1)
        targetFile = open(strFolderTestFile, 'w')
        targetFile.write(serialBuffer)
        targetFile.close()
    elif var == 's':
        print " \n *Save File \n"
        ser.write('l')
        ser.flush()
        time.sleep(0.1)
        try:
            bLoop = True
            serialBuffer = ''
            while bLoop:
                serialBufferTemp = ser.readline()
                serialBuffer += serialBufferTemp
                if serialBufferTemp.find("255") != -1:
                    bLoop = False
            print serialBuffer
            time.sleep(1)
        except ser.SerialTimeoutException:
            print('Data could not be read')
            time.sleep(1)
        var = raw_input("\n Enter file name> ")
        targetFile = open(var, 'w')
        targetFile.write(serialBuffer)
        targetFile.close()
        targetFile2 = open(strFolderTestFile, 'w')
        targetFile2.write(serialBuffer)
        targetFile2.close()
    elif var == 'p':            
        HEMng.loadDir(strFolder)
        commands = HEMng.getCmms()
        print strFolder
        for cmm in commands:
            print cmm
            if cmm == "test":
                HEMng.plotCmm(cmm)
    elif var == 't':
        print " \n Transmitting...\n"
        ser.write('t')
        ser.flush()
        time.sleep(0.1)
    elif var == 'q':
        ser.close()
        bExit = True

