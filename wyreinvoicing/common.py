""" Common constants and functions """
import flask
from decimal import Decimal
from web3 import Web3

INFURA_RATE_LIMIT = 1
STD_GAS_PRICE = int(1e9)
VALUE_TX_GAS = 21000
MAX_INVOICE = 1000000000000000000000000
JSONRPC_ENDPOINTS = {
    # Mainnet
    1: 'https://mainnet.infura.io/v3/0757bb8408244a1e929cafad8a05fd16',
    # Rinkeby
    4: 'https://rinkeby.infura.io/v3/0757bb8408244a1e929cafad8a05fd16',
    # Local testing
    9999: 'http://localhost:8545'
}

cached_web3 = None


class WyreJSONEncoder(flask.json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 == 0:
                return int(o)
            else:
                return float(o)

        return flask.json.JSONEncoder.default(self, o)


def get_web3_provider(endpoint):
    if endpoint.startswith('ws'):
        return Web3.WebsocketProvider(endpoint)
    elif endpoint.startswith('http'):
        return Web3.HTTPProvider(endpoint)
    elif endpoint.startswith('ipc'):
        return Web3.IPCProvider(endpoint)
    else:
        raise Exception('Unsupported JSON-RPC endpoint')


def get_web3(network):
    """ Get a web3 instance """
    global cached_web3

    if cached_web3 is not None:
        return cached_web3

    if type(network) == int:
        network = JSONRPC_ENDPOINTS.get(network)

    if type(network) != str:
        raise Exception('Invalid endpoint/network')

    return Web3(get_web3_provider(network))
