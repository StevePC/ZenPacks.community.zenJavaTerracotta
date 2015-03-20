from ZenPacks.community.zenJavaApp.lib.CommonMBeanMap import *
from ZenPacks.community.zenJavaTerracotta.Definition import *
import socket


__doc__ = """TerracottaClientMap

TerracottaClientMap detects Terracotta Clients on a per-JVM basis.

This version adds a relation to associated ipservice, javaapp, and terracottaserver components.

"""


class TerracottaClientMap(CommonMBeanMap):
    """Map JMX Client output table to model."""
    
    constr = Construct(TerracottaClientDefinition)
    relname = constr.relname
    modname = constr.zenpackComponentModule
    baseid = constr.baseid
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
        TCSERVERMBEAN = 'org.terracotta:type=Terracotta Server,name=DSO'
        TCCLIENTMBEAN = 'atxg:component-name=AppServer,subcomponent-name=EhCacheManager,mbean-name=TerracottaClient'
        
        self.scan = JavaAppScan(device.manageIp, device.zJavaAppPortRange, 
                                device.zJmxUsername, device.zJmxPassword,
                                device.zJolokiaProxyHost, device.zJolokiaProxyPort,
                                device.zJavaAppScanTimeout)
        self.scan.evalPorts()
        output = []
        for jmx in self.scan.portdict.values():
            # use these connection parameters
            self.scan.proxy.setJMX(jmx)
            if jmx.connected is True and self.scan.proxy.beanExists(TCSERVERMBEAN) is True:
                result = self.scan.proxy.getBeanAttributeValues(mbean=TCSERVERMBEAN, attributes=['ClientLiveObjectCount'])
                objects = self.scan.proxy.parseDictToList(result['ClientLiveObjectCount'])
                for ob in objects:
                    info = {
                        'id': '',
                        'server': device.id,
                        'serverport': jmx.port,
                        'serveruser':  jmx.user,
                        'serverpassword': jmx.password,
                        'serverauth': jmx.auth,
                        'serverprotocol': jmx.protocol,
                        'enabled' : jmx.connected,
                        'javaversion': jmx.javaversion,
                        'vendorname': jmx.vendorname,
                        'vendorproduct': jmx.vendorproduct,
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
                        envoutput = self.scan.proxy.getBeanAttributeValues(mbean=data['fullname'], attributes=['Environment'])
                        info['nodeport'] = self.findJMXPort(self.parseEnvironmentInfo(envoutput['Environment']))
                    except:  pass
                    output.append(info)
        return output
    
    def postprocess(self, result, om, log):
        ''''''
        om.setTerracottaserver = om.server
        om.setJavaapp = om.nodeport
        om.setIpservice = om.nodeport
        #om.setClientSettings = 'blah'
        return om

