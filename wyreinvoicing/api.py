""" API Server """
import sys
import time
import argparse
from subprocess import Popen
from flask import Flask, request, jsonify
from .db import get_invoice, get_invoices, add_invoice
from .common import WyreJSONEncoder
from .log import get_logger

log = get_logger(__name__)
app = Flask(__name__)
app.json_encoder = WyreJSONEncoder


def make_response(results=None, success=True):
    """ Build a response object for success """
    resp = {
        'success': success
    }
    resp.update({'result': results})
    return jsonify(resp)


def db_invoice_to_json(dbi):
    return {
        'invoice_id': dbi[0],
        'state_id': dbi[1],
        'address': dbi[2],
        'total': dbi[3],
        'paid': dbi[4]
    }


@app.route('/invoice', methods=['GET'])
def api_show_invoices():
    invoices = get_invoices()
    return make_response(list(map(db_invoice_to_json, invoices)))


@app.route('/invoice', methods=['POST'])
def api_add_invoice():
    assert request.content_type == 'application/json', 'Wrong content-type'

    incoming_json = request.get_json()

    invoice_result = add_invoice(incoming_json)

    if invoice_result:
        return make_response(invoice_result[0], success=True)
    else:
        return make_response(success=False)


@app.route('/invoice/<invoice_id>', methods=['GET'])
def api_invoice(invoice_id):
    res = get_invoice(invoice_id)
    return make_response(db_invoice_to_json(res))


def main(argv=None):
    """ CLI interaction """
    parser = argparse.ArgumentParser(description='API Daemon')
    parser.add_argument('--bind', type=str, default='127.0.0.1:8080',
                        help='The bind address to listen on')

    args = parser.parse_args(argv)

    gunicornd = Popen(['gunicorn', '-b', args.bind, 'wyreinvoicing.api:app'],
                      stdin=None, stdout=None)

    try:
        while gunicornd.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        gunicornd.terminate()
        sys.exit(0)
