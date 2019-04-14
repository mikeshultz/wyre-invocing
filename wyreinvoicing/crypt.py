import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from .log import get_logger

log = get_logger(__name__)


def read_keyfile(file):
    if file is None:
        return None
    try:
        with open(file, 'rb') as _file:
            return _file.read()
    except FileNotFoundError:
        return None


def write_keyfile(file, data):
    with open(file, 'wb') as _file:
        _file.write(data)


ENC_KEY_FILE = os.environ.get('ENC_KEY_FILE')
ENC_KEY = read_keyfile(ENC_KEY_FILE)


def create_keyfile():
    """ Create a keyfile to be used to encrypt/decrypt data from the DB """
    assert ENC_KEY is None, 'Key exists at {}!'.format(ENC_KEY)
    log.info("Creating keyfile at {}".format(ENC_KEY_FILE))
    bs = get_random_bytes(16)
    write_keyfile(ENC_KEY_FILE, bs)


def encrypt(data):
    """ Encrypt data to be inserted into the DB with AES-256 """
    assert len(ENC_KEY) == 16, 'Invalid key file. Should be 16 bytes.'

    salt = get_random_bytes(16)
    key = salt + ENC_KEY
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    enc_data = ''.join([cipher.nonce.hex(), tag.hex(), ciphertext.hex()])
    # log.debug('nonce|tag|cypertext == {}|{}|{}'.format(cipher.nonce.hex(), tag.hex(), ciphertext.hex()))
    return salt.hex(), enc_data


def decrypt(salt, data):
    """ Decrypt data from the DB """
    assert len(ENC_KEY) == 16, 'Invalid key file. Should be 16 bytes.'

    nonce = bytes.fromhex(data[:32])
    tag = bytes.fromhex(data[32:64])
    ciphertext = bytes.fromhex(data[64:])
    salt = bytes.fromhex(salt)
    # log.debug('nonce|tag|cypertext == {}|{}|{}'.format(data[:32], data[32:64], data[64:]))
    key = salt + ENC_KEY
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
