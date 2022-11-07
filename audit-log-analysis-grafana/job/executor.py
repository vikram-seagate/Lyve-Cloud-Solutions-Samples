# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates

import helpers.config_manager as config
from datetime import datetime, timezone, timedelta
from helpers.s3 import connect, download_latest_file
from parsers.console import ParserConsole
from parsers.audit import ParserAudit
from parsers.iam import ParserIAM
from typing import Optional

def run(collectFromDate : Optional[datetime] = None):
    d1 = datetime.now(timezone.utc)
    # Default S3 use UTC timezone.
    # lastHour = datetime.now(timezone.utc) - timedelta(hours=2)
    try:
        lastHour = collectFromDate if collectFromDate else datetime.now(timezone.utc) - timedelta(hours=2)
        print(f'Pulling the Lyve Log from {lastHour}')


        # Connect to S3 Lyve Cloud
        s3conn = connect()
        latestLogFound = download_latest_file(s3conn, config.Get('lyvecloud.log_bucket'), lastHour)

        for log in latestLogFound:
            if hasProcess(log['key']):
                print(f"{log['key']} has been processed")
                continue

            real_key = log['key'].split("/")[1]
            print(real_key)

            if real_key.startswith('Console'):
                log_console_handler(log)
            elif real_key.startswith('S3'):
                log_audit_handler(log)
            elif real_key.startswith('IAM'):
                log_iam_handler(log)

            done(log['key'])
            
        d2 = datetime.now(timezone.utc)
        with open('lastr_run.time','wt') as fp:
            dt_str = d2.strftime('%Y-%m-%d %H:%M:%S')
            fp.write(dt_str)
        d3 = d2-d1
        print(f"END - Time spent: {str(d3)}")
    except Exception as e:
       print('[executor.run] error', e)
       
    return None
            

def log_console_handler(log):
    parser = ParserConsole()
    parser.load(log['body'])
    for datasource in config.Get('datasources'):
        parser.sendTo(datasource)

def log_audit_handler(log):
    parser = ParserAudit()
    parser.load(log['body'])
    for datasource in config.Get('datasources'):
        parser.sendTo(datasource)

def log_iam_handler(log):
    parser = ParserIAM()
    parser.load(log['body'])
    for datasource in config.Get('datasources'):
        parser.sendTo(datasource)

def done(key):
    with open('.tmp', 'a') as f:
        f.write(f'{key}\n')

def hasProcess(key):
    try:
        with open('.tmp', 'r') as f:
            history = f.readlines()

            for h in history:
                if h.rstrip() == key:
                    return True
    except: pass
    return False
