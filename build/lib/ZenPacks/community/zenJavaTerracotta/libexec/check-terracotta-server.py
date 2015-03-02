#!/usr/bin/env python
from ZenPacks.community.ConstructionKit.libexec.CustomCheckCommand import *
from ZenPacks.community.zenJavaApp.lib.JavaAppScan import JavaAppScan
import time

class TerracottaServerStatus(CustomCheckCommand):
    '''
        Check to test Terracotta server status (active or passive) and number of clients connected
    '''
    def __init__(self):
        CustomCheckCommand.__init__(self, connect=True)
        self.clients = 0
        self.missing = []
        self.state = "OK"
        self.serverState = "Active Primary"
        self.statusMap = {
                          'OK': {'val': 0, 'exit': 0 , 'msg': 'OK'}, 
                          'CRITICAL': {'val': 1, 'exit': 2 , 'msg': 'CRITICAL'}, 
                          'WARNING': {'val': 2, 'exit': 1 , 'msg': 'WARNING'}, 
                          }
        self.verbose = True
    
    def initialize(self):
        ''''''
        self.device = self.dmd.Devices.findDevice(self.options.server)
        self.scan = JavaAppScan(self.device.manageIp, self.device.zJavaAppPortRange, 
                                self.options.username, self.options.password, 
                                self.device.zJolokiaProxyHost, 
                                self.device.zJolokiaProxyPort, 
                                self.device.zJavaAppScanTimeout)
        self.scan.proxy.connect(self.options.server, self.options.tcpport, self.options.username, self.options.password, self.options.jmxprotocol)
        if self.scan.proxy.jmx.connected is True:
            standby = self.isPassiveStandby()
            if standby is False:
                self.state = "OK"
                self.numClients()
                self.findMissing()
            else: self.serverState = "Passive Standby"
        else:
            self.serverState = "UNKNOWN"
            self.message = "Terracotta Server Status UNKNOWN.  Check JMX Avaialability"
            self.status = 2
    
    def evalStatus(self):
        '''evaluate data before exit'''
        msg = "%s: Terracotta server is %s|clients=%s" % (self.state, self.serverState, self.clients)
        if len(self.missing) > 0:
            self.state = 'CRITICAL'
            msg = '%s: Terracotta server has lost connection to %s|clients=%s' % (self.state, ','.join(self.missing), self.clients)
        entry = self.statusMap[self.state]
        self.status = entry['exit']
        self.message = msg
    
    def isPassiveStandby(self):
        '''whether this server is a passive standby'''
        result = self.scan.getBeanAttributeValues(port=self.options.tcpport, 
                                             mbean='org.terracotta.internal:name=Terracotta Server,type=Terracotta Server', 
                                             attributes=['PassiveStandby'], 
                                             protocol=self.options.jmxprotocol)
        try: return data['PassiveStandby']
        except: return False
    
    def numClients(self):
        '''find number of currently connected clients'''
        result = self.scan.getBeanAttributeValues(port=self.options.tcpport, 
                                             mbean='org.terracotta:type=Terracotta Server,name=DSO', 
                                             attributes=['ClientLiveObjectCount'], 
                                             protocol=self.options.jmxprotocol)
        self.objects = self.scan.proxy.parseDictToList(result['ClientLiveObjectCount'])
        try: self.clients = len(self.objects)
        except: pass
    
    def findTerracottaServer(self):
        '''find this terracotta server component'''
        for c in self.device.os.terracottaServers():
            if c.port == self.options.tcpport:  return c
        return None
    
    def findMissing(self):
        '''return references to any missing clients'''
        self.findClientIDs()
        c = self.findTerracottaServer()
        if c is not None: 
            self.missing = c.getDisconnectedClients(self.findClientIDs())
    
    def findClientIDs(self):
        '''return list of client IDs'''
        ids = []
        for o in self.objects: ids.append(str(o['channelID']))
        return ids
    
    def buildOptions(self):
        '''runtime options'''
        ZenScriptBase.buildOptions(self)
        self.parser.add_option('-s','--server', dest='server', help='Remote server host')
        self.parser.add_option('-p','--tcpport', dest='tcpport', help='JMX Port', default=9520)
        self.parser.add_option('-j','--jmxprotocol', dest='jmxprotocol', help='JMX Protocol')
        self.parser.add_option('-u','--username', dest='username', help='User Name')
        self.parser.add_option('-w','--password', dest='password', help='Password' ,default='RMI')
        self.parser.add_option('-t','--timeout', dest='timeout', help='timeout', default=30)
        
if __name__ == "__main__":
    u = TerracottaServerStatus()
    u.run()
