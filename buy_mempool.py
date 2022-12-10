import buy_as_fast_as_possible
from web3 import Web3
import datetime
from tools import load_json
import logging
from fire import Fire
logging.basicConfig(filename=f'mempool_buy.log', level=logging.INFO)


def liquidity_added(tx_hash, w3, signature, token_address):
    input = w3.eth.getTransaction(tx_hash)["input"]
    if input[:10] == signature:
        logging.info("got liqu added")
        if token_address.lower() in input:
            logging.info("correct token too")
            return True
        else:
            logging.info("not correct token")

    return False



def run(config,token_address, nonce=None):

    logging.info(f"starting mempool buy for {config}")
    signature = "0xf305d719"
    config_dict = load_json(config)

    w3 = Web3(Web3.HTTPProvider(config_dict["RPC"]))
    new_transaction_filter = w3.eth.filter('pending')


    while True:

        time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        logging.info(f"time: {time}")
        transactions = new_transaction_filter.get_new_entries()

        logging.info(transactions)
        if any(list(map(lambda x: liquidity_added(x, w3, signature, token_address), transactions))):
            print("cleared")
            tx_hash_buy = buy_as_fast_as_possible.run(config, token_address, nonce)
            logging.info(f"buy")
            return tx_hash_buy

if __name__ == "__main__":
    Fire(run)