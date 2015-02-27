from ZenPacks.community.ConstructionKit.BasicDefinition import *
from ZenPacks.community.ConstructionKit.Construct import *
from ZenPacks.community.zenJavaApp.Definition import getMBeanDef, addMBeanRelations

import logging
log = logging.getLogger('zen.zenhub')


ROOT = "ZenPacks.community"
BASE = "zenJavaTerracotta"
VERSION = Version(3, 0, 0)

def updateClientSettings(ob, test=''): 
    '''attempted workaround'''
    for x in ob.device().os.terracottaClients():   x.setClientSettings()

def getMapValue(ob, datapoint, map):
    ''' attempt to map number to data dict'''
    try: return map[int(ob.getRRDValue(datapoint))]
    except:
        if ob.monitor is False:  return map[3]
        else: return map[-1]

def getClientReportedCount(ob): 
    '''get number of clients per RRD'''
    try: return int(ob.getRRDValue('checkClients_clients'))
    except:  return 0

def getClientCount(ob): return len(ob.getChannelIDs())

def getChannelIDs(ob): 
    '''return list of client ids'''
    ids = []
    for x in ob.device().os.terracottaClients():  ids.append(x.channelID)
    return ids

def getDisconnectedClients(ob, ids):
    '''return any difference between known ids and currently connected ids'''
    knownIDs = ob.getChannelIDs()
    badIDs = []
    for k in knownIDs:
        if k not in ids:  badIDs.append(k)
    devIDs = []
    for c in ob.device().os.terracottaClients():
        ref = "%s/%s" % (c.node,c.nodeid)
        if c.channelID in badIDs:  devIDs.append(ref)
    return devIDs

def getServerMode(ob):
    ''''''
    if ob.isPassive() is True: return 'PASSIVE'
    else: return 'ACTIVE'

def isPassive(ob):
    '''return whether server is active or passive'''
    from ZenPacks.community.zenJavaApp.lib.JavaAppScan import JavaAppScan
    try: 
        scan = JavaAppScan(ob.device().manageIp, ob.device().zJavaAppPortRange, ob.user, ob.password, 
                           ob.device().zJolokiaProxyHost, ob.device().zJolokiaProxyPort, ob.device().zJavaAppScanTimeout)
        result = scan.getBeanAttributeValues(port=ob.port, mbean='org.terracotta.internal:name=Terracotta Server,type=Terracotta Server', 
                                             attributes=['PassiveStandby'], protocol=ob.protocol)
        return result['PassiveStandby']
    except: 
        return False

def dropIfPassive(ob, test=''):
    ''' drop all terracotta clients from device if server changes to passive'''
    from transaction import commit
    passive = ob.isPassive()
    if passive is True:
        log.info("PASSIVE SERVER REMOVING %s clients" % len(ob.device().os.terracottaClients()))
        try:
            for c in ob.device().os.terracottaClients(): 
                try: 
                    c.manage_deleteComponent()
                    commit()
                except:
                    try: 
                        c.getPrimaryParent()._delObject(c.id)
                        commit()
                    except: log.warn("%s could not be deleted" % c.id)
        except: pass
    return passive


TCSDATA = getMBeanDef(VERSION, ROOT, BASE, 'TerracottaServer','Terracotta Server', 'Terracotta Servers')
TCSDATA['componentData']['properties']['getClientCount'] = getReferredMethod('Clients', 'getClientCount')
TCSDATA['componentData']['properties']['getServerMode'] = getReferredMethod('Mode', 'getServerMode')
TCSDATA['componentData']['properties']['server'] = addProperty('Server', default='id', switch='-s',override=True, isReference=True,optional='false')
TCSDATA['componentData']['properties']['user'] =  addProperty('User', switch='-u')
TCSDATA['componentData']['properties']['password'] =  addProperty('Password', switch='-w')
TCSDATA['componentData']['properties']['port'] =  addProperty('Port', switch='-p')
TCSDATA['componentData']['properties']['protocol'] =  addProperty('Protocol', switch='-j')
TCSDATA['componentData']['properties']['eventClass'] = getEventClass('/App/Terracotta')
TCSDATA['createDS'] = True
TCSDATA['cmdFile'] = 'check-terracotta-server.py'
TCSDATA['datapoints'] = ['clients']
TCSDATA['componentMethods'] = [isPassive, getServerMode, getClientCount, getChannelIDs, getDisconnectedClients, dropIfPassive, getClientReportedCount, updateClientSettings]

TerracottaServerDefinition = type('TerracottaServerDefinition', (BasicDefinition,), TCSDATA)
addMBeanRelations(TerracottaServerDefinition)


def setClientSettings(ob, test=''):
    log.info('setClientSettings %s' % ob.id)
    cjav = ob.javaapp()
    if cjav is not None and cjav.monitor is True:
        available = ob.setNodeAvailable(test)
        ob._setPropValue('nodeavailable', available)
        ob._setPropValue('nodeauth',cjav.auth)
        ob._setPropValue('nodeuser',cjav.user)
        ob._setPropValue('nodeprotocol',cjav.protocol)
        passwd = cjav.getPassword('password')
        ob._setPropValue('nodepassword',passwd)
    return ob

