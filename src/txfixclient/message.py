# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from twisted.logger import Logger
from datetime import datetime
log = Logger()


class FixMessage(object):

    def __init__(self):
        self.length = 0
        self.checksum = None
        self.type = None
        self.created_at = datetime.utcnow()
        self.recieved_at = None

        self._data = []
        self._complete = False
        self._delimiter = '\x01'

    def get_tag(self, id):
        '''take a tag id and returns a list of tags of that id'''
        tags = []

        id = int(id)
        for tag in self._data:
            if tag[0] is id:
                tags.append(tag)
        return tags

    def append_tag(self, id, val):

        if id is 8:  # start new message
            if self._data:
                raise Exception('Last message hasnt been dealt with fully',
                                self._message)

            self._data.append((int(id), val))

        if id is 9:
            if not self._data:
                raise Exception('We should have a message if we are at tag 9')
            self._data.append((int(id), val))

        if id is 10:
            # TODO check body length
            chksum = self.calc_checksum()
            if chksum != val:
                raise Exception(
                    "Incorrect CheckSum: Actually '%s', Should be '%s'" %
                    (val, chksum)
                    )
            else:
                self._data.append((int(id), val))

        if id is 35:
            self.type = str(val)

        if id not in [8, 9, 10]:
            self._data.append((int(id), val))

        self._update_length()

    def append_tags(self, tags):
        for tag in tags:
            self.append_tag(tag[0], tag[1])

    def as_string(self):
        return self.as_binary().replace(self._delimiter, b'|')

    def _update_length(self):
        msg_str = ''
        for tag in self._data:
            k = tag[0]
            v = tag[1]
            if k in [8, 9, 10]:
                continue
            msg_str = msg_str + self._tag_to_string(k, v)
        self.length = len(msg_str)
        for i in range(0, len(self._data)):
            if self._data[i][0] is 9:
                self._data[i] = (9, str(self.length))

    def as_binary(self):
        msg_str = ''
        meta = {}
        for tag in self._data:
            k = tag[0]
            v = tag[1]
            if k in [8, 9, 10]:
                meta[k] = v
                continue
            msg_str = msg_str + self._tag_to_string(k, v)
        meta[9] = self.length  # set BodyLength
        msg_str = self._tag_to_string(8, meta[8]) + \
            self._tag_to_string(9, meta[9]) + msg_str
        meta[10] = self.calc_checksum()
        msg_str = msg_str + self._tag_to_string(10, meta[10])
        return msg_str

    def calc_checksum(self):
        total = 0
        for tag in self._data:
            if tag[0] is not 10:
                tag_str = self._tag_to_string(tag[0], tag[1])
                for char in list(tag_str):
                    total += ord(str(char))
        self.checksum = str(total % 256).zfill(3)

        return self.checksum

    def _tag_to_string(self, k, v):
        return "%s=%s%s" % (k, v, self._delimiter)
