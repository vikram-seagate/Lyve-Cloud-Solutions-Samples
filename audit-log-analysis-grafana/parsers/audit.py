# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates

from  .logparser import LogParser
from .enums import Action
from datasources import influxdb
import json
from tqdm import tqdm


class ParserAudit(LogParser):
    """ extract a console log from .gz to dict """

    def logs(self):
        return self.getLogs()

    def sendTo(self, datasource):
        if datasource == Action.toInflux.value:
            self.__toInfluxdb()

    def __toInfluxdb(self):
        points = []
        print("[!] - Make points list of audit logs...")
        for log in self.getLogs():
            tag = {
                'auditEntry.api.name': log.get('auditEntry.api.name', ''),
                'auditEntry.api.bucket': log.get('auditEntry.api.bucket', ''),
                'auditEntry.api.statusCode': log.get('auditEntry.api.statusCode', ''),
                'auditEntry.requestHeader.X-Real-Ip': log.get('auditEntry.requestHeader.X-Real-Ip', ''),
                'serviceAccountName': log.get('serviceAccountName', ''),
                'serviceAccountCreatorId': log.get('serviceAccountCreatorId', '')
            }

            timeToResponse = log.get('auditEntry.api.timeToResponse', 0)

            field = {
                'message': json.dumps(log),
                'auditEntry.api.timeToResponse': int(timeToResponse[:-2]) if timeToResponse != 0 else timeToResponse
            }

            time = log.get('auditEntry.time', None)

            point = influxdb.make_point('audit-01', tag, field, time)
            points.append(point)
        try:
            influxdb.BatchWrite(points)
        except Exception as e:
            raise e