from datetime import datetime, timedelta
from string import Template

class DeltaTemplate(Template):
    delimiter = "%"

def getFriendlyTime(datetimeObject : datetime, date=True, seconds=True):
    if date and seconds:
        return datetimeObject.strftime("%m/%d %H:%M:%S")
    if date:
        return datetimeObject.strftime("%m/%d %H:%M")
    if seconds:
        return datetimeObject.strftime("%H:%M:%S")
    return datetimeObject.strftime("%H:%M")

def getFriendlyRemainingTime(remaining : timedelta):
    strDiv = ""
    div = divmod(remaining.days * 3600*24 + remaining.seconds, 60)
    if div[0] != 0:
        divMin = divmod(div[0], 60)
        if divMin[0] != 0:
            strDiv = strDiv + str(divMin[0]) + "h "
        if divMin[1] != 0:
            strDiv = strDiv + str(divMin[1]) + "m "
    if div[1] != 0:
        strDiv = strDiv + str(div[1]) + "s"
    return strDiv

def getFriendlyBTCAmount(sats):
    return str(round(sats/100000000,2)) + " BTC"

