from zope.interface import implementer

from  twisted.logger import ILogObserver, formatEvent, FileLogObserver
from  twisted.logger import  formatEvent as flattenEvent


def formatEventAsString(event):
    eventText = flattenEvent(event)
    return eventText+"\n"

def passThroughFileLogObserver(outFile):

    def formatEvent(event):
        return formatEventAsString(event)

    return FileLogObserver(outFile, formatEvent)

