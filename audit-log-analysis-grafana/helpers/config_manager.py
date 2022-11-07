# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates

import yaml

cfg = None

with open("config.yaml", "r") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

def Get(key):
    nestedKey = key.split('.')
    value = cfg
    for k in nestedKey:
        value = value[k]
    return value