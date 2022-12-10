"""
Now that we know when the tokenpair was created, we can try to look up when liquidity was deposited in the pool
and which swaps were done after the liquidity was added

TODO: do the same analysis but only when the liquidity provided is worth more than a certain ONE or Dollar amount because
    for example EIGHT finance started with super low liquidity
"""
from web3 import Web3
from tools import robust_function_call, save_json, load_json
from fire import Fire
from web3.middleware import geth_poa_middleware
import time

def run(config):


    config = load_json(config)
    poolstart_times = load_json(f"data/{config['name']}/poolstart_times.json")
    abi_pair = load_json("abis/pair.json")

    all_swap_transactions = dict()

    n_tokenpairs = 0
    print("*********** GETTING SWAPS ***********")
    for pair in poolstart_times["any"].keys():

        print(f"tokenpair #{n_tokenpairs}, address: {pair}")
        n_tokenpairs += 1

        if poolstart_times["any"][pair] is None:
            all_swap_transactions[pair] = None
            continue

        while True:
            try:


                w3 = Web3(Web3.HTTPProvider(config["RPC"]))
                w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                address_pair = w3.toChecksumAddress(pair)
                contract_pair = w3.eth.contract(address=address_pair, abi=abi_pair)

                event_filter = contract_pair.events.Swap.createFilter(
                    fromBlock=poolstart_times["any"][pair]["blockNumber"],
                    toBlock=poolstart_times["any"][pair]["blockNumber"] + config["blockrange_swaps"] - 1)
                swap_event_txs = event_filter.get_all_entries()
                swap_hashes = [swap_event_tx["transactionHash"].hex() for swap_event_tx in swap_event_txs]

                all_swap_transactions[pair] = swap_hashes
                break

            except Exception as exc:
                print(exc)
                time.sleep(10)


    save_json(all_swap_transactions, f"data/{config['name']}/all_swap_transactions.json")


if __name__ == "__main__":
    Fire(run)