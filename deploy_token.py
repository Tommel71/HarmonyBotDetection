from web3 import Web3
from solcx import compile_source
from tools import load_json

credentials = load_json("credentials/test_wallet.json")
pk = credentials["pk"]
address = credentials["address"]

def run(config):

    config = load_json(config)

    # Solidity source code
    name = "testitup2"
    symbol = "TST2"

    test2 = """
    pragma solidity ^0.8.0;
    
    import "./contracts/ERC20.sol";
    
    contract MyToken is ERC20 {
        address public admin;
        constructor() ERC20("""  + f"'{name}', '{symbol}'" +  """){
            _mint(msg.sender, 10000*10**18);
            admin = msg.sender;
        }
    }
    """

    compiled_sol = compile_source(test2, output_values=['abi', 'bin'])

    # retrieve the contract interface
    contract_interface = compiled_sol["<stdin>:MyToken"]

    # get bytecode / bin
    bytecode = compiled_sol["<stdin>:MyToken"]['bin']

    # get abi
    abi = compiled_sol["contracts/ERC20.sol:ERC20"]['abi']

    # web3.py instance
    w3 = Web3(Web3.HTTPProvider(config["RPC"]))


    Token = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(address)

    tx_hash = Token.constructor("das", "sad").buildTransaction({'nonce': nonce, 'gasPrice': w3.toWei(config["gasPrice"], "gwei"), 'from':address})

    signed_tx = w3.eth.account.sign_transaction(tx_hash, pk)

    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Wait for the transaction to be mined, and get the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.contractAddress