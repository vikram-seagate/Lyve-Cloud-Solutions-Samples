# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates

from datetime import datetime, timezone
import hashlib

def makeID(paintext, unique=False):
    if unique:
        paintext = "{}@{}".format(paintext, datetime.now(timezone.utc).strftime('%d-%b-%Y %H:%M:%S:%f'))
    return hashlib.md5(paintext.encode()).hexdigest()

def fatdict(data):
    resp = {}
    def toFatdict(data, keychain=''):
        for key, value in data.items():
            if keychain:
                key = keychain + "." + key

            if isinstance(value, dict):
                toFatdict(value, key)
            else:
                resp[key] = value
                
    toFatdict(data)
    return resp