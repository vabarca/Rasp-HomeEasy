import sys
import glob
import matplotlib.pyplot as plt

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

    def plotSeq(self):
        arrayTimeTemp = self._arrayTime
        arrayStateTemp = self._arrayState

        arrayStateTemp2 = []
        arrayTimeTemp2 = []

        for index in range (1,len(arrayTimeTemp)):
            arrayTimeTemp[index] += arrayTimeTemp[index-1]

        arrayTimeTemp[len(arrayTimeTemp)-1] = arrayTimeTemp[len(arrayTimeTemp)-1] - 480000

        arrayStateTemp2.append(0);
        arrayTimeTemp2.append(0);
        arrayStateTemp2.append(arrayStateTemp[0]);
        arrayTimeTemp2.append(1);

        for index in range (0,len(arrayTimeTemp)):

            arrayStateTemp2.append(arrayStateTemp[index]);
            arrayTimeTemp2.append(arrayTimeTemp[index]);

            state = arrayStateTemp[index]
            if state == 0:
                arrayStateTemp2.append(1);
            else:
                arrayStateTemp2.append(0);

            arrayTimeTemp2.append(arrayTimeTemp[index]+1);
        
        plt.plot(arrayTimeTemp2,arrayStateTemp2)
        plt.title('This is the command output - ' + str(len(self._arrayState)))
        plt.xlabel('Time in usec')
        plt.ylabel('Logical value')
        plt.axis([0, arrayTimeTemp2[len(arrayTimeTemp2)-1], 0, 1.2])
        #plt.axis([0,15000, 0, 1.2])
        plt.show()

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

    def plotCmm(self, cmmObjName):
        if(homeEasyCommMng.cmmObjs.has_key(cmmObjName)):
            obj = homeEasyCommMng.cmmObjs[cmmObjName]
            obj.plotSeq()
            return True
        else:
            print "No command"
            return False          

    def getCmms(self):  
        cmmObjNames = []
        for key, value in homeEasyCommMng.cmmObjs.iteritems():
            cmmObjNames.append(key)
        return cmmObjNames