def setNodeAvailable(ob, test=''):
    '''test if remote node supports the ClusterConnectionStatus attributes'''
    log.info('setNodeAvailable %s' % ob.id)
    from ZenPacks.community.zenJavaApp.lib.JolokiaProxyHandler import JolokiaProxyHandler
    proxy = JolokiaProxyHandler()
    cjav = ob.javaapp()
    mbean = 'atxg:component-name=AppServer,subcomponent-name=EhCacheManager,mbean-name=TerracottaClient'
    if cjav is not None and cjav.monitor is True:
        proxy.connect(host=cjav.device().manageIp, port=cjav.port, user=cjav.user, password=cjav.getPassword('password'), protocol=cjav.protocol)
        output = proxy.proxy.request(type='read', mbean=mbean ,attribute='ClusterConnectionStatusValue')
        if 'value' in output.keys():  return True
    return False

def getClientSettings(ob): return ob#.javaapp()
    
def getNodeAvailable(ob): return ob#.javaapp()

def getMapValue(ob, datapoint, map):
    ''' attempt to map number to data dict'''
    try:
        return map[int(ob.getRRDValue(datapoint))]
    except:
        if ob.monitor is False:  return 'DISABLED'
        else: return 'UNKNOWN'

cacheManagerStatusMap = { 0: 'NOT_CLUSTERED', 1: 'CONNECTED', 2: 'CONNECTING',  3: 'DISCONNECTED'}
clusterConnectionStatusMap = { 0: 'UNITIALIZED', 1: 'ALIVE', 2: 'SHUTDOWN'}

def getCacheManagerState(ob): return ob.getMapValue('CacheManagerStatusValue_CacheManagerStatusValue', ob.cacheManagerStatusMap)
def getClusterConnectionState(ob): return ob.getMapValue('ClusterConnectionStatusValue_ClusterConnectionStatusValue', ob.clusterConnectionStatusMap)


TerracottaClientDefinition = type('TerracottaClientDefinition', (BasicDefinition,), {
        'version' : VERSION,
        'zenpackbase': BASE,
        'component' : 'TerracottaClient',
        'componentData' : {
                          'singular': 'Terracotta Client',
                          'plural': 'Terracotta Clients',
                          'displayed': 'node', # component field in Event Console
                          'primaryKey': 'node',
                          'properties': { 
                                        # Client
                                        'channelID': addProperty('Channel ID'),
                                        'TerracottaServerBeanName' : addProperty('TerracottaServerBeanName'),
                                        'TerracottaClientBeanName' : addProperty('TerracottaClientBeanName'),
                                        'EnterpriseTCClientBeanName': addProperty('EnterpriseTCClientBeanName'),
                                        'InstrumentationLoggingBeanName': addProperty('InstrumentationLoggingBeanName'),
                                        'L1InfoBeanName': addProperty('L1InfoBeanName'),
                                        'L1DumperBeanName': addProperty('L1DumperBeanName'),
                                        'L1OperatorEventsBeanName': addProperty('L1OperatorEventsBeanName'),
                                        'RuntimeLoggingBeanName': addProperty('RuntimeLoggingBeanName'),
                                        'RuntimeOutputOptionsBeanName': addProperty('RuntimeOutputOptionsBeanName'),
                                        # Server side      
                                        'server' : addProperty('Server'), 
                                        'serverport' : addProperty('Server Port',default='9520', optional=False),
                                        'serverauth': addProperty('Server Authenticate', default=False, ptype='boolean'),
                                        'serveruser' : addProperty('Server User'),
                                        'serverpassword' : addProperty('Server Password', ptype='password'),
                                        'serverprotocol': addProperty('Protocol'),
                                        # Client Side
                                        'node' : addProperty('Node'),
                                        'nodeip' : addProperty('Node IP'),  
                                        'nodeport' : addProperty('Node Port', default='8686'),
                                        'nodeid' : addProperty('Node ID'),
                                        'nodeauth': addProperty('Node Authenticate', default=False, ptype='boolean'),
                                        'nodeuser' : addProperty('Node User'),
                                        'nodepassword' : addProperty('Node Password', ptype='password'),
                                        'nodeavailable': addProperty('Node Status Available', default=False, ptype='boolean'),
                                        'nodeprotocol': addProperty('Protocol'),
                                        'eventClass' : getEventClass('/App/Terracotta'),
                                        'getCacheManagerState' : getReferredMethod('Cache Manager Status', 'getCacheManagerState'),
                                        'getClusterConnectionState' : getReferredMethod('Cluster Connection Status', 'getClusterConnectionState'),
                                        },
                          },
        'componentAttributes' : {'cacheManagerStatusMap': cacheManagerStatusMap, 'clusterConnectionStatusMap': clusterConnectionStatusMap,},                                                                  
        'componentMethods' : [setClientSettings, getClientSettings, setNodeAvailable, getNodeAvailable, getMapValue, getCacheManagerState, getClusterConnectionState],
        }
)

addDefinitionSelfComponentRelation(TerracottaClientDefinition,
                          'terracottaclients', ToMany, 'ZenPacks.community.zenJavaTerracotta.TerracottaClient','server',
                          'terracottaserver',  ToOne, 'ZenPacks.community.zenJavaTerracotta.TerracottaServer', 'server',
                          "Terracotta Server")

addDefinitionDeviceComponentRelation(TerracottaClientDefinition, 'manageIp', 'nodeip',
                          'terracottaclients', ToMany, 'ZenPacks.community.zenJavaTerracotta.TerracottaClient','nodeport',
                          'javaapp',  ToOne, 'ZenPacks.community.zenJavaApp.JavaApp', 'port',
                          "Java App")

addDefinitionDeviceComponentRelation(TerracottaClientDefinition,'manageIp', 'nodeip',
                          'terracottaclients', ToMany, 'ZenPacks.community.zenJavaTerracotta.TerracottaClient','nodeport',
                          'ipservice',  ToOne, 'Products.ZenModel.IpService', 'port',
                          'IP Service')

