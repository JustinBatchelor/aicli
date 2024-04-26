import pprint, datetime


def prettyPrint(json):
    print(f"LOG:{datetime.datetime.now()}: {pprint.pprint(json)}")


def logMessage(msg):
    print(f"LOG:{datetime.datetime.now()}: {msg}")

def errorMessage(msg):
    print(f"Error:{datetime.datetime.now()}: {msg}")

def quitMessage(msg):
    logMessage(f"Error{datetime.datetime.now()}:{msg}")
    quit()