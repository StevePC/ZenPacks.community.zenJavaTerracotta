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
    
    def postprocess(self, result, om, log):
        ''''''
        om.server = self.device.id
        om.dropIfPassive = 'blah'
        om.updateClientSettings = 'blah'
        return om

