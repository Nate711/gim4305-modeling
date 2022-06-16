import pickle
from time import time
import moteus
from collections import defaultdict
import pandas as pd

DATA_KEYS = {"torque": moteus.Register.TORQUE,
             "position": moteus.Register.POSITION,
             "velocity": moteus.Register.VELOCITY}


def load_log(filename):
    return pickle.load(open(filename, "rb"))


def log_to_dict(log):
    data = defaultdict(list)

    for datum in log:
        time_elapsed = datum[0]
        data["ts"].append(time_elapsed)
        states = datum[1]
        for id, state in states.items():
            for measurement, moteus_key in DATA_KEYS.items():
                data[f"{measurement}-{id}"].append(state.values[moteus_key])

    return data


def load_log_df(filename):
    log = load_log(filename)
    data_dict = log_to_dict(log)
    return pd.DataFrame(data_dict)

if __name__ == "__main__":
    df = load_log_df("log_06_14_2022_16_03_53.pickle")