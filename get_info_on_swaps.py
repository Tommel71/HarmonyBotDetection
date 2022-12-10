"""
For each swap we get when it was mined, the value etc.
"""

from web3 import Web3
from fire import Fire
from tools import load_json, save_json
from web3.middleware import geth_poa_middleware
import time

def run(config):

    config = load_json(config)

    all_swap_transactions = load_json(f"data/{config['name']}/all_swap_transactions.json")

    n_swaps = 0
    swap_to_info = dict()
    for pair in all_swap_transactions.keys():
        if all_swap_transactions[pair] is None:
            continue

        while True:
            try:
                w3 = Web3(Web3.HTTPProvider(config["RPC"]))
                w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                for swap_hash in all_swap_transactions[pair]:
                    print(f"swap #{n_swaps}, address {swap_hash}")

                    n_swaps+=1
                    tx = w3.eth.getTransaction(swap_hash)
                    info = dict()
                    info["timestamp"] =  int(w3.eth.getBlock(tx["blockNumber"])["timestamp"]) # TODO check if still works for Harmony
                    info["blockNumber"] = tx["blockNumber"]
                    info["gasPrice"] = tx["gasPrice"]
                    info["value"] = tx["value"]
                    input = tx["input"]
                    info["functionSignatureHash"] = input[2:10]
                    info["functionParameters"] = [input[10+24+i*64:10+24+40+i*64] for i in range(int((len(input)-10)/64))]
                    swap_to_info[swap_hash] = info

                break

            except Exception as exc:
                print(exc)
                time.sleep(10)

    save_json(swap_to_info, f"data/{config['name']}/swap_to_info.json")

if __name__ == "__main__":
    Fire(run)
