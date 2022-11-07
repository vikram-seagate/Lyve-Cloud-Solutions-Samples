# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates


from .logparser import LogParser
from .enums import Action
from datasources import influxdb
import json
from tqdm import tqdm

class ParserConsole(LogParser):
    """ extract a console log from .gz to dict """

    def logs(self):
        return self.getLogs()

    def sendTo(self, datasource):
        if datasource == Action.toInflux.value:
            self.__toInfluxdb()

    def __toInfluxdb(self):
        points = []
        print("[!] - Make points list of console logs...")
        for log in self.getLogs():
            tag = {
                'UserIdentity.UserName': log.get('UserIdentity.UserName', ''),
                'UserIdentity.Role': log.get('UserIdentity.Role', ''),
                'UserIdentity.IPAddress': log.get('UserIdentity.IPAddress', ''),
                'ConsoleEvent.Eventname': log.get('ConsoleEvent.Eventname', ''),
            }

            StatusCode = log.get('ConsoleEvent.StatusCode', 0)

            field = {
                'message': json.dumps(log),
                'StatusCode': int(StatusCode) if StatusCode != 0 else StatusCode
            }

            time = log.get('ConsoleEvent.EventTime', None)

            if time:
                time = time.split('UTC')[0]

            point = influxdb.make_point('console-01',tag, field, time)
            points.append(point)
        try:
            influxdb.BatchWrite(points)
        except Exception as e:
            raise e        