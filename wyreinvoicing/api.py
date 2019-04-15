""" API Server """
import sys
import time
import argparse
from subprocess import Popen
from flask import Flask, request, jsonify
from flask_cors import CORS
from .db import get_invoice, get_invoices, add_invoice
from .common import WyreJSONEncoder
from .log import get_logger

log = get_logger(__name__)
app = Flask(__name__)
app.json_encoder = WyreJSONEncoder
CORS(app, resources={r"/*": {"origins": "*"}})


def make_headers(headers):
    default_headers = {
        'Content-Type': 'application/json',
    }
    if headers and isinstance(headers, dict):
        return default_headers.update(headers)
    return default_headers


def make_response(results=None, success=True, headers=None):
    """ Build a response object for success """
    resp = {
        'success': success
    }
    resp.update({'result': results})
    response = jsonify(resp)
    response.headers = make_headers(headers)
    return response


def db_invoice_to_json(dbi):
    return {
        'invoice_id': dbi[0],
        'state_id': dbi[1],
        'address': dbi[2],
        'total': str(dbi[3]),
        'paid': str(dbi[4])
    }


@app.route('/invoice', methods=['GET'])
def api_show_invoices():
    invoices = get_invoices()
    return make_response(list(map(db_invoice_to_json, invoices)))


@app.route('/invoice', methods=['POST'])
def api_add_invoice():
    assert 'application/json' in request.content_type, 'Wrong content-type'

    incoming_json = request.get_json()

    log.info("Adding new invoice")
    log.debug(incoming_json)

    invoice_result = add_invoice(incoming_json)

    if invoice_result:
        return make_response(invoice_result[0], success=True)
    else:
        return make_response(success=False)


@app.route('/invoice/<invoice_id>', methods=['GET'])
def api_invoice(invoice_id):

    try:
        invoice_id = int(invoice_id)
    except ValueError:
        return make_response(success=False)

    res = get_invoice(invoice_id)

    if not res:
        log.debug("Unable to fetch invoice #".format(invoice_id))
        return make_response(success=False)
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
