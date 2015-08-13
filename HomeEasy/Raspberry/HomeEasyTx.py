import sys
import os
from utilClasses import homeEasyCmmTx
import RPi.GPIO as GPIO ## Import GPIO library

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

HETx = homeEasyCmmTx()
HETx.loadDir(strFolder)

#---------------


try:
    bExit = False
    while not(bExit):
        var = raw_input("\n----------------" \
                        "\n Enter command: \n" \
                        "   - f - Load folder files \n" \
                        "   - p - Print commands \n" \
                        "   - e - Execute command \n" \
                        "   - q - Quit \n\n" \
                        "> ")

        
        if var == 'f':
            HETx.loadDir(raw_input("\n Enter Folder Name> "))
        elif var == 'p':
            print "\n Commands: \n"
            cmms = HETx.HEMng.getCmms()
            for cmm in cmms:
                print "- " + cmm
        elif var == 'e':
            if HETx.runCmm(raw_input("\n Enter command> ")):
                print "Do it!"
            else:
                print "Error!"
        elif var == 'q':
            GPIO.cleanup()
            bExit = True
except:
    GPIO.cleanup()
