import shellvars, shlex, subprocess, urllib2, uuid, os, time
from ConfigParser import SafeConfigParser

# define the path constant
_scriptLoc = os.path.dirname(os.path.realpath(__file__))
ARTIFACTS_PATH = os.path.realpath("%s/../../../delivery/artifacts" % _scriptLoc)

# define the docker client
_docker_host = os.environ.get("DOCKER_HOST", "tcp://dockerhost:2375")
DOCKER_CLIENT = "docker -H %s" % _docker_host


# set env vars via sh script, then get them here
def getEnvVars():
  envSh = 'env.sh'
  envVars = shellvars.get_vars(envSh)
  return envVars

# run careless command without throwing error if failed
def runCarelessCommand(command):
  commandParts = shlex.split(command)
  p = subprocess.Popen(commandParts, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
  out, err = p.communicate()
  return (p.returncode, out, err)

# run sensitive command, throw error if failed
def runCommand(command, errorMessage = None):
  result = runCarelessCommand(command)
  code = result[0]
  if code != 0:
    if errorMessage is not None:
      result = result + (errorMessage,)
    raise RuntimeError(result)
  return result

# access an URL
def isUrlAccessible(url):
  accessible = False
  try:
    c = urllib2.urlopen(url)
    c.read()
    c.close()
    accessible = True
  except IOError:
    accessible = False
  return accessible


# get the server ready url to check
def _getServerReadyUrl(rc):
  return rc.general.server_ready_url

def checkServerReady(rc, serverHostname, serverPort, warmup = 0):
  url = _getServerReadyUrl(rc)

  if url:
    url = url % (serverHostname, serverPort)
    # server must start to server connecting service in 1 minute
    for _ in range(0, 20):
      if isUrlAccessible(url):
        # url is ready
        # the server need more time to warm up, waiting
        if warmup > 0: 
          time.sleep(warmup)
        return True
      time.sleep(3)
  return False


# output http headers with status code
HTTP_CODE_200 = "200 OK"
HTTP_CODE_500 = "500 Internal Server Error"
def httpResponse(statusCode=HTTP_CODE_200, contentType="text/plain"):
  print "Content-Type: ", contentType
  print "Status: ", statusCode
  print

# generate a random string (may be a random UUID with underscore)
def generateRandom():
  random = str(uuid.uuid4())
  random = random.replace('-', '_')
  return random

# debug function
def debug(text):
  httpResponse()
  print "----- debug ------"
  print text
  print "------------------"


import threading, signal, errno, fcntl
from contextlib import contextmanager

class Lock:
  TIME_OUT = 60 * 60  # 1 hour
  LOCK_LOCATION = '/var/lock'
  
  @contextmanager
  def _timeout(self, seconds):
    # only main thread can set and handle signal
    if not isinstance(threading.current_thread(), threading._MainThread):
      yield
      return

    def timeout_handler(signum, frame):
      pass

    original_handler = signal.signal(signal.SIGALRM, timeout_handler)

    try:
      signal.alarm(seconds)
      yield
    finally:
      signal.alarm(0)
      signal.signal(signal.SIGALRM, original_handler)

  def __init__(self, room):
    lockFile = '%s/.__docker_%s__' % (self.LOCK_LOCATION, room)
    self.filename = lockFile
    # This will create it if it does not exist already
    self.handle = open(self.filename, 'w')
  
  # Bitwise OR fcntl.LOCK_NB if you need a non-blocking lock 
  def acquire(self):
    with self._timeout(self.TIME_OUT):
      try:
        fcntl.flock(self.handle, fcntl.LOCK_EX)
        return True
      except IOError as e:
        if e.errno != errno.EINTR:
          raise e
        return False
      
  def release(self):
    with self._timeout(self.TIME_OUT):
      try:
        fcntl.flock(self.handle, fcntl.LOCK_UN)
        return True
      except IOError as e:
        if e.errno != errno.EINTR:
          raise e
        return False
      
  def __del__(self):
    self.handle.close()
