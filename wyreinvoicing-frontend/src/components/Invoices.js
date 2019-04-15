import React, { Component } from 'react';
import { connect } from 'react-redux'
import Modal from 'react-modal';
import Web3 from 'web3';

import './Invoices.css';

import { initialInvoices } from '../store/actions'
import WyreAPI from '../api'
import { toBN, toWei, fromWeiToString } from '../utils'


function getStateIndicator(state_id) {
  switch(state_id) {
    case 1:
      return (<span className="state-indicator expired">Expired</span>);
    case 2:
      return (<span className="state-indicator partial">Partially Paid</span>);
    case 3:
      return (<span className="state-indicator paid">Paid</span>);
    case 0:
    default:
      return (<span className="state-indicator created">Created</span>);
  }
}

class Invoices extends Component {
  constructor(props) {
    super(props);

    this.state = {
      paymentModalIsOpen: false,
      paymentAddress: null,
      paymentAmountInEth: 0
    };

    // Demo provider
    this.web3 = new Web3('http://localhost:8545/');

    const that = this;
    // Refresh invoics every 3s
    setInterval(() => {
      that.refreshInvoices()
    }, 30000)
    
    this.openPayment = this.openPayment.bind(this);
    this.makePayment = this.makePayment.bind(this);
    this.handleAmountChange = this.handleAmountChange.bind(this);
  }

  componentDidMount() {
    this.refreshInvoices();
  }

  refreshInvoices() {
    console.debug('Refresing invoices...')
    const that = this;
    WyreAPI.getInvoices().then(invoices => {
      that.props.initialInvoices(invoices)
    });
  }

  openPayment(address, amount) {
    console.debug('openPayment()', address, amount)
    this.setState({
      paymentAddress: address,
      paymentModalIsOpen: true,
      paymentAmountInEth: amount
    })
  }

  makePayment() {
    const that = this;
    this.web3.eth.getAccounts().then(accounts => {
      const tx = {
        'from': accounts[0],
        'to': this.state.paymentAddress,
        'gas': 21000,
        'gasPrice': 1e9,
        'value': toWei(that.state.paymentAmountInEth)
      };
      console.debug('sending tx: ', tx)
      that.web3.eth.sendTransaction(tx)
        .on('transactionHash', txhash => {
          console.log('sent tx hash: ', txhash);
          that.setState({
            paymentAddress: null,
            paymentModalIsOpen: false,
            paymentAmountInEth: 0
          });
          setTimeout(() => {
            that.refreshInvoices();
          }, 10000);
        });
    });
  }

  handleAmountChange(ev) {
    this.setState({ paymentAmountInEth: ev.target.value });
  }

  render() {
    let invoiceItems;
    if (this.props.invoices && this.props.invoices.length >0) {
      invoiceItems = this.props.invoices.map(invoice => {
        const paidInEther = fromWeiToString(invoice.paid)
        const totalInEther = fromWeiToString(invoice.total)
        const paymentLeft = fromWeiToString(toBN(invoice.total).sub(toBN(invoice.paid)))

        return (
          <tr key={invoice.invoice_id}>
            <td>{invoice.invoice_id}</td>
            <td>{getStateIndicator(invoice.state_id)}</td>
            <td>&Xi;{totalInEther}</td>
            <td>&Xi;{paidInEther}</td>
            <td>{invoice.address}</td>
            <td>
              <button onClick={ev => {
                ev.preventDefault();
                this.openPayment(invoice.address, paymentLeft);
              }}>Make Payment</button>
            </td>
          </tr>
        );
      });
    } else {
      invoiceItems = (
        <tr><td className="notice">No invoices found</td></tr>
      );
    }
    return (
      <div id="invoices">

        <Modal
            isOpen={this.state.paymentModalIsOpen}
            onRequestClose={this.closePaymentModal}
            contentLabel="Make a Payment"
          >
          <h4>Make a Payment</h4>
          <p>
            Normally, a user would use their wallet of choice to do this, but
            for the purposes of this demo, we're going to trigger payments from
            an auto-generated account.
          </p>
          <form>
            <label htmlFor="amount">Amount</label>
            <div className="form-append">
              <input type="number" name="total" value={this.state.paymentAmountInEth} onChange={this.handleAmountChange} />
              <span className="append">&Xi;</span>
            </div>
            <button type="submit" className="button"
              onClick={ev => { ev.preventDefault(); this.makePayment(); }}
              >Pay</button>
            <button type="submit" className="button button-outline"
              onClick={ev => { ev.preventDefault(); this.setState({ paymentModalIsOpen: false}); }}
              >Close</button>
          </form>
        </Modal>

        <h3>All Invoices</h3>
        <table className="invoice-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>State</th>
              <th>Total</th>
              <th>Paid</th>
              <th>Payment Address</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {invoiceItems}
          </tbody>
        </table>
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    invoices: state.invoices
  }
}

function mapDispatchToProps(dispatch) {
  return {
    initialInvoices: (invoices) => dispatch(initialInvoices(invoices))
  };
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Invoices);
