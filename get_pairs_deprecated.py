"""
This script fetches all the pairs from the exchanges specified in exchanges.json
"""
from web3 import Web3
from tools import robust_function_call, load_json, save_json
from fire import Fire

def run(config):

    config = load_json(config)
    w3 = Web3(Web3.HTTPProvider(config["RPC"]))

    exchanges = config["exchanges"]
    abi_router = load_json("abis/router.json")
    abi_factory = load_json("abis/factory.json")

    pairs_dict = dict()

    for exchange_name in exchanges.keys():

        print(f"Working on {exchange_name}...")

        address_router = Web3.toChecksumAddress(exchanges[exchange_name])
        contract_router = w3.eth.contract(address=address_router, abi=abi_router)
        address_factory = robust_function_call(contract_router.functions.factory().call)

        contract_factory = w3.eth.contract(address=address_factory, abi=abi_factory)
        got_pairs = True
        i = 0
        pairs = []
        while got_pairs:
            try:
                print(i)
                pair = contract_factory.functions.allPairs(i).call()
                pairs.append(pair)
                i+=1

            except Exception as exc:
                print(exc)
                got_pairs=False

        pairs_dict[exchange_name] = pairs

    save_json(pairs_dict, f"data/{config['name']}/pairs.json")

if __name__ == "__main__":
    Fire(run)