import deploy_token, add_liquidity, buy_as_fast_as_possible
from web3 import Web3
from tools import load_json

chain = "harmony"

credentials = load_json("credentials/test_wallet.json")
address = credentials["address"]

config = f"configs/config_{chain}.json"
config_dict = load_json(config)
w3 = Web3(Web3.HTTPProvider(config_dict["RPC"]))

token_address = deploy_token.run(config)

nonce = w3.eth.get_transaction_count(address)

tx_hash_add_liq = add_liquidity.run(config, token_address, nonce)

tx_hash_buy = buy_as_fast_as_possible.run(config, token_address, nonce+2)

tx_receipt_add_liq = w3.eth.wait_for_transaction_receipt(tx_hash_add_liq)
tx_receipt_buy = w3.eth.wait_for_transaction_receipt(tx_hash_buy)

new_pair = "0x" +tx_receipt_add_liq["logs"][0]["data"][26:(26+40)]
