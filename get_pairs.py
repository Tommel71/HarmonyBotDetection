"""
This script extracts the pairs only and contains a subsampling step if there are too many pairs to handle
"""
from tools import load_json, save_json
from fire import Fire
import numpy as np
from web3.auto import Web3 as w3

def run(config, only_selected=None):

    config = load_json(config)
    pair_created_transactions = load_json(f"data/{config['name']}/pair_created_transactions.json")

    pairs_dict = dict()

    for exchange_name in pair_created_transactions.keys():

        print(f"Working on {exchange_name}...")
        pairs = [tx["tokenpair"] for tx in pair_created_transactions[exchange_name]]
        tx_hashes = [tx["tx_hash"] for tx in pair_created_transactions[exchange_name]]

        # In case we only want to analyse certain pairs
        if only_selected is not None:
            pairs_dict[exchange_name] = {w3.toChecksumAddress(pairs[i]): tx_hashes[i] for i in range(len(pairs)) if pairs[i] in only_selected}
            continue

        n_pairs = int(len(pairs)*config["percentage_pairs"])
        idx = np.round(np.linspace(0, len(pairs) - 1, n_pairs)).astype(int)
        print(idx)
        pairs_dict[exchange_name] = {w3.toChecksumAddress(pairs[i]):tx_hashes[i] for i in idx}

    save_json(pairs_dict, f"data/{config['name']}/pairs.json")

if __name__ == "__main__":
    Fire(run)