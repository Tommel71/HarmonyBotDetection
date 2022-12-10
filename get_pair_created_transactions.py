"""
For all pairs, get the transaction that created it
"""

from web3 import Web3
import time
from tools import robust_function_call, load_json, save_json
import numpy as np
from fire import Fire
from web3.middleware import geth_poa_middleware


def run(config):

    config = load_json(config)
    w3 = Web3(Web3.HTTPProvider(config["RPC"]))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    interval = config["interval"]
    blockrange_swaps = config["blockrange_swaps"]

    # get the n most recent pairs on the chain if specified
    if not ("n_latest_pairs" in config):
        n_latest = np.infty
    elif config["n_latest_pairs"] is None:
        n_latest = np.infty
    else:
        n_latest = config["n_latest_pairs"]

    # get the most recent block if no until_block is specified
    if not ("until_block" in config):
        until_block = w3.eth.get_block('latest')["number"]
    elif config["until_block"] == None:
        until_block = w3.eth.get_block('latest')["number"]
    else:
        until_block = config["until_block"]

    exchanges = config["exchanges"]
    abi_router = load_json("abis/router.json")

    exchange_to_transactions = dict()
    for name in exchanges.keys():
        print(f"exchange:{name}")

        # get relevant contracts, and addresses for filtering the blockchain
        address_router = Web3.toChecksumAddress(exchanges[name])
        contract_router = w3.eth.contract(address=address_router, abi=abi_router)
        address_factory = contract_router.functions.factory().call()

        transactions_serialisable = []
        i = 0
        finished = False
        while not finished:

            now = time.time()

            # define interval borders
            left =  until_block - (i+1)*interval +1 - blockrange_swaps
            right = until_block - i*interval        - blockrange_swaps

            # when we arrive at block 0 we are done
            if left <= 0:
                finished = True
                left =0

            # create function and call it with robust_function_call to retry on errors
            def get_entries():
                w3 = Web3(Web3.HTTPProvider(config["RPC"]))
                event_filter = w3.eth.filter(filter_params={"fromBlock": left, "toBlock": right, "address": address_factory})
                return event_filter.get_all_entries()

            transactions = robust_function_call(get_entries)[::-1]

            later = time.time()
            print(i*interval, " entries take ", later-now, " and yields #", len(transactions), " relevant transactions")
            print(i*interval/until_block)
            # increase i for the next step
            i+=1

            # get the data we are interested in
            for tx in transactions:
                attributes = dict()
                attributes["tokenpair"] = "0x" + tx["data"][26:66]
                attributes["tx_hash"] = tx["transactionHash"].hex()
                attributes["blockHash"] = tx["blockHash"].hex()
                attributes["blockNumber"] = tx["blockNumber"]

                transactions_serialisable.append(attributes)

            print(len(transactions_serialisable))
            # go to the next exchange as soon as we have enough pairs
            if len(transactions_serialisable) >= n_latest:
                finished=True


        # add all the data for the exchange in the dictionary
        exchange_to_transactions[name] = transactions_serialisable[::-1]

    # save dictionary
    save_json(exchange_to_transactions, f"data/{config['name']}/pair_created_transactions.json")

if __name__ == "__main__":
    Fire(run)
