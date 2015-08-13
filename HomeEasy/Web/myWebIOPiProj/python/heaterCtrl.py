#import glob
import webiopi
import datetime
import os
import pickle

#from webiopi.devices.serial import Serial

#---------------------------
#---------------------------
#     HOMEEASY CLASSES
#---------------------------
#---------------------------

STATE_UNDEFINED = -1
STATE_ON = 1
STATE_OFF = 0

#---------------------------
#---------------------------

ser = webiopi.deviceInstance("ardu")

#---------------------------
#---------------------------


class homeEasyCommand:
    def __init__(self, fileName):
        self._arrayState = []
        self._arrayTimeRAW = []
        try:
            file2Parse = open(fileName, "r")
            for line in file2Parse:
                rslt = line.split(',')
            if len(rslt) == 2:
                self._arrayState.append(int(rslt[0]))
                rsltTime = rslt[1].split('\n')
                self._arrayTimeRAW.append(int(rsltTime[0]))
            file2Parse.close()
        except:
            pass

        if len(self._arrayState) != len(self._arrayTimeRAW):
            self._arrayState = []
            self._arrayTimeRAW = []

    def run(self):
        lenght = int(len(self._arrayTimeRAW))

        if lenght == 0:
            return False

        print "kk"

        ser.writeByte('W')
        ser.writeByte('H')
        ser.writeByte('D')
        ser.writeByte('O')
        ser.writeByte(chr(0x000000FF & (lenght >> 8)))
        ser.writeByte(chr(lenght & 0x000000FF))
        ser.writeByte(chr(self._arrayState[0]))

        for timeValue in self._arrayTimeRAW:
            ser.writeByte(chr(timeValue))

        ser.writeByte('M')
        ser.writeByte('S')
        ser.writeByte('L')
        ser.writeByte('P')
        rslt = ser.read()

        return rslt == "ok"

#---------------------------
#---------------------------


class homeEasyChannel:
    def __init__(self, ID, dirName):

        self._id = ID
        self._dirName = dirName
        self._currentState = STATE_UNDEFINED
        self._timeSchedule = ()

        fileNameOn = dirName + "/" + "on" + ID + ".cmm"
        fileNameOff = dirName + "/" + "off" + ID + ".cmm"
        self._chnnCommands = {}
        self._chnnCommands['on'] = homeEasyCommand(fileNameOn)
        self._chnnCommands['off'] = homeEasyCommand(fileNameOff)

        self.loadSchedule()

    def switchON(self):
        if self._chnnCommands['on'].run():
            self._currentState = STATE_ON
        else:
            self._currentState = STATE_UNDEFINED
        return self._currentState

    def switchOFF(self):
        if self._chnnCommands['off'].run():
            self._currentState = STATE_OFF
        else:
            self._currentState = STATE_UNDEFINED
        return self._currentState

    def setSwitch(self, var):
        if var == STATE_ON:
            return self.switchON()
        elif var == STATE_OFF:
            return self.switchOFF()

    def clearSchedule(self):
        self._timeSchedule = ()

    def getSchedule(self):
        return self._timeSchedule

    def setSchedule(self, timeSchedule):
        self._timeSchedule = timeSchedule
        self.saveSchedule()

    def update(self, currentTime):
        if len(self._timeSchedule) != 0:
            # _timeSchedule = [(time1.start, state),
            #(time1.stop, state),(time2.start,state),(time2.stop,state)]
            for element in self._timeSchedule:
                if currentTime < element[0]:
                    if self._currentState != element[1]:
                        self.setSwitch(element[1])

    def saveSchedule(self):
        fileName = self._dirName + "/" + self.id + ".chdl"
        pickle.dump(self._timeSchedule, fileName)

    def loadSchedule(self):
        try:
            fileName = self._dirName + "/" + self.id + ".chdl"
            self._timeSchedule = pickle.load(fileName)
        except:
            self.clearSchedule()

#---------------------------
#---------------------------


class homeEasyChannelMng:
    chnnObj = {}
    enableSystem = STATE_ON

    def __init__(self, dirName):
        homeEasyChannelMng.chnnObj["1"] = homeEasyChannel("1", dirName)
        homeEasyChannelMng.chnnObj["2"] = homeEasyChannel("2", dirName)
        homeEasyChannelMng.chnnObj["3"] = homeEasyChannel("3", dirName)
        homeEasyChannelMng.chnnObj["4"] = homeEasyChannel("4", dirName)
        homeEasyChannelMng.chnnObj["M"] = homeEasyChannel("M", dirName)

        #Paramos todas las salidas
        homeEasyChannelMng.chnnObj["M"].switchOFF

        #Actualizamos los estados
        #self.update()

    def getChannelSchedule(channel):
        if homeEasyChannelMng.enableSystem == STATE_ON:
            for key, value in homeEasyChannelMng.chnnObj.iteritems():
                if key == channel:
                    return value.getSchedule()
        emptyList = []
        return emptyList

    def setChannelSchedule(channel, schedule):
        if homeEasyChannelMng.enableSystem == STATE_ON:
            for key, value in homeEasyChannelMng.chnnObj.iteritems():
                if key == channel:
                    value.setSchedule(schedule)

    def updateChannels(self, currentTime):
        if homeEasyChannelMng.enableSystem == STATE_ON:
            for key, value in homeEasyChannelMng.chnnObj.iteritems():
                value.update(currentTime)

    def switchChannel(self, channel, state):
        if homeEasyChannelMng.enableSystem == STATE_ON:
            for key, value in homeEasyChannelMng.chnnObj.iteritems():
                if key == channel:
                    return value.setSwitch(state)
        return STATE_UNDEFINED

    def getChannelState(self, channel):
        if homeEasyChannelMng.enableSystem == STATE_ON:
            for key, value in homeEasyChannelMng.chnnObj.iteritems():
                if key == channel:
                    return value._currentState
        return STATE_UNDEFINED

    def setSystemEnable(var):
        if var == STATE_ON:
            homeEasyChannelMng.enableSystem = STATE_ON
        else:
            homeEasyChannelMng.enableSystem = STATE_OFF
            homeEasyChannelMng.chnnObj["M"].switchOFF()

    def getSystemState():
        pass


#---------------------------
#---------------------------
#     MAIN LOOPS WEBIOPI
#---------------------------
#---------------------------

g_full_path = os.path.realpath(__file__)
g_strFolder, g_strfile = os.path.split(g_full_path)
HEMng = homeEasyChannelMng(g_strFolder)

#---------------------------


def setup():
    pass


def loop():
    # retrieve current datetime
    HEMng.updateChannels(datetime.datetime.now())
    HEMng.switchChannel("M", STATE_ON)
    # gives CPU some time before looping again
    print "u"
    webiopi.sleep(5)


def destroy():
    pass

#---------------------------
#---------------------------
#     MACRO DEFINITIONS
#---------------------------
#---------------------------


# macro to switch on channel VAR
@webiopi.macro
def setChannel():#channel, state):
    print "hellou"
    '''
    if state:
        return HEMng.switchChannel(channel, STATE_ON)
    else:
        return HEMng.switchChannel(channel, STATE_OFF)
    '''


# macro to switch off channel VAR
@webiopi.macro
def setChannelSchedule(var):
    channel = '1'
    schedule = []
    return HEMng.setChannelSchedule(channel, schedule)


# set system enabled/disabled
@webiopi.macro
def setEnableSystem(var):
    return HEMng.setSystemEnable(var)


# set system enabled/disabled
@webiopi.macro
def getSystemState():
    return HEMng.getSystemState()
