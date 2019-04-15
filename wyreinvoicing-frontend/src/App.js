import React, { Component } from 'react';
import '../node_modules/milligram/dist/milligram.min.css'
import './App.css';

import Invoices from './components/Invoices';
import AddInvoice from './components/AddInvoice';

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Invoicing</h1>
          <p>
            Ultra simple proof of concept invoicing app that generates unique Ethereum payment accounts for each invoice.
          </p>
        </header>
        <section id="invoices-section">
          <Invoices />
        </section>
        <section id="add-invoice-section">
          <AddInvoice />
        </section>
      </div>
    );
  }
}

export default App;
