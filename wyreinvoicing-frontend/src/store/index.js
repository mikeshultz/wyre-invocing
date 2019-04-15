import { createStore } from 'redux'
import main from './reducers'

export const store = createStore(main)
