import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tools import load_json

confignames = ["harmony", "binance", "binance_latest_n", "ethereum"]

def get_swap_times(pair):
    poolstart_times = load_json(f"data/harmony/poolstart_times.json")
    all_swap_transactions = load_json(f"data/harmony/all_swap_transactions.json")
    swap_to_info = load_json(f"data/harmony/swap_to_info.json")

    poolstart_times = poolstart_times["any"]

    pairs = list()
    first_buy_difference = list()

    pairs_all_times = list()
    swap_all_times = list()
    all_time_diffs = list()
    poolstarts = list()

    if poolstart_times[pair] is None:
        return
    poolstart = poolstart_times[pair]["timestamp"]
    swap_hashes = all_swap_transactions[pair]
    if swap_hashes is None:
        return

    times = list()
    for swap_hash in swap_hashes:
        pairs_all_times.append(pair)
        swap_all_times.append(swap_hash)
        all_time_diffs.append(swap_to_info[swap_hash]["timestamp"] - poolstart)
        times.append(swap_to_info[swap_hash]["timestamp"])

    return all_time_diffs


def calculate_times(configname):
    config = f"configs/config_{configname}.json"
    config = load_json(config)
    poolstart_times = load_json(f"data/{config['name']}/poolstart_times.json")
    all_swap_transactions = load_json(f"data/{config['name']}/all_swap_transactions.json")
    swap_to_info = load_json(f"data/{config['name']}/swap_to_info.json")

    poolstart_times = poolstart_times["any"]

    pairs = list()
    first_buy_difference = list()

    pairs_all_times = list()
    swap_all_times = list()
    all_time_diffs = list()
    poolstarts = list()

    for pair in poolstart_times.keys():
        if poolstart_times[pair] is None:
            continue
        poolstart = poolstart_times[pair]["timestamp"]
        swap_hashes = all_swap_transactions[pair]
        if swap_hashes is None:
            continue

        times = list()
        for swap_hash in swap_hashes:
            pairs_all_times.append(pair)
            swap_all_times.append(swap_hash)
            all_time_diffs.append(swap_to_info[swap_hash]["timestamp"] - poolstart)
            times.append(swap_to_info[swap_hash]["timestamp"])

        if len(times) == 0:
            continue
        first_swap_time = min(times)
        pairs.append(pair)
        poolstarts.append(poolstart)
        first_buy_difference.append(first_swap_time - poolstart)

    df = pd.DataFrame({"pair": pairs, "first_buy_speed": first_buy_difference, "poolstart": poolstarts})
    return df


"""
    df = df[df["first_buy_speed"] < config["blockrange_swaps"] * 2]  # TODO blocktime is 2 only for harmony

    df.hist(bins=100)
    plt.show()

    df_first_minute = df[df["first_buy_speed"] < 60]
    df_first_minute[["first_buy_speed"]].hist(bins=60)
    plt.show()

    df_all = pd.DataFrame({"pair": pairs_all_times, "buy_speed": all_time_diffs, "swap": swap_all_times})
    df_all = df_all[df_all["buy_speed"] < config["blockrange_swaps"] * 2]  # TODO blocktime is 2 only for harmony
    df_all.hist(bins=100)
    plt.show()

    df_all_first_minute = df_all[df_all["buy_speed"] < 60]
    df_all_first_minute.hist(bins=20)
    plt.show()

"""
def get_snipe_percentage(df):
    return sum(df["first_buy_speed"] < 5) / len(df)


dfs = list(map(calculate_times, confignames))
snipe_percentages = list(map(get_snipe_percentage, dfs))
i=0

sns.set_style('darkgrid')

for df in dfs:
    df_first_minute = df[df["first_buy_speed"] < 100]
    sns.histplot(df_first_minute['first_buy_speed'], kde=True, bins=50)\
        .set(title=('Distribution of first buy speed on ' + confignames[i]), xlabel='First buy speed')
    plt.show()
    i = i+1

most_traded = ['0x1e35802a66f5346b350ab10169cc7868dcd0c32d', #HRC20 Star and HRC20 Wrapped ONE
               '0x7e506951f196bc4504ab4557bb856d1043497c0b', #HRC20 JOC and HRC20 Wrapped ONE
               '0xcde0a00302cf22b3ac367201fbd114cefa1729b4'] #HRC20 Wrapped ONE and HRC20 Reverse Token

titles = ['HRC20 Star and HRC20 Wrapped ONE',
          'HRC20 JOC and HRC20 Wrapped ONE',
          'HRC20 Wrapped ONE and HRC20 Reverse Token']
i=0
for pair in most_traded:
    times = get_swap_times(pair)
    times = [row for row in times if row < 1000]
    sns.histplot(times, bins=50).set(title=titles[i], xlabel='Transaction time')
    plt.show()
    i = i+1
df_first_minute = df[df["first_buy_speed"] < 60]
df_first_minute[["first_buy_speed"]].hist(bins=60)
plt.show()

df["bins"] = pd.cut(df.poolstart, bins=10, labels=False)
df_binned = df.groupby("bins").mean()
print(df_binned)
# df_binned["first_buy_speed"].plot()
# plt.show()
sns.lineplot('first_buy_speed', 'bins', data=df_binned)
plt.show()
