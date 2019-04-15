import BN from 'bn.js';
//import Web3 from 'web3';
import * as W3Utils from 'web3-utils';

export function toBN(num) {
  return new BN(num);
}

export function fromWei(wei) {
  return W3Utils.fromWei(wei, 'ether');
}

export function fromWeiToString(wei) {
  wei = fromWei(wei);
  return wei.toString();
}


export function toWei(ether) {
  return W3Utils.toWei(ether, 'ether');
}

export function toWeiToString(ether) {
  const wei = toWei(ether);
  return wei.toString();
}
