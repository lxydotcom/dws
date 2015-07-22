import os
from .utils import ARTIFACTS_PATH

class RunContext:
  def __init__(self, productName, productVersion, branch, serverType, dbType):
    self._setup(productName, productVersion, branch, serverType, dbType)

  def _setup(self, productName, productVersion, branch, serverType, dbType):
    self.productName = productName
    self.productVersion = productVersion
    self.branch = branch
    self.serverType = serverType
    self.dbType = dbType

    # basic context
    self.artifactsPath = ARTIFACTS_PATH
    self.projectRootPath = "%s/projects" % self.artifactsPath

    self.projectId = "%s_v%s_%s" % (self.productName, self.productVersion, self.branch)
    self.projectPath = "%s/%s/v%s/%s" % (self.projectRootPath, self.productName, self.productVersion, self.branch)

    self.serverId = "%s_%s" % (self.projectId, self.serverType)
    self.serverPath = "%s/servers/%s" % (self.projectPath, serverType)

    self.dbId = "%s_%s" % (self.serverId, self.dbType)
    self.dbPath = "%s/deliver/run/dbs/%s" % (self.serverPath, self.dbType)

    # read the run conf to form the attributes
    self._readConf()

  # read run configure recursively to load all config, access these config via object reference
  # for example, rc=RunContext(..), rc.general.server_ready_url means option server_ready_url in section general in some run.conf file
  def _readConf(self):
    from ConfigParser import SafeConfigParser
    self.__config = SafeConfigParser()

    # read run conf recursively, the later will override the former
    path = self.projectRootPath
    pathSegment = (".", self.productName, "v%s" % self.productVersion, self.branch, "servers/%s" % self.serverType)
    if self.dbType:
      pathSegment += ("deliver/run/dbs/%s" % self.dbType,)

    for segment in pathSegment:
      path += "/" + segment
      self.__config.read("%s/run.conf" % path)

  def __getattr__(self, key):
    # self attribute
    if key in self.__dict__:
      return self.__dict__[key]

    # return run conf option as context attribute
    # for example, rc=RunContext(..), rc.general.serverReadyUrl = "http://localhost/"
    class Section:
      def __init__(self, config, section):
        self.__config = config
        self.__section = section

      def __getattr__(self, key):
        option = key
        return self.__config.get(self.__section, option)

    section = key
    if self.__config.has_section(section):
      return Section(self.__config, section)
