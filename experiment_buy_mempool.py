import deploy_token, add_liquidity
from web3 import Web3
from tools import load_json
import subprocess as sp
import time

chain = "harmony"

credentials = load_json("credentials/test_wallet.json")
address = credentials["address"]

config = f"configs/config_{chain}.json"
config_dict = load_json(config)
w3 = Web3(Web3.HTTPProvider(config_dict["RPC"]))

token_address = deploy_token.run(config)

nonce = w3.eth.get_transaction_count(address)

cmd = f"python buy_mempool.py {config} {token_address[2:]} {nonce+2}"
process = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

tx_hash_add_liq = add_liquidity.run(config, token_address, nonce)
tx_receipt_add_liq = w3.eth.wait_for_transaction_receipt(tx_hash_add_liq)
time.sleep(10)
process.kill()