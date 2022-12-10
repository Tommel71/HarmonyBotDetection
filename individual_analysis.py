import requests
# pretty print is used to print the output in the console in an easy to read format
from pprint import pprint
from matplotlib import pyplot as plt
import pandas as pd

endpoint = 'https://sushi.graph.t.hmny.io/subgraphs/name/sushiswap/harmony-exchange'

# function to use requests.post to make an API call to the subgraph url
def run_query(q):

    # endpoint where you are making the request
    request = requests.post(endpoint,
                            '',
                            json={'query': query})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed. return code is {}.      {}'.format(request.status_code, query))


token = '"0xed0b4b0f0e2c17646682fc98ace09feb99af3ade"'
n = 1000

query = """

{
 pairs(first: 1000, where: {token1: """ + token + """, token0: "0xcf664087a5bb0237a0bad6742852ec6c8d69a27a"},orderBy: reserveUSD, orderDirection: desc) {
   id
 }
}
"""
result = run_query(query)
tokenpair = '"' + result["data"]["pairs"][0]["id"] + '"'


query = """
{
    swaps(first:""" + str(n) + """ , where: { pair: """ + tokenpair + """ }, orderBy: timestamp, orderDirection: asc) {
      timestamp
      transaction {
        id
        timestamp
      }
      id
      pair {
        token0 {
          id
          symbol
        }
        token1 {
          id
          symbol
        }
      }
      amount0In
      amount0Out
      amount1In
      amount1Out
      amountUSD
      to
    }
}

"""

result = run_query(query)

# print the results
print('Print Result - {}'.format(result))
print('#############')
# pretty print the results
pprint(result)
import numpy
start = numpy.datetime64(int(result["data"]["swaps"][0]["timestamp"]), "s")
end = numpy.datetime64(int(result["data"]["swaps"][n-1]["timestamp"]), "s")
print(end-start)




sum = 0
df_in = pd.DataFrame()
times_in = []
df_out = pd.DataFrame()
times_out = []
for i in range(n):
    swap = result["data"]["swaps"][i]
    ONE_spent = float(swap["amount0In"])
    print(ONE_spent)
    time = numpy.datetime64(int(swap["timestamp"]), "s")

    price = float(swap["amountUSD"])
    time = numpy.datetime64(int(swap["timestamp"]), "s")
    sum += price
    line = pd.Series(data = {"USD": price, "cumulative": sum, "id": swap["id"]})

    if ONE_spent>0:
        times_in.append(time)
        df_in = df_in.append(line, ignore_index=True)
    else:
        times_out.append(time)
        df_out = df_out.append(line, ignore_index=True)

    print(i, price, time)

df_in["index"] = times_in
df_in.index = times_in
df_out["index"] = times_out
df_out.index = times_out


### FOR IN
plt.hist(x=df_in.index, bins=50) # number of transactions
plt.xticks(rotation=45)
# TODO volume of transactions
# TODO perhaps restrict to unique sender addresses
# TODO get sender address from transaction


#### FOR OUT
plt.hist(x=df_out.index, bins=50) # number of transactions
plt.xticks(rotation=45)
plt.show()


# TODO for a single address get when it dumps


### STALK BOTS

query = """
{
    swaps(first:""" + str(n) + """ , where: { pair: """ + tokenpair + """ }, orderBy: timestamp, orderDirection: asc) {
      timestamp
      transaction {
        id
        timestamp
      }
      id
      pair {
        token0 {
          id
          symbol
        }
        token1 {
          id
          symbol
        }
      }
      amount0In
      amount0Out
      amount1In
      amount1Out
      amountUSD
      to
    }
}

"""

plt.bar(x=df_in.index[:100]) # number of transactions
