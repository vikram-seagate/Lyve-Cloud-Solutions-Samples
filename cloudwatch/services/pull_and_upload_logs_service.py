import gzip
import json
import time
from datetime import datetime, timedelta


class PullAndUploadLogsService(object):
    def __init__(self, s3, cloudwatch, input_bucket, mode, log_type, log_group, chunk_size=100):
        self.s3 = s3        
        self.mode = mode
        self.log_type = log_type
        self.log_group = log_group
        self.chunk_size = chunk_size
        self.cloudwatch = cloudwatch
        self.input_bucket = input_bucket

        # constants
        self.AUDITLOGS = "_audit_logs"
        self.LYVELASTHOUR = "lyve_lasthour_"
        self.LYVEFROMDATE = "lyve_fromdate_"
        self.INTEGRATIONLOGS = "_integration_logs"

       
    def __call__(self):
        try:
            self.start_time = datetime.utcnow()

            if self.mode == "":
                # check if audit logs stream already exists
                response = self.cloudwatch.describe_log_streams(logGroupName=self.log_group, logStreamNamePrefix=self.LYVELASTHOUR + self.log_type + self.AUDITLOGS)

                # if audit logs stream doesn't exists, create it
                if response['logStreams'] == []:
                    response = self.cloudwatch.create_log_stream(logGroupName=self.log_group, logStreamName=self.LYVELASTHOUR + self.log_type + self.AUDITLOGS)

                # check if integration logs stream already exists
                response = self.cloudwatch.describe_log_streams(logGroupName=self.log_group, logStreamNamePrefix=self.LYVELASTHOUR + self.log_type + self.INTEGRATIONLOGS)

                # if integration logs stream doesn't exists, create it
                if response['logStreams'] == []:
                    response = self.cloudwatch.create_log_stream(logGroupName=self.log_group, logStreamName=self.LYVELASTHOUR + self.log_type + self.INTEGRATIONLOGS)

                # set streams
                self.audit_log_stream = self.LYVELASTHOUR + self.log_type + self.AUDITLOGS
                self.integration_log_stream = self.LYVELASTHOUR + self.log_type + self.INTEGRATIONLOGS

                prefix = self.__get_prefix__()
                # set the minimum date from which logs should be taken
                min_date = datetime.utcnow() - timedelta(hours=1)
            else:
                # reset mode so that the next iteration would take logs from the last hour
                self.__set_mode_lasthour__("/app/config.json") 

                # create new audit log stream
                _ = self.cloudwatch.create_log_stream(logGroupName=self.log_group, logStreamName=self.LYVEFROMDATE + self.log_type + self.AUDITLOGS)

                # create integration log stream
                _ = self.cloudwatch.create_log_stream(logGroupName=self.log_group, logStreamName=self.LYVEFROMDATE + self.log_type + self.INTEGRATIONLOGS)

                prefix = ""
                self.audit_log_stream = self.LYVEFROMDATE + self.log_type + self.AUDITLOGS
                self.integration_log_stream = self.LYVEFROMDATE + self.log_type + self.INTEGRATIONLOGS

                # set the minimum date from which logs should be taken
                if self.mode == "all":
                    min_date = datetime.min
                else:
                    min_date = datetime.strptime(self.mode, "%m/%d/%y")

            all_objects = self.s3.list_objects_v2(Bucket=self.input_bucket, Prefix=prefix)
            if "Contents" not in all_objects:
                self.__log_to_cloudwatch__(f"Bucket {self.input_bucket} is empty")
                return

            objects = all_objects["Contents"]
            while all_objects['IsTruncated']:
                all_objects = self.s3.list_objects_v2(Bucket=self.input_bucket, Prefix=prefix, ContinuationToken=all_objects['NextContinuationToken'])
                objects += all_objects["Contents"]

            return self.__get_audit_logs__(objects, self.log_type, min_date)

        except Exception as e:
            self.__log_to_cloudwatch__(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")


    def __get_audit_logs__(self, objects, suffix, min_time):
        logs = list()
        # iterating over log files(.gz), adding its lines to a dict
        for obj in objects:
            if self.start_time > obj["LastModified"].replace(tzinfo=None) > min_time and suffix in obj["Key"]:
                s3_response_object = self.s3.get_object(Bucket=self.input_bucket, Key=obj["Key"])
                with gzip.open(s3_response_object["Body"], "rt") as gf:
                    lines = gf.readlines()
                    for line in lines:
                        logs += [json.loads(line)] # adds line as a dict item
                        if len(logs) == self.chunk_size:
                            _ = self.__upload_logs__(logs, self.audit_log_stream)
                            logs.clear()

                self.__log_to_cloudwatch__("Finished Uploading: {}".format(obj["Key"]))

        # send leftovers
        if len(logs) > 0:
            _ = self.__upload_logs__(logs, self.audit_log_stream)


    def __get_prefix__(self):
        today = datetime.utcnow() - timedelta(hours=1)
        string_month = today.strftime("%B")
        year = today.year
        return f"{string_month}-{year}/{self.log_type}-"


    def __upload_logs__(self, log_events, log_stream):
        timestamp = int(round(time.time() * 1000))
        logs_response = self.cloudwatch.describe_log_streams(logGroupName=self.log_group, logStreamNamePrefix=log_stream)

        sequence_token = logs_response['logStreams'][0].get("uploadSequenceToken")
        log_events = [{"timestamp": timestamp, "message": str(event)} for event in log_events]
        if sequence_token is None:
            return self.cloudwatch.put_log_events(logEvents=log_events, logGroupName=self.log_group, logStreamName=log_stream)
            
        return self.cloudwatch.put_log_events(logEvents=log_events, logGroupName=self.log_group, logStreamName=log_stream, sequenceToken=sequence_token)


    def __log_to_cloudwatch__(self, message):
        log = list()
        line = {'integration-log': '{}'.format(message)}
        log += [json.loads(json.dumps(line))]
        _ = self.__upload_logs__(log, self.integration_log_stream)


    def __set_mode_lasthour__(self, file):
        jsonFile = open(file, "r")
        data = json.load(jsonFile) 
        jsonFile.close()
        data["lyvecloud"]["mode"] = ""
        jsonFile = open(file, "w+")
        jsonFile.write(json.dumps(data))
        jsonFile.close()