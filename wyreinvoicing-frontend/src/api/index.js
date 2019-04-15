import axios from 'axios';

const BASE_URL = 'http://localhost:8000' // there's no production environment

export default class WyreAPI {

  static async _get(endpoint) {
    const response = await axios.get(`${BASE_URL}/${endpoint}`);
    if (response.status !== 200) {
      throw new Error(`Unexpected reponse: ${response.status}`)
    }
    return response.data;
  }

  static async _post(endpoint, body) {
    const response = await axios.post(`${BASE_URL}/${endpoint}`, body, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    if (response.status !== 200) {
      throw new Error(`Unexpected reponse: ${response.status}`);
    }
    return response.data;
  }

  /**
   * API Data Requests
   */

  static async getInvoices() {
    const response = await WyreAPI._get('invoice');
    if (!response.success) {
      throw new Error('Error fetching invoices')
    }
    return response.result;
  }

  static async getInvoice(invoiceId) {
    const response = await WyreAPI._get(`invoice/${invoiceId}`);
    if (!response.success) {
      throw new Error('Error fetching invoice')
    }
    return response.result;
  }

  static async addInvoice(totalWei) {
    console.log('submitting invoice for total: ', totalWei)
    const response = await WyreAPI._post('invoice', {
      total: totalWei
    });
    return response.result;
  }
}
