import sys
from plotUtils import homeEasyCommMng
import os

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

'''
if sys.platform.startswith('win'):
    HEMng.loadDir()
else:
    HEMng.loadDir()
'''

bExit = False

while not(bExit):
    var = raw_input("\n----------------" \
                    "\n Enter command: \n" \
                    "   - p - Print commands \n" \
                    "   - d - Draw commands \n" \
                    "   - q - Quit \n\n" \
                    "> ")
    if var == 'q' or var == 'Q':
        bExit = True
    elif var == 'p':
        print "\n Commands: \n"
        for key, value in HEMng.cmmObjs.iteritems():
            print "- " + key
    elif var == 'd':
        var = raw_input("\n Enter command> ")
        if HEMng.plotCmm(var):
            print "Do it!"
        else:
            print "Error!"
