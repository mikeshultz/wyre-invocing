import psycopg2
from functools import wraps
from .accounts import create_account
from .crypt import encrypt, decrypt
from .validation import validate_invoice
from .common import InvoiceState
from .log import get_logger

EXPECTED_TABLES = ['state', 'invoice']
INITIAL_SQL = """
CREATE TABLE state (
    state_id SERIAL PRIMARY KEY,
    name VARCHAR
);

INSERT INTO state (state_id, name) VALUES (0, 'created');
INSERT INTO state (state_id, name) VALUES (1, 'expired');
INSERT INTO state (state_id, name) VALUES (2, 'partial');
INSERT INTO state (state_id, name) VALUES (3, 'paid');

CREATE TABLE account (
    account_id SERIAL PRIMARY KEY,
    address VARCHAR (42) NOT NULL,
    salt TEXT NOT NULL,
    private_key TEXT NOT NULL
);

CREATE TABLE invoice (
    invoice_id SERIAL PRIMARY KEY,
    state_id INT REFERENCES state (state_id) NOT NULL DEFAULT 0,
    account_id INT REFERENCES account (account_id) NOT NULL,
    created TIMESTAMP DEFAULT now(),
    total NUMERIC(24),
    paid NUMERIC(24),
    drain_txhash VARCHAR(66)
);

"""

log = get_logger(__name__)
cached_conn = None


def create_initial(conn):
    """ Creates the schema and default data for the DB, if necessary """

    with conn.cursor() as curs:

        # Check for the expected tables
        try:
            for tbl in EXPECTED_TABLES:
                curs.execute(
                    "SELECT 1 "
                    "FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = %s",
                    (tbl,)
                )
                assert curs.rowcount == 1
        except AssertionError:
            log.info('Creating database schema...')
            curs.execute(INITIAL_SQL)
            conn.commit()


def get_connection():
    """ Return a psycopg2 connection

    Use the PostgreSQL env vars to configure.
    See: https://www.postgresql.org/docs/current/static/libpq-envars.html
    """
    global cached_conn

    if cached_conn is None:
        cached_conn = psycopg2.connect("")
        create_initial(cached_conn)

    return cached_conn


def provide_connection(fn):
    """ Decorator to provide a Postgres connection as the kwarg `conn` """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        kwargs['connection'] = get_connection()
        return fn(*args, **kwargs)
    return wrapper


@provide_connection
def insert_account(private_key, address, connection):
    """ Get a specific invoice """

    salt, encrypted_pk = encrypt(private_key)

    with connection.cursor() as cursor:

        cursor.execute(
            "INSERT INTO account (address, salt, private_key) "
            " VALUES (%s, %s, %s)"
            " RETURNING (account_id);",
            (address, salt, encrypted_pk)
        )
        if cursor.rowcount < 1:
            connection.rollback()
            return []

        account_id = cursor.fetchone()
        connection.commit()
        return account_id


@provide_connection
def unlock_account(address, connection):
    """ Get an account """

    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT account_id, address, salt, private_key"
            " FROM account"
            " WHERE address = %s",
            (address, )
        )
        if cursor.rowcount < 1:
            return None

        account = cursor.fetchone()
        private_key = decrypt(account[2], account[3])
        return private_key


@provide_connection
def get_invoice(invoice_id, connection):
    """ Get a specific invoice """

    if type(invoice_id) != int:
        log.warning('Provided invoice_id is not an integer')
        return None

    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT invoice_id, state_id, address, total, paid"
            " FROM invoice"
            " JOIN account USING (account_id)"
            " WHERE invoice_id = %s",
            (invoice_id,)
        )
        if cursor.rowcount < 1:
            return None

        return cursor.fetchone()


@provide_connection
def get_invoices(connection):
    """ Get all invoices """
    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT invoice_id, state_id, address, total, paid"
            " FROM invoice"
            " JOIN account USING (account_id)"
        )
        if cursor.rowcount < 1:
            return []

        return cursor.fetchall()


@provide_connection
def add_invoice(invoice_object, connection):
    """ Add an invoice to the DB """
    if not validate_invoice(invoice_object):
        log.info("Failed to validate incoming invoice")
        return []

    address, privkey = create_account()
    account_id = insert_account(privkey, address)
    if not account_id:
        log.error("Failed to create and insert account")
        return []

    with connection.cursor() as cursor:

        cursor.execute(
            "INSERT INTO invoice (account_id, total, paid)"
            " VALUES (%s, %s, %s)"
            " RETURNING (invoice_id);",
            (account_id, invoice_object.get('total'), 0)
        )
        if cursor.rowcount < 1:
            connection.rollback()
            return []

        invoice_id = cursor.fetchone()
        connection.commit()
        return invoice_id


@provide_connection
def get_unpaid_invoices(connection):
    """ Get unpaid invoices """
    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT a.account_id, a.address, i.total, i.paid"
            " FROM account a"
            " JOIN invoice i"
            "   ON i.account_id = a.account_id AND i.paid < i.total"
        )
        if cursor.rowcount < 1:
            return []

        return cursor.fetchall()


@provide_connection
def get_paid_invoices(connection):
    """ Get unpaid invoices """
    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT i.invoice_id, a.address, i.total, i.paid"
            " FROM account a"
            " JOIN invoice i"
            "   ON i.account_id = a.account_id AND i.paid >= i.total"
            "       AND i.drain_txhash is null"
        )
        if cursor.rowcount < 1:
            return []

        return cursor.fetchall()


@provide_connection
def update_invoice_paid(invoice_id, balance, connection):
    """ Update the invoice account balance """

    if type(invoice_id) != int:
        log.warning('Provided invoice_id is not an integer')
        return None

    if type(balance) != int:
        log.warning('Provided balance is not an integer')
        return None

    with connection.cursor() as cursor:

        # Get the invoice
        cursor.execute(
            "SELECT invoice_id, state_id, total, paid"
            " FROM invoice WHERE invoice_id = %s;",
            (invoice_id,)
        )

        if cursor.rowcount < 1:
            connection.rollback()
            return False

        invoice = cursor.fetchone()

        state_id = invoice[1]
        total = invoice[2]
        log.debug('Total: {}, Paid: {}'.format(total, balance))
        if balance > 0 and balance < total:
            log.debug('Setting invoice state PARTIAL')
            state_id = InvoiceState.PARTIAL
        elif balance >= total:
            log.debug('Setting invoice state PAID')
            state_id = InvoiceState.PAID

        cursor.execute(
            "UPDATE invoice SET"
            " paid = %s,"
            " state_id = %s"
            " WHERE invoice_id = %s;",
            (balance, state_id, invoice_id)
        )
        if cursor.rowcount < 1:
            connection.rollback()
            return False

        connection.commit()
        return True


@provide_connection
def update_invoice_drained(invoice_id, txhash, connection):
    """ Get unpaid invoices """

    if type(invoice_id) != int:
        log.warning('Provided invoice_id is not an integer')
        return None

    if type(txhash) != str:
        log.warning('Provided transaction hash is not the right type')
        return None

    if len(txhash) != 66:
        log.warning('Provided transaction hash is not the right length')
        return None

    with connection.cursor() as cursor:

        cursor.execute(
            "UPDATE invoice SET"
            " drain_txhash = %s"
            " WHERE invoice_id = %s;",
            (txhash, invoice_id)
        )
        if cursor.rowcount < 1:
            connection.rollback()
            return False

        connection.commit()
        return True
