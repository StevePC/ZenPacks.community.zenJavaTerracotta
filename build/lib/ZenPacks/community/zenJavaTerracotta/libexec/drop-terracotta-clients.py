#!/usr/bin/env python
import Globals
from optparse import OptionParser
import re
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from transaction import commit

class DropTerracottaClients(ZenScriptBase):
    def __init__(self):
        ZenScriptBase.__init__(self, connect=True)

    def buildOptions(self):
        ''''''
        ZenScriptBase.buildOptions(self)
        self.parser.add_option('--server', dest='server', help='Remote server host')

    def run(self):
        ''''''
        device = self.findDevice(self.options.server)
        if device is not None:
            try:
                for c in device.os.terracottaClients(): self.delComponent(c)
            except: pass
        print "Completed drop of terracotta clients on %s" % self.options.server
    
    def delComponent(self, c):
        ''''''
        try:
            c.manage_deleteComponent()
            commit()
        except:
            try:
                c.getPrimaryParent()._delObject(c.id)
                commit()
            except: print "    ",c.id,"could not be deleted"

    def findDevice(self, deviceName):
        """ find and return dmd device object if exists
        """
        for device in self.dmd.Devices.getSubDevices():
            if re.search(deviceName,device.id) != None:
                return device
        return None

if __name__ == "__main__":
    u = DropTerracottaClients()
    u.run()

