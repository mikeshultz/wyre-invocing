import React, { Component } from 'react';
import { connect } from 'react-redux'
import './AddInvoice.css';
import { addInvoice } from '../store/actions'
import WyreAPI from '../api'

class AddInvoice extends Component {
  constructor(props) {
    super(props);

    this.state = {
      totalEther: 0,
      notice: ''
    }

    this.handleTotalChange = this.handleTotalChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
  }
  componentDidMount() {
    
  }

  handleSubmit(ev) {
    ev.preventDefault();
    if (this.state.totalEther < 0.001) {
      console.error('Total invoice amount too low');
      return;
    }
    this.setState({ notice: ''})
    const that = this;
    const totalInWei = this.state.totalEther * 1e18;
    WyreAPI.addInvoice(totalInWei).then(invoiceId => {
      if (!invoiceId) {
        console.error('failed adding invoice', invoiceId)
        that.setState({ notice: 'Backend error adding invoice.'})
        return
      }
      WyreAPI.getInvoice(invoiceId).then(invoice => {
        that.props.addInvoice(invoice);
        that.setState({
          notice: 'Successfully added invoice!',
          totalEther: 0
        })
      });
    }).catch(err => {
      console.error(err);
      that.setState({ notice: 'Error ocurred when submitting new invoice' });
    });
  }

  handleTotalChange(ev) {
    this.setState({ totalEther: ev.target.value });
  }

  render() {
    return (
      <div id="add-invoice">
        <h3>Add an Invoice</h3>
        <form id="add-invoice-form" onSubmit={this.handleSubmit}>
          <label htmlFor="total">Total</label>
          <div className="form-append">
            <input type="number" name="total" value={this.state.totalEther} onChange={this.handleTotalChange} />
            <span className="append">&Xi;</span>
          </div>
          <button type="submit">Add</button>
          <div className="notice">{this.state.notice}</div>
        </form>
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {};
}

function mapDispatchToProps(dispatch) {
  return {
    addInvoice: (invoice) => dispatch(addInvoice(invoice))
  };
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(AddInvoice);
