# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates

from .logparser import LogParser
from .enums import Action
from datasources import influxdb
import json
from tqdm import tqdm

class ParserIAM(LogParser):
    """ extract a console log from .gz to dict """

    def logs(self):
        return self.getLogs()

    def sendTo(self, datasource):
        if datasource == Action.toInflux.value:
            self.__toInfluxdb()

    def __toInfluxdb(self):
        points = []
        print("[!] - Make points list of IAM logs...")
        for log in self.getLogs():
            tag = {
                'organization': log.get('organization', ''),
                'source': log.get('source', ''),
                'content.client_name': log.get('client_name', ''),
                'content.ip': log.get('ip', ''),
                'content.hostname': log.get('hostname', ''),
                'content.user_name': log.get('user_name', ''),
                'bucket_name': log.get('bucket_name', '')
            }

            field = {
                'message': json.dumps(log),
                'created_date': log.get('created_date', '')
            }

            time = log.get('date', None)

            point = influxdb.make_point('iam-01',tag,field,time)
            points.append(point)
        try:
            influxdb.BatchWrite(points)
        except Exception as e:
            raise e   
