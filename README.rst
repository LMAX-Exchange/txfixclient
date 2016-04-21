txfixclient
===========

A very basic FIX (Financial Information eXchange) Protocol client to collect
performance stats.

- https://en.wikipedia.org/wiki/Financial_Information_eXchange

To use this as it is you will need to be a customer of LMAX Exchange. If you
wish to use this against another FIX engine then you can modify the messages to
suit that platform.

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
        --spec LMAX-FIX-MarketData-API-QuickFix-DataDictionary.xml \
        --target_comp_id <targetcompid> \
        --sender_comp_id <sendercompid> \
        --password <password> \
        --heartbeat_int 30 \
        --instrument_id 4001 \
        --market_depth 1 \
        --statsdir ./stats \
        --metrics_interval 60

Thanks
------

Written using the Twisted framework for async networking in Python.

- https://twistedmatrix.com/

Stats recorded by HdrHistogram_py

- https://github.com/HdrHistogram/HdrHistogram_py/

