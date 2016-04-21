"""
foo
"""
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.logger import Logger
from txfixclient.message import FixMessage

from zope.interface import Interface
from zope.interface import implementer
from datetime import datetime

log = Logger()


class _PauseableMixin:
    paused = False

    def pauseProducing(self):
        self.paused = True
        self.transport.pauseProducing()

    def resumeProducing(self):
        self.paused = False
        self.transport.resumeProducing()
        self.dataReceived(b'')

    def stopProducing(self):
        self.paused = True
        self.transport.stopProducing()


class FixTagReceiver(Protocol, _PauseableMixin):
    """
    takes fix data from the wire and decodes it then calls a methof to pass it
    to the main service
    """

    _buffer = b''
    _busyReceiving = False

    MAX_TAG_LENGTH = 500
    delimiter = b'\x01'

    def dataReceived(self, data):
        if self._busyReceiving:
            self._buffer += data
            return
        try:
            self._busyReceiving = True
            self._buffer += data
            while self._buffer and not self.paused:
                try:
                    tag, self._buffer = self._buffer.split(self.delimiter, 1)
                except ValueError:
                    if len(self._buffer) > self.MAX_TAG_LENGTH:
                        tag, self._buffer = self._buffer, b''
                        return self.tagLengthExceeded(tag)
                    return
                else:
                    tagLength = len(tag)
                    if tagLength > self.MAX_TAG_LENGTH:
                        exceeded = tag + self.delimiter + self._buffer
                        self._buffer = b''
                        return self.tagLengthExceeded(exceeded)
                    why = self.tagReceived(tag)
                    if (why or self.transport and
                            self.transport.disconnecting):
                        return why
        finally:
            self._busyReceiving = False

    def tagReceived(self, tag):
        '''
        Override this for notification when each complete tag string is
        received.
        '''
        raise NotImplementedError

    def tagLengthExceeded(self, msg):
        raise Exception(
            'MAX_TAG_LENGTH %s exceeded: %s' %
            (self.MAX_TAG_LENGTH, msg)
        )


class FixMessageReceiver(FixTagReceiver):
    # Twisted stuff

    encoding = 'latin1'

    def __init__(self):
        self._message = None

    def reset(self):
        self._message = None

    def connectionMade(self):
        log.debug("connection successful")
        self.factory.clientConnected(self)

    def dataSend(self, msg):
        self.transport.write(msg)

    def sendMessage(self, msg):
        self.dataSend(msg.as_binary())

    def tagReceived(self, tag):
        self.handleTag(tag)

    def handleTag(self, tag):
        key, val = tag.split('=')
        key = int(key)

        if key is 8:  # start new message
            if self._message:
                raise Exception('Last message hasnt been dealt with fully',
                                self._message)

            self._message = FixMessage()
            self._message.append_tag(int(key), val)

        if key is 9:
            if not self._message:
                raise Exception('We should have a message if we are at tag 9')
            self._message.append_tag(int(key), val)

        if key is 10:
            # TODO check body length
            self._message.append_tag(int(key), val)
            if self._message.checksum != val:
                raise Exception(
                    "Incorrect CheckSum: Recieved '%s', Should be '%s'" %
                    (val, self._message.checksum)
                    )
            else:
                message = self._message
                self.reset()
                self.messageReceived(message)

        if key not in [8, 9, 10]:
            self._message.append_tag(int(key), val)

    def messageReceived(self, message):
        message.recieved_at = datetime.utcnow()
        self.factory.handleMessage(message)


class IFixClientFactory(Interface):

    def clientConnected():
        '''
        '''

    def handleMessage(message):
        '''
        '''

    def sendMessage(message):
        '''
        '''


@implementer(IFixClientFactory)
class FixClientFactory(ReconnectingClientFactory):

    protocol = FixMessageReceiver

    def __init__(self, service):
        self.service = service

    #def clientConnectionFailed(self, connector, reason):
    #    log.debug("Connection Failed: {msg}", msg=reason.getErrorMessage())
    #    super(FixClientFactory, self).clientConnectionFailed(connector, reason)
#
#    def clientConnectionLost(self, connector, reason):
#        log.debug("Connection Lost: {msg}", msg=reason.getErrorMessage())
#        super(FixClientFactory, self).clientConnectionLost(connector, reason)

    def clientConnected(self, proto):
        self.resetDelay()
        self.service.clientConnected(proto)

    def handleMessage(self, message):
        self.service.handleMessage(message)

