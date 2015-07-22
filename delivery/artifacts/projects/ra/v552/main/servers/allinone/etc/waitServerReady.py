#!/usr/bin/env python

import sys, urllib2, time
from ConfigParser import SafeConfigParser

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

# get check url
def getUrl(conf_path):
  config = SafeConfigParser()
  config.read('%s/run.conf' % (conf_path))
  return config.get('general', 'server_ready_url')


url = None
warmup = 0
if len(sys.argv) > 0:
  script_path = sys.argv[0]
  script_loc = "/".join(script_path.split('/')[:-1])

  (productName, productVersion, branch, productPort, warmup) = ("ra", "552", "main", 8080, 180)
  productPort = int(productPort)
  warmup = int(warmup)
  url = getUrl("%s/.." % script_loc)

if url:
  url = url % ('localhost', productPort)
  print "waiting server to be ready ..."
  for _ in range(0, 5):
    if isUrlAccessible(url):
      print "server url %s is ready" % url
      # the server need more time to warm up, waiting
      if warmup > 0: 
        print "product is warming up ..."
        time.sleep(warmup)
      sys.exit()
    print "server url %s is not ready, waiting ..." % url
    time.sleep(3)
else:
  print "Usage %s url" % sys.argv[0]

sys.exit(1)
