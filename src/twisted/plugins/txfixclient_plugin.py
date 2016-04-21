from twisted.application.service import ServiceMaker
TxFixClient = ServiceMaker(
    'txfixclient',
    'txfixclient.tap',
    'Run the Fix Client service',
    'txfixclient'
    )
