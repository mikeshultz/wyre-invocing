""" Drain invoice accounts """
import argparse
from enum import IntEnum

from .db import get_paid_invoices, update_invoice_drained, unlock_account
from .common import STD_GAS_PRICE, VALUE_TX_GAS, get_web3
from .log import get_logger

log = get_logger(__name__)


class PaidColumns(IntEnum):
    INVOICE_ID = 0
    ADDRESS = 1
    TOTAL = 2
    PAID = 3


def drain_paid_invoice_accounts(web3, destination_account):
    invoices = get_paid_invoices()

    total_drained = 0

    for inv in invoices:

        invoice_id = inv[PaidColumns.INVOICE_ID]
        address = inv[PaidColumns.ADDRESS]
        total = inv[PaidColumns.TOTAL]
        paid = inv[PaidColumns.PAID]

        if paid < total:
            log.error("Attempted to drain unpaid account")
            continue

        balance = web3.eth.getBalance(address)
        tx_fee = VALUE_TX_GAS * STD_GAS_PRICE

        if balance <= tx_fee:
            log.warning("Balance of account {} is {}. Less than the cost of gas({}).".format(
                address,
                balance,
                VALUE_TX_GAS * STD_GAS_PRICE
            ))
        elif balance > 0:
            nonce = web3.eth.getTransactionCount(address)

            try:
                privkey = unlock_account(address)
            except ValueError as err:
                if 'MAC' not in str(err):
                    raise err
                log.error('Unable to unlock account {}.  Invalid decryption key?'.format(address))
                continue

            tx = {
                'from': address,
                'to': destination_account,
                'gasPrice': STD_GAS_PRICE,
                'gas': VALUE_TX_GAS,
                'value': balance - tx_fee,
                'nonce': nonce
            }
            print('tx', tx)
            raw_tx = web3.eth.account.signTransaction(tx, privkey)
            print('raw_tx', raw_tx.rawTransaction)
            txhash = web3.eth.sendRawTransaction(raw_tx.rawTransaction)
            log.debug("Sent transaction {}".format(txhash))
            receipt = web3.eth.waitForTransactionReceipt(txhash)
            log.debug("Transaction mined {}".format(txhash))
            if receipt.status != 1:
                log.error("Drain transaction failed! {}".format(txhash))
            else:
                total_drained += balance
                if not update_invoice_drained(invoice_id, txhash):
                    log.error('Drained invoice was not updated in the DB!')
    return total_drained


def main(argv=None):
    """ CLI interaction """
    parser = argparse.ArgumentParser(description='API Daemon')
    parser.add_argument(
        'account',
        metavar='ADDRESS',
        type=str,
        nargs=1,
        help='Address of a destination Ethereum account'
    )
    parser.add_argument(
        '--network',
        type=int,
        help='Ethereum network ID to connect to (default: 4 (rinkeby))'
    )
    parser.add_argument(
        '--json-rpc',
        type=str,
        default='http://localhost:8545/',
        help='Ethereum JSON-RPC endpoint (default: http://localhost:8545/)'
    )
    args = parser.parse_args(argv)

    web3 = get_web3(args.network or args.json_rpc)

    total_drained = drain_paid_invoice_accounts(web3, args.account[0])
    if total_drained > 0:
        log.info("Successfully withdrew {} Ether".format(
            web3.fromWei(total_drained, 'ether')
        ))
    else:
        log.debug('noop')
