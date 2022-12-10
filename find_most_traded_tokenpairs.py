"""
random analysis, find most traded tokenpairs
"""
import pandas as pd
from tools import load_json

chain = "Harmony"
all_swap_transactions = load_json(f"data/{chain}/all_swap_transactions.json")

tuples = []
for pair in all_swap_transactions.keys():
    if all_swap_transactions[pair] is not None:
        for val in all_swap_transactions[pair]:
            tuples.append((pair, val))

df = pd.DataFrame(tuples, columns=["pair", "txhash"])
counts = df.groupby("pair").count()
max_counts = counts.max()
mask = (counts > 250).values
print(max_counts)
print(counts[mask])