from Products.DataCollector.plugins.CollectorPlugin import CollectorPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap
from ZenPacks.community.zenJavaApp.lib.JavaAppScan import *
from ZenPacks.community.zenJavaTerracotta.Definition import *
from Products.ZenUtils.Utils import zenPath,prepId
import socket



__doc__ = """TerracottaClientMap

TerracottaClientMap detects Terracotta Clients on a per-JVM basis.

This version adds a relation to associated ipservice, javaapp, and terracottaserver components.

"""


class TerracottaClientMap(CollectorPlugin):
    """Map JMX Client output table to model."""
    compname = "os"
    constr = Construct(TerracottaClientDefinition)
    relname = constr.relname
    modname = constr.zenpackComponentModule
    baseid = constr.baseid
    transport = "python"
    # use for validation
    deviceProperties = CollectorPlugin.deviceProperties + (
                    'zJmxUsername', 'zJmxPassword',
                    'zJavaAppPortRange' 'manageIp',
                    'zJavaAppScanTimeout',
                    'zJolokiaProxyHost',
                    'zJolokiaProxyPort'
                    )
    
    def getRelatedBeans(self, path):
        '''find mbeans related to this one'''
        attributes = []
        data = {}
        output = self.scan.proxy.proxy.request(type='list', path=path.replace(':','/'))
        if 'value' in output.keys(): attributes = output['value']
        for attr in attributes['attr'].keys():
            attr = str(attr)
            if 'BeanName' in attr: 
                try: data[attr] = str(self.scan.proxy.proxy.request(type='read', mbean=path, attribute=attr)['value']['objectName'])
                except:  data[attr] = ''
        return data
    
    def parseEnvironmentInfo(self, info):
        '''convert JVM environment info to dictionary'''
        lines = info.split('\n')
        envinfo = {}
        for l in lines:
            try:
                tmp = l.split(':')
                envinfo[str(tmp[0])] = str(tmp[1]).lstrip().rstrip()
            except: pass
        return envinfo
    
    def findJMXPort(self, info):
        '''try to determine the JMX (RMI) port based on args'''
        # first see if the port is explicitly mentioned
        keys = ['JMX_SYSTEM_CONNECTOR_PORT']
        for k in keys:
            if k in info.keys():  
                if len(info[k]) > 0: return int(info[k])
        # secondly see if it can be pulled out of the args
        if 'BrokerArgs' in info.keys():
            args = info['BrokerArgs']
            findString = '-rmiRegistryPort '
            start = args.find(findString)+len(findString)
            args = args[start:]
            port = args.split(' ')[0]
            return int(port)
        return None
    
    def collect(self, device, log):
        ''''''
        log.info("collecting %s for %s." % (self.name(), device.id))
        self.scan = JavaAppScan(device.manageIp, device.zJavaAppPortRange, 
                                device.zJmxUsername, device.zJmxPassword,
                                device.zJolokiaProxyHost, device.zJolokiaProxyPort,
                                device.zJavaAppScanTimeout)
        self.scan.evalPorts()
        TCSERVERMBEAN = 'org.terracotta:type=Terracotta Server,name=DSO'
        TCCLIENTMBEAN = 'atxg:component-name=AppServer,subcomponent-name=EhCacheManager,mbean-name=TerracottaClient'
        output = []
        for port, status in self.scan.portdict.items():
            if status['isGood'] is True and self.scan.beanExists(port,TCSERVERMBEAN) is True:
                #log.debug("got entry for %s: %s" % (port, status))
                result = self.scan.getBeanAttributeValues(port=port, mbean=TCSERVERMBEAN, attributes=['ClientLiveObjectCount'], protocol=status['protocol'])
                objects = self.scan.proxy.parseDictToList(result['ClientLiveObjectCount'])
                for ob in objects:
                    info = {
                        'id': '',
                        'server': device.id,
                        'serverport': port,
                        'serveruser':  self.scan.username,
                        'serverpassword': self.scan.password,
                        'serverauth': status['useAuth'],
                        'serverprotocol': status['protocol'],
                        'node': '', # should be client host name
                        'nodeport': '', # client JMX port
                        'nodeid': '', # identifier following the "/" character
                        'nodeip': '', #socket.gethostbyname(info['node']), # remote IP address
                        'nodeuser': None, # self.scan.username,
                        'nodepassword':  None, # self.scan.password,
                        'nodeauth': None, # status['useAuth'],
                        'nodeprotocol': None, # status['protocol'], # this can be overridden later if needed
                        'nodeavailable': False,
                        'channelID': str(ob['channelID']),
                        'TerracottaServerBeanName': str(ob['fullname']),
                        'TerracottaClientBeanName' : TCCLIENTMBEAN,
                        }
                    # find related MBeans for this channelID
                    info.update(self.getRelatedBeans(ob['fullname']))
                    # examine the L1InfoBeanName MBean path
                    data = self.scan.proxy.parseData(info['L1InfoBeanName'])
                    # find node name and ID
                    info['node'], info['nodeid'] = data['node'].split('/')
                    name = "%s_%s_%s" % (self.baseid, info['node'], info['nodeid'])
                    info['id'] = prepId(name)
                    # find node IP address
                    info['nodeip'] = socket.gethostbyname(info['node'])
                    # attempt to find node port
                    try:
                        envoutput = self.scan.getBeanAttributeValues(port=port, mbean=data['fullname'], attributes=['Environment'], protocol=status['protocol'])
                        info['nodeport'] = self.findJMXPort(self.parseEnvironmentInfo(envoutput['Environment']))
                    except:  pass
                    output.append(info)
        return output
    
    def process(self, device, results, log):
        ''''''
        log.info("The plugin %s returned %s results." % (self.name(), len(results)))
        if len(results) == 0: return None
        rm = self.relMap()
        for result in results:
            om = self.objectMap(result)
            om.setTerracottaserver = om.server
            om.setJavaapp = om.nodeport
            om.setIpservice = om.nodeport
            #om.setClientSettings = 'blah'
            rm.append(om)
            log.debug(om)
        return rm

