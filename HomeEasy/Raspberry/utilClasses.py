import RPi.GPIO as GPIO ## Import GPIO library
import glob
import sys
import time 

usleep = lambda x: time.sleep(x/1000000.0)

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

class homeEasyComm:
    def __init__(self, ID):
        self._id = ID
        self._arrayState = []
        self._arrayTime = []
        self._arrayTimeRAW = []

    def clear(self):
        self._arrayState = []
        self._arrayTime = []
        self._arrayTimeRAW = []

class homeEasyCommMng:
    cmmObjs = {}

    def parseFile(self,fileName,cmmObj):
        file2Parse = open(fileName,"r")

        try:
            for line in file2Parse:
                rslt = line.split(',')
                if len(rslt) == 2:
                    cmmObj._arrayState.append(int(rslt[0]))
                    rslt = rslt[1].split('\n')
                    iTime = int(rslt[0])
                    cmmObj._arrayTimeRAW.append(iTime)

                    if iTime == END_MSG:
                        iTime = 50000
                    elif iTime == TEMP_10000_US:
                        iTime = 10000
                    elif iTime == TEMP_5000_US:
                        iTime = 5000
                    else:
                        iTime *= 10

                    cmmObj._arrayTime.append(iTime)
            file2Parse.close()
        except:
            print "File with wrong format. Check it out!"
            return False

        if len(cmmObj._arrayState) == len(cmmObj._arrayTime):
            #print "Estados "
            #print cmmObj._arrayState
            #print "Tiempos "
            #print cmmObj._arrayTime
            return True
        else:
            print "File with wrong format. Check it out!"
            return False

    def loadDir(self, dirName):
        homeEasyCommMng.cmmObjs.clear()
        self._dirName = dirName
        dirName += "/*.cmm"
        commFileList = glob.glob(dirName)
        if len(commFileList) > 0:
            for fileName in commFileList:
                if(fileName.find('.cmm') != -1):
                    fileNameSplitList = fileName.split('.')
                    strTemp = fileNameSplitList[0]
                    if sys.platform.startswith('win'):
                        cmmObj = homeEasyComm(strTemp.replace(self._dirName+"\\", ""))
                    else:
                        cmmObj = homeEasyComm(strTemp.replace(self._dirName+"/", ""))

                    if self.parseFile(fileName,cmmObj):
                        homeEasyCommMng.cmmObjs[cmmObj._id] = cmmObj
        return len(homeEasyCommMng.cmmObjs)

    def getCmms(self):  
        cmmObjNames = []
        for key, value in homeEasyCommMng.cmmObjs.iteritems():
            cmmObjNames.append(key)
        return cmmObjNames        

class GPIOMsgSender:
    def __init__(self, pin):
        self._pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._pin, GPIO.OUT)     ## Setup GPIO Pin to OUT
        

    def txMsg(self, cmmObj):
        for i in range (0,len(cmmObj._arrayState)):
            if cmmObj._arrayState[i] == 1:
                GPIO.output(self._pin,True)
            else:
                GPIO.output(self._pin,False)
            usleep(cmmObj._arrayTime[i]) #sleep during 100ms

        GPIO.output(self._pin,False)
        time.sleep(1)
        return True

class homeEasyCmmTx:
    HEMng = homeEasyCommMng()
    sender = GPIOMsgSender(7)      ## GPIO 4

    def loadDir(self, dirName):
        homeEasyCmmTx.HEMng.loadDir(dirName)

    def runCmm(self, cmmObjName):
        if(homeEasyCommMng.cmmObjs.has_key(cmmObjName)):
            homeEasyCmmTx.sender.txMsg(homeEasyCommMng.cmmObjs[cmmObjName])
            return True
        else:
            print "No command"
            return False

#---------------
