from flask import request
from collections import OrderedDict
from . import utils
from .DeliveryStatus import DeliveryStatus

def getBuildNumbers():
  output = OrderedDict()
  try:
    # get the query parameters
    productName = request.args.get("product_name", "")
    productVersion = request.args.get("product_version", "")
    branch = request.args.get("branch", "")
    serverType = request.args.get("server_type", "")
    dbType = request.args.get("db_type", "")
    lastBuildNumber = request.args.get("last_build_number", "")

    from .RunContext import RunContext
    rc = RunContext(productName, productVersion, branch, serverType, dbType)

    # get the latest built image num from status db
    status = DeliveryStatus(productName, productVersion, branch, serverType, dbType)
    latestBuildNumber = status.getLatestBuildNumber(status.getImageTask())
    
    # find the later build nums after the last build num
    if not lastBuildNumber:
      lastBuildNumber = "0"
    laterBuildNumbers = status.getLaterBuildNumbers(status.getImageTask(), lastBuildNumber)
    laterBuildNumbers = ",".join(laterBuildNumbers)


    # output the later/latest build num
    if int(latestBuildNumber) > int(lastBuildNumber):
      output["result"] = "successful"
      output["later_build_numbers"] = laterBuildNumbers
      output["latest_build_number"] = latestBuildNumber
    else:
      output["result"] = "none"
  except Exception as e:
    output["result"] = "failed"
    output["error="] = str(e).replace('\n', r'\n')

  return output  