from web3 import Web3
from tools import load_json
import calendar
import time


credentials = load_json("credentials/test_wallet.json")
pk = credentials["pk"]
address = credentials["address"]

def run(config, token_address, nonce=None):
      config = load_json(config)
      w3 = Web3(Web3.HTTPProvider(config["RPC"]))
      token_amt = 100*10**18
      ONE_amt = int(0.001*10**18)
      exchanges = config["exchanges"]

      dex = "defikingdoms"

      ### APPROVE
      data = f"0x095ea7b3000000000000000000000000{exchanges[dex][2:]}ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

      if nonce is None:
            nonce = w3.eth.get_transaction_count(address)


      tx = {'nonce': nonce,
            'chainId': config["chainId"],
            'gasPrice': w3.toWei(config["gasPrice"], "gwei"),
            'gas': config["gas"],
            'from':address,
            'data':data,
            'to':w3.toChecksumAddress(token_address)}

      signed_tx = w3.eth.account.sign_transaction(tx, pk)

      tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

      # Wait for the transaction to be mined, and get the transaction receipt
      tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)


      ### ADD LIQUIDITY
      address_router = exchanges[dex]
      abi_router = load_json("abis/router.json")

      nonce +=1


      contract_router = w3.eth.contract(address=w3.toChecksumAddress(address_router), abi=abi_router)


      # gmt stores current gmtime
      gmt = time.gmtime()
      # ts stores timestamp
      ts = calendar.timegm(gmt)

      deadline = ts+1000

      tx_hash = contract_router.functions.addLiquidityETH(w3.toChecksumAddress(token_address), token_amt, token_amt, ONE_amt, w3.toChecksumAddress(address), deadline).buildTransaction({'nonce': nonce, 'gasPrice': w3.toWei(config["gasPrice"]+20, "gwei"), 'from':w3.toChecksumAddress(address), "value": ONE_amt})

      signed_tx = w3.eth.account.sign_transaction(tx_hash, pk)

      tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
      return tx_hash
