""" Balance updater """
import time
import argparse
from enum import IntEnum

from .db import get_unpaid_invoices, update_invoice_paid
from .common import INFURA_RATE_LIMIT, get_web3
from .log import get_logger

log = get_logger(__name__)


class UnpaidColumns(IntEnum):
    INVOICE_ID = 0
    ADDRESS = 1
    TOTAL = 2
    PAID = 3


def update_balances(web3):
    """ Update the paid field of invoice """
    invoices = get_unpaid_invoices()

    updated = 0

    for inv in invoices:

        time.sleep(INFURA_RATE_LIMIT)  # be nice to Infura

        invoice_id = inv[UnpaidColumns.INVOICE_ID]
        address = inv[UnpaidColumns.ADDRESS]
        total = inv[UnpaidColumns.TOTAL]
        paid = inv[UnpaidColumns.PAID]

        balance = web3.eth.getBalance(address)

        log.info("Checking invoice #{}.".format(invoice_id))

        if balance > paid:
            log.debug("Invoice total: {} -- Paid: {} -- Balance: {}".format(
                total,
                paid,
                balance
            ))
            if not update_invoice_paid(invoice_id, balance):
                log.erro("Update of invoice balance failed")
            else:
                updated += 1

    return updated


def main(argv=None):
    """ CLI interaction """
    parser = argparse.ArgumentParser(description='Updater Daemon')
    parser.add_argument(
        '--network',
        type=int,
        help='Ethereum network ID to connect to'
    )
    parser.add_argument(
        '--json-rpc',
        type=str,
        default='http://localhost:8545/',
        help='Ethereum JSON-RPC endpoint (default: http://localhost:8545/)'
    )
    args = parser.parse_args(argv)

    web3 = get_web3(args.network or args.json_rpc)

    while True:
        count = update_balances(web3)
        log.debug("Updated {} invoice balances".format(count))
        time.sleep(5)
