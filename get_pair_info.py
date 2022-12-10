"""
This script creates a json file so one can look up the tokens involved in a pair

this script takes ~2200 seconds on harmony
"""
from web3 import Web3
import time
from tools import robust_function_call, load_json, save_json
from fire import Fire

def run(config):

    config = load_json(config)
    w3 = Web3(Web3.HTTPProvider(config["RPC"]))

    abi_pair = load_json("abis/pair.json")
    pairs = load_json(f"data/{config['name']}/pairs.json")

    pair_to_info = dict()
    n_pairs = 0

    now = time.time()

    for name in pairs.keys():
        print(f"exchange {name}")
        for pair in pairs[name].keys():
            print(f"pair #{n_pairs}, address {pair}")
            n_pairs +=1
            contract_pair = w3.eth.contract(address=pair, abi=abi_pair)

            info = dict()
            info["token0"] = robust_function_call(contract_pair.functions.token0().call)
            info["token1"] = robust_function_call(contract_pair.functions.token1().call)
            pair_to_info[pair] = info

    later = time.time()


    print("took", later-now)
    save_json(pair_to_info, f"data/{config['name']}/pair_to_info.json")

if __name__ == "__main__":
    Fire(run)