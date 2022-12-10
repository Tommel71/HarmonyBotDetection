import get_pair_created_transactions, get_swaps, get_pair_info, get_info_on_swaps, get_times, get_pairs
import logging
from time import time

chain = "harmony_testnet"
config = f"configs/config_{chain}.json"
logging.basicConfig(filename=f'main_{chain}.log', level=logging.INFO)
logging.info(f"starting main for {config}")

start = time()
get_pair_created_transactions.run(config, test=True)
logging.info(f"took {time()- start}")

start = time()
get_pairs.run(config)#, only_selected={"0xbf5b2b30ef89b3bf6e931601a3c498aa11f7eee1"})
logging.info(f"took {time()- start}")

start = time()
get_pair_info.run(config)
logging.info(f"took {time()- start}")

start = time()
get_times.run(config)
logging.info(f"took {time()- start}")

start = time()
get_swaps.run(config)
logging.info(f"took {time()- start}")

start = time()
get_info_on_swaps.run(config)
logging.info(f"took {time()- start}")