# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#

"""
Helper class for handling FIX xml spec files

http://www.quickfixengine.org/


> spec = Spec('../specs/FIX42.xml')
"""

import xml.etree.ElementTree as ET


# TODO: look at http://stackoverflow.com/questions/13637934/python-trying-to-override-getattr-for-dynamically-added-class-but-only-sor

class Spec(object):

    def __init__(self, file=None):
        self.file = file
        self.root = None
        if self.file:
            self.load_spec(self.file)

    def load_spec(self, file):
        tree = ET.parse(file)
        self.root = tree.getroot()

    def search_components(self, component, attrib, query):
        if self.root is None:
            raise Exception('spec not loaded')
        result = (item for item in self.root.find(component)
                  if item.attrib[attrib] == query).next()
        return result

    def get_field_by_num(self, num):
        return self.search_components('fields', 'number', str(num))

    def get_field_by_name(self, name):
        return self.search_components('fields', 'name', str(name))

    def get_message_by_msgtype(self, msgtype):
        return self.search_components('messages', 'msgtype', str(msgtype))

    def get_message_by_name(self, name):
        return self.search_components('messages', 'name', str(name))

    def get_header_by_name(self, name):
        return self.search_components('header', 'name', str(name))

    def list_components(self, component):
        if self.root is None:
            raise Exception('spec not loaded')
        result = [item for item in self.root.find(component)]
        return result

    def list_fields(self):
        return self.list_components('fields')

    def list_messages(self):
        return self.list_components('messages')

    def list_header(self):
        return self.list_components('header')


    def _get_component_children(self, message):
        if hasattr(message, '_children'):
            result = [field for field in message._children]
        else:
            result = []
        return result

    def get_fields_for_message_msgtype(self, msgtype, required=None):
        '''
        @required = 'Y' or 'N'
        '''
        msg = self.get_message_by_msgtype(msgtype)
        fields = self._get_component_children(msg)
        if required is not None:
            result = [field.attrib for field in fields if field.attrib['required'] == required]
        else:
            result = [field.attrib for field in fields]
        return result

    def get_fields_for_message_name(self, name, required=None):
        msg = self.get_message_by_name(name)
        fields = self._get_component_children(msg)
        if required is not None:
            result = [field.attrib for field in fields if field.attrib['required'] == required]
        else:
            result = [field.attrib for field in fields]
        return result

    def get_fields_for_message(self, message, required=None):
        msg = (item for item in self.root.find('messages')
                  if item.attrib == message.attrib).next()
        return [field.attrib for field in self._get_component_children(msg)]


    def list_header_required(self, required=None):
        '''
        @required = 'Y' or 'N'
        '''
        headers = self.list_components('header')
        if required is not None:
            result = [header.attrib for header in headers if header.attrib['required'] == required]
        else:
            result = [header.attrib for header in headers]
        return result

# vim: set ft=python ts=4 sw=4 tw=0 et :
