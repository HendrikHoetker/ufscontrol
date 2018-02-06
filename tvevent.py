'''
Created on 16.01.2016

@author: hendrik
'''

import hashlib

class TVEvent(object):
    id = 0
    channelNumber = -1
    channelName = ''
    eventName = ''
    startTime = -1
    duration = -1
    description = ''
    tvShowId = -1
    tvtvId = -1

    def getMD5(self):
        return hashlib.md5((self.channelName + self.eventName + str(self.startTime)).encode('utf-8')).hexdigest()
    
    def getUniqueId(self):
        return hashlib.md5((self.eventName + self.description).encode('utf-8')).hexdigest()
