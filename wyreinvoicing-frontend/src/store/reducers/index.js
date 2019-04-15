import { ADD_INVOICE, INITIAL_INVOICES } from '../actions'

const initialState = {
  invoices: []
}

export default function main(state = initialState, action) {
  switch (action.type) {
    case ADD_INVOICE:
      console.debug('reducer ADD_INVOICE', action)
      return {
        ...state,
        invoices: [...state.invoices, action.payload]
      }
    case INITIAL_INVOICES:
      console.debug('INITIAL_INVOICES', action)
      return {
        ...state,
        invoices: action.payload
      }
    default:
      return state
  }
}
