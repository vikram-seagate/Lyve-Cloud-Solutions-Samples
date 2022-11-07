# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates

import gzip
import json
from . import NEWLINE
from helpers.utils import fatdict

class LogParser:

    __logs = []

    def load(self, buffer):
        with gzip.open(buffer, 'r') as f:
            content = f.read().decode('UTF-8')
            lines = content.split(NEWLINE)
            for line in lines:
                if line:
                    log = json.loads(line)
                    self.__logs.append(log)
                
    def getLogs(self):
        logs = []
        for l in self.__logs:
            logs.append(fatdict(l))
        return logs
