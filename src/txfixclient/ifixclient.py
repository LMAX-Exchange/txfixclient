#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from zope.interface import Interface, Attribute


class IFixClient(Interface):

    name = Attribute("A short string identifying this chat service (eg, a hostname)")

    def marketDataRequest():
        "Issue a market data request to a single instrument"


    def marketDataUpdateRequest( ):
        "Issue a market data request to a multiplr instruments"
