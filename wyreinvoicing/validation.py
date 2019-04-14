""" Data validators """


def validate_invoice(invoice_object):
    """ Validate the the invoice_object meets the database spec """
    try:
        # One requirement, seems reasonable
        assert isinstance(invoice_object, dict)
        assert 'total' in invoice_object
        return True
    except AssertionError:
        return False
