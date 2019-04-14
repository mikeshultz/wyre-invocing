""" Ethereum account functionality """
from Crypto.Random import get_random_bytes
from eth_account import Account


def create_account():
    """ Create an account and return address and pk in a tuple """
    eth_account = Account()
    account = eth_account.create(get_random_bytes(32))
    return (account.address, account.privateKey)
