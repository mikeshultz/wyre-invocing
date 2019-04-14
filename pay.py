import sys
import argparse
from web3 import Web3


def main(argv=sys.argv[1:]):
    """ Make a simple payment to be run on the test node using an
    already-unlocked account
    """

    parser = argparse.ArgumentParser(description='Test payment script')
    parser.add_argument(
        'destination_account',
        metavar='ADDRESS',
        type=str,
        nargs=1,
        help='Destination Ethereum account address'
    )
    parser.add_argument(
        'amount_in_wei',
        metavar='WEI',
        type=int,
        nargs=1,
        help='The amount to send in wei'
    )
    args = parser.parse_args(argv)

    web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

    assert int(web3.version.network) > 100, 'This is a test script.'

    tx = {
        'from': web3.eth.accounts[0],
        'to': args.destination_account[0],
        'gas': 21000,
        'gasPrice': int(1e9),
        'value': args.amount_in_wei[0]
    }
    txhash = web3.eth.sendTransaction(tx)
    print('Sending transaction {}'.format(txhash))
    receipt = web3.eth.waitForTransactionReceipt(txhash)
    assert receipt.status == 1, 'Transaction failed!'
    print(receipt)


if __name__ == '__main__':
    main()
