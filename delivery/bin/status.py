#!/usr/bin/env python

from .DeliveryStatus import DeliveryStatus
import sys

if len(sys.argv) > 1:
    statusDb = sys.argv[1] # db file path
    operation = sys.argv[2] # get, set
    task = sys.argv[3] # build, image
    (productName, productVersion, branch, serverType, dbType) = (sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])
    if len(sys.argv) > 9:
        buildNumber = sys.argv[9]
    else:
        buildNumber = "0"

    status = DeliveryStatus(statusDb, productName, productVersion, branch, serverType, dbType)

    task = task.lower()
    if task == 'build':
        task = status.getBuildTask()
    elif task == 'image':
        task = status.getImageTask()

    if operation == 'get':
        buildNumber = status.getLatestBuildNumber(task)
        print buildNumber 
    elif operation == 'set':
        status.addBuildNumber(task, buildNumber)
