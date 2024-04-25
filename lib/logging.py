import pprint, datetime


def prettyPrint(json):
    logMessage(pprint.pprint(json))


def logMessage(msg):
    print(f"LOG:{datetime.datetime.now()}: {msg}")

def errorMessage(msg):
    print("ERR: {}".format(msg))


def quitMessage(msg):
    print("ERR: {}".format(msg))
    quit()