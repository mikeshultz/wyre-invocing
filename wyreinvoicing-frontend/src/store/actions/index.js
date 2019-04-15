
// Types
export const ADD_INVOICE = 'ADD_INVOICE'
export const INITIAL_INVOICES = 'INITIAL_INVOICES'

export function addInvoice(invoice) {
  return {
    type: ADD_INVOICE,
    payload: invoice
  }
}

export function initialInvoices(invoices) {
  return {
    type: INITIAL_INVOICES,
    payload: invoices
  }
}
