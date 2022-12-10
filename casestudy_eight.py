from web3 import Web3
from tools import load_json
import pyhmy
from pyhmy.util import convert_one_to_hex
import networkx as nx
#from pyvis.network import Network
import matplotlib.pyplot as plt

config_name = "harmony_test"
config = f"configs/config_{config_name}.json"

config = load_json(config)
RPC = config["RPC"]
w3 = Web3(Web3.HTTPProvider(RPC))

CA = "0x6fB25f3D3ed5A048cB50E50B0eADcEb49087ad7B" # "0xfc2E3B2e7f81B4f01e05C465509a5e256354C434" # just regular swap: "0x4b8E29C1162Bc583A00ADBAF741891bB04Aedf37" another regular swap 0x564DAFa3424aCfe49419a0EFe96D2758fB6A1dF4 #"0x6fB25f3D3ed5A048cB50E50B0eADcEb49087ad7B" # 0xe5B21f200a8a39E6b677080995Cd5a0e494FF3d2

def query_in_txes(address, page_size=100, max_pages=10):
    relevant_txes = list()
    n = pyhmy.account.get_transactions_count(address, tx_type='RECEIVED', endpoint="https://api.harmony.one/")
    print(f"{n} incoming")
    n_pages = n // page_size +1
    for page in range(min(max_pages,n_pages)):
        print(page)
        txes_ = pyhmy.account.get_transaction_history(address, page=page, page_size=page_size, tx_type="RECEIVED", include_full_tx=True, endpoint="https://api.harmony.one/")
        txes  = [tx for tx in txes_ if len(tx["to"]) >0]
        tos  = [convert_one_to_hex(tx["to"]) for tx in txes]
        relevant_txes_block = [txes[i] for i in range(len(txes)) if tos[i] == address]
        relevant_txes += relevant_txes_block

    return relevant_txes

def n_hop_in_txes(address, n_hops, pages_size=100, max_pages=10):

    assert n_hops>=1
    in_addresses = [address]
    graphinfo = set()
    queried = set()
    for j in range(n_hops):



        addresses_to_query = list(set(in_addresses) - queried)
        len_to_query = len(addresses_to_query)

        for i in range(len_to_query):
            print(f"{j + 1}-th out of {n_hops} hops, {i + 1}-th input out of {len_to_query}")
            address_to_query = addresses_to_query[i]
            # query
            relevant_txes = query_in_txes(address_to_query, pages_size, max_pages)

            # build data for graph
            graphinfo_i = set([(convert_one_to_hex(t["from"]), convert_one_to_hex(t["to"])) for t in relevant_txes])
            graphinfo =  list(set(graphinfo) | graphinfo_i)

            # build set to query next
            in_addresses = [graphinfo[k][0] for k in range(len(graphinfo))]
            queried |= set(address_to_query)


    G = nx.DiGraph()
    G.add_edges_from(graphinfo)
    return G

# CA is the target of trans
G = n_hop_in_txes(CA, 2, 1, 10)
nx.write_edgelist(G, "data/nx.csv", delimiter=",", data=False)

fig = plt.figure(3, figsize=(20, 20), dpi=200)
nx.draw_circular(G)
plt.show()
