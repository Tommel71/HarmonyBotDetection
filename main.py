import get_pair_created_transactions, get_swaps, get_pair_info, get_info_on_swaps, get_times, get_pairs, get_uniswap_routers
import logging
from time import time
from tools import load_json, save_json
import os

config_name = "harmony_value2"
config = f"configs/config_{config_name}.json"
logging.basicConfig(filename=f'main_{config_name}.log', level=logging.INFO)
logging.info(f"starting main for {config}")
config_dict = load_json(config)

# create folder if it doesnt already exist
foldername = f"data/{config_dict['name']}"
if not os.path.exists(foldername):
    os.makedirs(foldername)


# query most activate exchanges if not provided already
if "exchanges" not in config_dict:
    routers = get_uniswap_routers.run(config, n_routers=1)
    config_dict["exchanges"] = routers
    save_json(config_dict, config)

start = time()
get_pair_created_transactions.run(config)
logging.info(f"took {time()- start}")

start = time()
get_pairs.run(config)
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