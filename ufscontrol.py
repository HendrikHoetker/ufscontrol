'''
Created on 01.01.2016

@author: hendrik
'''

import xml.etree.ElementTree as ElementTree
import requests
import json

from .recordingevent import RecordingEvent
from .channel import Channel
from .tvevent import TVEvent
from .timerevent import TimerEvent

import re
import urllib.parse


class UFSControl:
    
    configuration = 0
    
    def __init__(self):
        json_data = open('config.json', encoding='utf-8').read()
        self.configuration = json.loads(json_data)
        
        receiverInterfaceVersion = self.getXmlInterfaceVersion()
        minInterfaceVersion = self.configuration['receiver']['minInterfaceVersion']
        
        if receiverInterfaceVersion < minInterfaceVersion:
            print("Receiver interfaces do not match to required interface")
            assert(False)


    def _webserverhost(self):
        return self.configuration['receiver']['host'] + ':' + self.configuration['receiver']['webserver'] + "/"


    def _downloadserverhost(self):
        return self.configuration['receiver']['host'] + ':' + self.configuration['receiver']['downloadserver'] + "/"


    def getTVRecordings(self):
        recordings = list()
        
        r = requests.get(self._webserverhost() + self.configuration['receiver']['queries']['getTVRecordings'])
        xmldata = r.text.encode("latin-1")
        
        e = ElementTree.fromstring(xmldata)
        for event in e.findall('recordingevent'):
            
            recordingEvent = RecordingEvent()
            
            for child in event.iter():
                if child.tag == 'title':
                    title = child.text
                    title = re.sub('\([0-9]*\)', '', title)
                    title = title.strip()
                    recordingEvent.title = title
                    
                if child.tag == 'archiveNo':
                    recordingEvent.archiveId = int(child.text)
                
                if child.tag == 'startTime':
                    recordingEvent.startTime = int(child.text)
                
                if child.tag == 'duration':
                    recordingEvent.duration = int(child.text)

                if child.tag == 'channelNumber':
                    recordingEvent.channelNumber = int(child.text)

                if child.tag == 'channelName':
                    recordingEvent.channelName = child.text

            recordings.append(recordingEvent)
        
        return recordings
    
    
    def getTVRecordingDownloadPath(self, recordingEvent):
        url = self._downloadserverhost() + 'content/internal-recordings/0/record/' + str(recordingEvent.archiveId) + '/'
        url = url + urllib.parse.quote(str(recordingEvent.title).encode('utf8'), safe='()')
        url = url + ".ts"
        return url
    
    
    def deleteRecordingEvent(self, recordingEvent):
        url = self._webserverhost() + self.configuration['receiver']['commands']['deleteTVRecording']
        url = url.replace('{$1}', str(recordingEvent.archiveId))
        r = requests.get(url)
        
        return "Ok" in r.text
    
    
    def getTvChannel(self, channelNumber):
        query = self.configuration['receiver']['queries']['getTvChannel']
        query = query.replace('{$1}', str(channelNumber))
        r = requests.get(self._webserverhost() + query)
        xmldata = r.text.encode("latin-1")
        
        e = ElementTree.fromstring(xmldata)
        for c in e.findall('channel'):
            channel = Channel()
            
            for child in c.iter():
                if child.tag == 'channelName':
                    if child.text != None:
                        channel.channelName = child.text
                    else:
                        channel.channelName = ""

                if child.tag == 'channelNumber':
                    channel.channelNumber = child.text

                if child.tag == 'streamable':
                    channel.streamable = child.text == "1"

                if child.tag == 'tuneable':
                    channel.tuneable = child.text == "1"

                if child.tag == 'sdChannelNumber':
                    channel.sdChannelNumber = int(child.text)

                if child.tag == 'sdStreamable':
                    channel.sdStreamable = child.text == "1"

                if child.tag == 'hd':
                    channel.hd = child.text == "1"

                if child.tag == 'tvtvId':
                    channel.tvtvId = int(child.text)

                if child.tag == 'dvb':
                    channel.dvb = child.text

                if child.tag == 'channelIcon':
                    channel.channelIcon = child.text

            return channel
            
        return None
        
    
    def getTvChannels(self):
        tvChannels = list()
        
        r = requests.get(self._webserverhost() + self.configuration['receiver']['queries']['getTvChannels'])
        xmldata = r.text.encode("latin-1")
        
        e = ElementTree.fromstring(xmldata)
        for c in e.findall('channel'):
            channel = Channel()
            
            for child in c.iter():
                if child.tag == 'channelName':
                    if child.text != None:
                        channel.channelName = child.text
                    else:
                        channel.channelName = ""

                if child.tag == 'channelNumber':
                    channel.channelNumber = child.text

                if child.tag == 'streamable':
                    channel.streamable = child.text == "1"

                if child.tag == 'tuneable':
                    channel.tuneable = child.text == "1"

                if child.tag == 'sdChannelNumber':
                    channel.sdChannelNumber = int(child.text)

                if child.tag == 'sdStreamable':
                    channel.sdStreamable = child.text == "1"

                if child.tag == 'hd':
                    channel.hd = child.text == "1"

                if child.tag == 'tvtvId':
                    channel.tvtvId = int(child.text)

                if child.tag == 'dvb':
                    channel.dvb = child.text

                if child.tag == 'channelIcon':
                    channel.channelIcon = child.text

            tvChannels.append(channel)
            
        return tvChannels
    
    
    def getEpgOfChannel(self, channel):
        
        epg = list()
        
        query = self.configuration['receiver']['queries']['getEpgOfChannel']
        query = query.replace('{$1}', channel.channelNumber)
        
        r = requests.get(self._webserverhost() + query)
        xmldata = r.text.encode("latin-1")
        
        e = ElementTree.fromstring(xmldata)
        for event in e.findall('event'):
            tvEvent = TVEvent()
            tvEvent.channelName = channel.channelName
            
            endtime = 0
            for child in event.iter():
                if child.tag == 'title':
                    title = child.text
                    if title != None:
                        title = re.sub('\([0-9]*\)', '', title)
                        title = title.strip()
                        tvEvent.eventName = title
                    else:
                        tvEvent.eventName = ""
                    
                if child.tag == 'startTime':
                    if child.text != None:
                        tvEvent.startTime = int(child.text)
                    else:
                        tvEvent.startTime = 0
                    
                if child.tag == 'endTime':
                    if child.text != None:
                        endtime = int(child.text)
                    else:
                        endtime = 0
                    
            tvEvent.description = self._getDetailedInfo(channel.channelNumber, tvEvent.startTime)
            tvEvent.duration = max(0, endtime - tvEvent.startTime)
            tvEvent.tvtvId = channel.tvtvId
            tvEvent.channelNumber = channel.channelNumber
            epg.append(tvEvent)
        
        return epg
    
    
    def _getDetailedInfo(self, channelNumber, startTime):
        query = self.configuration['receiver']['queries']['getDetailedInfo']
        query = query.replace('{$1}', str(channelNumber))
        query = query.replace('{$2}', str(startTime))

        r = requests.get(self._webserverhost() + query)
        xmldata = r.text.encode("latin-1")

        detailedInfo = ''
        e = ElementTree.fromstring(xmldata)
        for event in e.findall('event'):
            for child in event.iter():
                if child.tag == 'longInfo':
                    if child.text != None:
                        detailedInfo = child.text.replace('<br>', '\n')

        return detailedInfo
    
    
    def getTimerEvents(self):
        timerEvents = list()
        
        query = self.configuration['receiver']['queries']['getTimerEvents']
        r = requests.get(self._webserverhost() + query)
        xmldata = r.text.encode("latin-1")
        e = ElementTree.fromstring(xmldata)
        for event in e.findall('timerevent'):
            e = TimerEvent()
            for child in event.iter():
                if child.tag == 'channelName':
                    e.channelName = child.text

                if child.tag == 'startTime':
                    e.startTime = int(child.text)
                    
                if child.tag == 'timerNo':
                    e.id = int(child.text)
                    
            timerEvents.append(e)
        
        return timerEvents
    
    
    def getCurrentChannelNumber(self):
        query = self.configuration['receiver']['queries']['getDeviceInfo']
        r = requests.get(self._webserverhost() + query)
        xmldata = r.text.encode("latin-1")
        e = ElementTree.fromstring(xmldata)
        for d in e.findall('deviceInfo'):
            for c in d.iter():
                if c.tag == "liveChannel":
                    return int(c.text.split('.')[1])
        
        return 0
    
    
    def getCurrentChannelName(self):
        return self.getTvChannel(self.getCurrentChannelNumber())
    

    def isTvMode(self):
        query = self.configuration['receiver']['queries']['getDeviceInfo']
        r = requests.get(self._webserverhost() + query)
        xmldata = r.text.encode("latin-1")
        e = ElementTree.fromstring(xmldata)
        for d in e.findall('deviceInfo'):
            for c in d.iter():
                if c.tag == "liveChannel":
                    return c.text.split('.')[0] == "TV"
        
        return False
    
    
    def getProductType(self):
        query = self.configuration['receiver']['queries']['getDeviceInfo']
        r = requests.get(self._webserverhost() + query)
        xmldata = r.text.encode("latin-1").encode("latin-1")
        e = ElementTree.fromstring(xmldata)
        for d in e.findall('deviceInfo'):
            for c in d.iter():
                if c.tag == "productType":
                    return c.text
        
        return ""
    
    
    def isInStandby(self):
        query = self.configuration['receiver']['queries']['getDeviceInfo']
        r = requests.get(self._webserverhost() + query)
        xmldata = r.text.encode("latin-1")
        e = ElementTree.fromstring(xmldata)
        for d in e.findall('deviceInfo'):
            for c in d.iter():
                if c.tag == "VirtualStandBy":
                    return c.text == "TRUE"
        
        return False
    
    
    def getXmlInterfaceVersion(self):
        query = self.configuration['receiver']['queries']['getDeviceInfo']
        r = requests.get(self._webserverhost() + query)
        xmldata = r.text.encode("latin-1")
        e = ElementTree.fromstring(xmldata)
        for d in e.findall('deviceInfo'):
            for c in d.iter():
                if c.tag == "xmlInterfaceVersion":
                    return int(c.text)
                        
        return 0
    
    
    def setTimer(self, channelnumber, starttime, tvtvid):
        url = self._webserverhost() + self.configuration['receiver']['commands']['setTimer']
        url = url.replace('{$1}', str(channelnumber))
        url = url.replace('{$2}', str(starttime))
        url = url.replace('{$3}', str(tvtvid))
        
        r = requests.get(url)
        
        if "Ok" in r.text:
            return True
        else:
            print(r.text.encode("latin-1"))
            
        return False

        
    def deleteTimer(self, channelName, starttime):
        timerid = -1
        
        timerEvents = self.getTimerEvents()
        for t in timerEvents:
            if t.channelName == channelName and t.startTime == starttime:
                timerid = t.id
                break
        
        if timerid >= 0:
            url = self._webserverhost() + self.configuration['receiver']['commands']['deleteTimer']
            url = url.replace('{$1}', str(timerid))
            
            r = requests.get(url)
            
            return "Ok" in r.text
        
        return False
