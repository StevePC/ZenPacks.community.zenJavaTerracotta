from ZenPacks.community.ConstructionKit.ClassHelper import *

def TerracottaServergetEventClassesVocabulary(context):
    return SimpleVocabulary.fromValues(context.listgetEventClasses())

class TerracottaServerInfo(ClassHelper.TerracottaServerInfo):
    ''''''

from ZenPacks.community.zenJavaTerracotta.datasources.TerracottaServerDataSource import *
def TerracottaServerRedirectVocabulary(context):
    return SimpleVocabulary.fromValues(TerracottaServerDataSource.onRedirectOptions)

class TerracottaServerDataSourceInfo(ClassHelper.TerracottaServerDataSourceInfo):
    ''''''

def TerracottaClientgetEventClassesVocabulary(context):
    return SimpleVocabulary.fromValues(context.listgetEventClasses())

class TerracottaClientInfo(ClassHelper.TerracottaClientInfo):
    ''''''


