"""
Given a blockchain, returns the most busy uniswap routers in the last x blocks (1000 as of now but might be subject to change)
"""

from web3 import Web3
from tools import load_json
from fire import Fire
from web3.middleware import geth_poa_middleware
from collections import Counter
import numpy as np
import pandas as pd

def is_router(address, w3, abi_router):
    try:
        contract_router = w3.eth.contract(address=address, abi=abi_router)
        contract_router.functions.WETH().call()
        contract_router.functions.factory().call()
        return True
    except:
        return False

def run(config, n_routers=1):

    print(f"started getting DEXes")
    swap_signature = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
    config_dict = load_json(config)
    abi_router = load_json("abis/router.json")
    abi_factory = load_json("abis/factory.json")
    abi_pair = load_json("abis/pair.json")

    w3 = Web3(Web3.HTTPProvider(config_dict["RPC"]))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    latestBlock = w3.eth.get_block('latest')["number"]
    new_transaction_filter = w3.eth.filter({"fromBlock":latestBlock -1000, "toBlock":latestBlock,
                                            "topics": [swap_signature, None, None]})



    # collect transactions
    relevant = new_transaction_filter.get_all_entries()


    # find most common ones
    addresses = [[topic.hex() for topic in tx["topics"][1:]] for tx in relevant]
    flat = [Web3.toChecksumAddress("0x"+x[-40:]) for x in np.concatenate(addresses)]
    counter = Counter(flat)
    potential_routers = [x[0] for x in counter.most_common()]

    # filter for routers only, not just swapping addresses
    routers = [pr for pr in potential_routers if is_router(pr, w3, abi_router)]

    def get_name(router_address):
        contract_router = w3.eth.contract(address=router_address, abi=abi_router)
        factory_address = contract_router.functions.factory().call()
        contract_factory = w3.eth.contract(address=factory_address, abi=abi_factory)
        pair_address = contract_factory.functions.allPairs(0).call()
        contract_pair = w3.eth.contract(address=pair_address, abi=abi_pair)
        name = contract_pair.functions.name().call()
        return name[:name.find(" ")]

    router_names = [get_name(router) for router in routers]
    df = pd.DataFrame({"address": routers, "name": router_names, "swaps": [counter[add] for add in routers]})
    df = df.sort_values("swaps", ascending=False)
    result = {df.name[i]:df.address[i] for i in range(min(len(df), n_routers))}
    return result

if __name__ == "__main__":
    Fire(run)