from web3 import Web3
import time
from tools import load_json
import calendar


credentials = load_json("credentials/test_wallet.json")
pk = credentials["pk"]
address = credentials["address"]

def run(config, token_address, nonce = None):
    config = load_json(config)
    dex = "defikingdoms"

    w3 = Web3(Web3.HTTPProvider(config["RPC"]))

    abi_router = load_json("abis/router.json")
    exchanges = config["exchanges"]
    address_router = exchanges[dex]
    ONE_amt = int(0.001*10**18)


    WONE_address = config["WONE_address"]

    # gmt stores current gmtime
    gmt = time.gmtime()
    # ts stores timestamp
    ts = calendar.timegm(gmt)
    deadline = ts+1000
    if nonce is None:
        nonce = w3.eth.get_transaction_count(address)

    contract_router = w3.eth.contract(address=w3.toChecksumAddress(address_router), abi=abi_router)
    unbuilt = contract_router.functions.swapExactETHForTokens(1, # insane slippage
                                                    [w3.toChecksumAddress(WONE_address), w3.toChecksumAddress(token_address)],
                                                    w3.toChecksumAddress(address),
                                                    deadline)

    tx_hash = unbuilt.buildTransaction({'nonce': nonce, 'gasPrice': w3.toWei(config["gasPrice"], "gwei"), 'from':w3.toChecksumAddress(address), "value": ONE_amt})
    signed_tx = w3.eth.account.sign_transaction(tx_hash, pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash