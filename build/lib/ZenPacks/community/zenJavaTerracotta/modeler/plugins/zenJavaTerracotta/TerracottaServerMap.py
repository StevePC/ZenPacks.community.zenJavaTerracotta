from Products.DataCollector.plugins.CollectorPlugin import CollectorPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenUtils.Utils import prepId
from ZenPacks.community.zenJavaApp.lib.JavaAppScan import *
from ZenPacks.community.zenJavaApp.lib.CommonMBeanMap import *
from ZenPacks.community.zenJavaTerracotta.Definition import *

__doc__ = """TerracottaServerMap

TerracottaServerMap detects Terracotta Servers on a per-JVM basis.

This version adds a relation to associated ipservice, javaapp, and terracottaclient components.

"""

class TerracottaServerMap(CommonMBeanMap):
    """Map JMX Client output table to model."""
    
    constr = Construct(TerracottaServerDefinition)
    relname = constr.relname
    modname = constr.zenpackComponentModule
    baseid = constr.baseid
    
    searchMBean = 'org.terracotta:type=Terracotta Server,name=DSO'
    
    def process(self, device, results, log):
        log.info("The plugin %s returned %s results." % (self.name(), len(results)))
        rm = self.relMap()
        for result in results:
            om = self.objectMap(result)
            om.server = device.id
            #om.setTerracottaport = om.port
            om.dropIfPassive = 'blah'
            om.setJavaapp = ''
            om.setIpservice = om.port
            om.updateClientSettings = 'blah'
            rm.append(om)
            log.debug(om)
        return rm

