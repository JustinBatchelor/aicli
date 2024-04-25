import pprint, datetime


def prettyPrint(json):
    print(f"LOG:{datetime.datetime.now()}: {pprint.pprint(json)}")


def logMessage(msg):
    print(f"LOG:{datetime.datetime.now()}: {msg}")

def errorMessage(msg):
    print("ERR: {}".format(msg))


def quitMessage(msg):
    print("ERR: {}".format(msg))
    quit()