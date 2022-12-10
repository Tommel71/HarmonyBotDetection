import time
import json

def robust_function_call(f):
    while True:
        try:
            return f()
        except Exception as exc:
            print(exc)
            time.sleep(10)

def load_json(path):

    with open(path) as f:
        result = json.load(f)

    return result

def save_json(dictionary, path):

    with open(path, "w") as outfile:
        json.dump(dictionary, outfile, indent=4)
