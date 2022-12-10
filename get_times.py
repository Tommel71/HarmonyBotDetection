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
    abi_pair = load_json("abis/pair.json")
    pair_created_txs = load_json(f"data/{config['name']}/pair_created_transactions.json")
    pairs = load_json(f"data/{config['name']}/pairs.json")

    tx_hash_to_blocknumber = dict()
    for exchange in pair_created_txs.keys():
        mapping = {tx["tx_hash"]:tx["blockNumber"] for tx in pair_created_txs[exchange]}
        tx_hash_to_blocknumber[exchange] = mapping


    """
    def is_significant():
        pass

    significant_threshold = {
        "0xcf664087a5bb0237a0bad6742852ec6c8d69a27a": 5000, # WONE
        "0xef977d2f931c1978db5f6747666fa1eacb0d0339": 1000, # 1DAI
        "0x9c2a806948758a3b0959488de36830e1e2139007": 1000, # 1USDC
        "0x3c2b8be99c50593081eaa2a724f0b8285f5aba8f": 1000, # 1USDT
        "0xe176ebe47d621b984a73036b9da5d834411ef734": 1000, # BUSD
    }
    """

    poolstart_times = dict()
    poolstart_times["any"] = dict() # if any liquidity was first added
    poolstart_times["significant"] = dict() #  if significant liquidity was first added TODO implement in loop
    n_tokenpairs = 0
    for exchange in pairs.keys():
        print(f"Exchange: {exchange}")

        for pair in pairs[exchange].keys():
            while True:
                try:
                    tx_hash = pairs[exchange][pair]
                    print(f"tokenpair #{n_tokenpairs}, address: {pair}")
                    n_tokenpairs+=1
                    w3 = Web3(Web3.HTTPProvider(config["RPC"]))
                    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                    address_pair = w3.toChecksumAddress(pair)
                    contract_pair = w3.eth.contract(address=address_pair, abi=abi_pair)

                    # iteratively search
                    max_iter = config["lookahead_liq_reps"]
                    interval = config["lookahead_liq_block_interval"]
                    blockNumber = tx_hash_to_blocknumber[exchange][tx_hash]
                    transfer_event_txs = []
                    liq_found = False

                    for i in range(max_iter):
                        print(f"looking ahead {(i+1)*interval} blocks, or {(i+1)*interval*2/60} minutes")
                        event_filter = contract_pair.events.Transfer.createFilter(fromBlock=blockNumber + i*interval,
                                                                                  toBlock=blockNumber+ (i+1)*interval -1)
                        transfer_event_txs = event_filter.get_all_entries()
                        print(transfer_event_txs)

                        for transfer_event_tx in transfer_event_txs: # TODO make sure theyre in order

                            tx_to_inspect = w3.eth.getTransaction(transfer_event_tx["transactionHash"].hex())
                            if tx_to_inspect["input"][:10] in ["0xf305d719", "0xe8e33700"]: # , "0x22363eec"] : this is never used
                                print("add liquidity found")
                                liq_found = True
                                times = dict()
                                times['value'] = tx_to_inspect['value']  #we get value in wei https://web3js.readthedocs.io/en/v1.2.11/web3-eth.html#gettransaction
                                times["blockNumber"] = tx_to_inspect["blockNumber"]
                                times["timestamp"] = int(w3.eth.getBlock(tx_to_inspect["blockNumber"])["timestamp"]) # TODO see if this works for Harmony or we need to convert to int from hex
                                poolstart_times["any"][pair] = times
                                break

                        if liq_found:
                            break

                    break

                except Exception as exc:
                    print(exc)
                    time.sleep(10)


            if not liq_found:
                print("Couldnt find add liquidity transaction")
                times = None
                poolstart_times["any"][pair] = times
                print(transfer_event_txs)

    save_json(poolstart_times, f"data/{config['name']}/poolstart_times.json")


if __name__ == "__main__":
    Fire(run)