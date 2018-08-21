txfixclient
===========

A very basic FIX (Financial Information eXchange) Protocol client to collect
performance stats.

- https://en.wikipedia.org/wiki/Financial_Information_eXchange

To use this as it is you will need to be a customer of LMAX Exchange. If you
wish to use this against another FIX engine then you can modify the messages to
suit that platform.

Quickfix XML spec files ara available at http://www.quickfixengine.org/

.. image:: https://travis-ci.org/LMAX-Exchange/txfixclient.svg?branch=master
    :target: https://travis-ci.org/LMAX-Exchange/txfixclient

.. image:: https://www.quantifiedcode.com/api/v1/project/b2954a0977f44934a413a2be030f114a/badge.svg
  :target: https://www.quantifiedcode.com/app/project/b2954a0977f44934a413a2be030f114a
  :alt: Code issues

Installation
------------

::

    pip install git+https://github.com/lmax-exchange/txfixclient.git#egg=txfixclient

Usage
-----

::

    twistd -n \
        txfixclient \
        --hostname fix-marketdata.london-demo.lmax.com \
        --port 443 \
        --spec ./specs/FIX44.xml \
        --target_comp_id <targetcompid> \
        --sender_comp_id <sendercompid> \
        --password <password> \
        --heartbeat_int 30 \
        --instrument_id 4001 \
        --market_depth 1 \
        --statsdir ./stats \
        --metrics_interval 60

You can make it busyspin the epoll reactor if you change the timeout in doPoll() within twisted to = 0


https://github.com/twisted/twisted/blob/twisted-18.7.0/src/twisted/internet/epollreactor.py#L211

Thanks
------

Written using the Twisted framework for async networking in Python.

- https://twistedmatrix.com/

Stats recorded by HdrHistogram_py

- https://github.com/HdrHistogram/HdrHistogram_py/

